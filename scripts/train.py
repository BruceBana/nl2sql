"""Fine-tune Qwen2.5-Coder-7B-Instruct on Spider with QLoRA.

Run from the project root:

    # 1. memory test: 3 training steps on the longest examples only
    uv run python scripts/train.py --memory-test

    # 2. the real run
    uv run python scripts/train.py --name qlora_r16

    # if a run is interrupted, carry on from its last checkpoint
    uv run python scripts/train.py --name qlora_r16 --resume

The real run saves a LoRA adapter to checkpoints/<name>/checkpoint-<step>/ every
--eval-steps steps, and the final one to checkpoints/<name>/final/. It also
writes checkpoints/<name>/run_config.json with every setting used.
"""

import argparse
import json
import math
import os
import time
from pathlib import Path

from nl2sql.schema import SERIALISERS, load_schemas
from nl2sql.spider import (
    find_spider_root,
    load_examples,
    tables_path,
    validation_databases,
)
from nl2sql.training import (
    build_records,
    prompt_mismatches,
    render_full,
    token_lengths,
)

# All seven linear layers in each transformer block: the attention projections
# (q, k, v, o) and the feed-forward projections (gate, up, down).
LORA_TARGETS = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]
MEMORY_TEST_STEPS = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--name", default="qlora_r16", help="run name")
    parser.add_argument("--format", choices=tuple(SERIALISERS), default="ddl")
    parser.add_argument(
        "--batch-size", type=int, default=2, help="examples on the GPU at once"
    )
    parser.add_argument(
        "--effective-batch-size",
        type=int,
        default=16,
        help="examples per weight update (reached by gradient accumulation)",
    )
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--rank", type=int, default=16, help="LoRA rank; alpha = 2x")
    parser.add_argument("--max-length", type=int, default=2560)
    parser.add_argument(
        "--eval-steps", type=int, default=100, help="validate and save this often"
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--memory-test", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--no-wandb", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.effective_batch_size % args.batch_size:
        raise SystemExit("--effective-batch-size must be a multiple of --batch-size")
    accumulation = args.effective_batch_size // args.batch_size

    # Heavy imports after argument parsing, so --help is instant.
    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from trl import SFTConfig, SFTTrainer

    from nl2sql.generate import MODEL_ID, load_model, load_tokenizer

    # ---- data ----------------------------------------------------------------
    root = find_spider_root()
    schemas = load_schemas(tables_path(root, "train"))
    fit_examples = load_examples(root, "fit")
    val_examples = load_examples(root, "val")
    val_dbs = sorted(validation_databases(load_examples(root, "train")))
    print(f"fit: {len(fit_examples)} questions")
    print(f"val: {len(val_examples)} questions on {len(val_dbs)} held-out databases")
    print(f"     {', '.join(val_dbs)}")

    tokenizer = load_tokenizer()
    fit = build_records(fit_examples, schemas, args.format)
    val = build_records(val_examples, schemas, args.format)

    # Control check: the training text must begin with the exact eval prompt.
    bad = prompt_mismatches(tokenizer, fit + val)
    if bad:
        raise SystemExit(
            f"{len(bad)} records do not start with the evaluation prompt "
            f"(first: {bad[0]}). Training would not match evaluation; stopping."
        )
    print("check passed: every training sequence starts with the eval prompt")
    print("\n===== one full training sequence =====")
    print(render_full(tokenizer, fit[0]))
    print("======================================\n")

    # Never truncate: the end of the sequence is the SQL being learned. Drop
    # anything too long instead, and say how many.
    fit_lengths = token_lengths(tokenizer, fit)
    val_lengths = token_lengths(tokenizer, val)
    print(f"longest training sequence: {max(fit_lengths)} tokens")
    too_long = sum(n > args.max_length for n in fit_lengths + val_lengths)
    if too_long:
        print(f"dropping {too_long} sequences longer than {args.max_length} tokens")
    fit = [r for r, n in zip(fit, fit_lengths, strict=True) if n <= args.max_length]
    val = [r for r, n in zip(val, val_lengths, strict=True) if n <= args.max_length]

    if args.memory_test:
        # Worst case: every batch is made of the longest sequences.
        longest_first = sorted(
            zip(fit, fit_lengths, strict=True), key=lambda pair: -pair[1]
        )
        needed = MEMORY_TEST_STEPS * args.effective_batch_size
        fit = [record for record, _ in longest_first[:needed]]

    # ---- model ---------------------------------------------------------------
    model = load_model()  # the same 4-bit base model used for the baseline
    model.config.use_cache = False  # the cache is for generation, not training

    lora = LoraConfig(
        r=args.rank,
        lora_alpha=2 * args.rank,
        lora_dropout=0.05,
        target_modules=LORA_TARGETS,
        bias="none",
        task_type="CAUSAL_LM",
    )

    # ---- training settings ---------------------------------------------------
    steps_per_epoch = math.ceil(len(fit) / args.effective_batch_size)
    total_steps = math.ceil(steps_per_epoch * args.epochs)
    out_dir = Path("checkpoints") / ("_memory_test" if args.memory_test else args.name)
    use_wandb = not (args.no_wandb or args.memory_test)
    if use_wandb:
        os.environ.setdefault("WANDB_PROJECT", "nl2sql")

    config = SFTConfig(
        output_dir=str(out_dir),
        run_name=args.name,
        seed=args.seed,
        # what is learned from
        completion_only_loss=True,  # loss on the SQL only
        packing=False,  # one example per sequence, never mixed
        max_length=args.max_length,  # nothing reaches this: long ones dropped above
        # how much and how fast
        num_train_epochs=args.epochs,
        max_steps=MEMORY_TEST_STEPS if args.memory_test else -1,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=accumulation,
        learning_rate=args.learning_rate,
        lr_scheduler_type="cosine",
        warmup_steps=max(1, round(0.03 * total_steps)),
        # memory
        bf16=True,
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",
        # monitoring
        logging_steps=10,
        eval_strategy="no" if args.memory_test else "steps",
        eval_steps=args.eval_steps,
        save_strategy="no" if args.memory_test else "steps",
        save_steps=args.eval_steps,
        report_to="wandb" if use_wandb else "none",
    )

    trainer = SFTTrainer(
        model=model,
        args=config,
        train_dataset=Dataset.from_list(fit),
        eval_dataset=Dataset.from_list(val),
        processing_class=tokenizer,
        peft_config=lora,
    )
    trainer.model.print_trainable_parameters()
    print(
        f"{len(fit)} training examples, {args.batch_size} per batch x "
        f"{accumulation} accumulation steps = {args.effective_batch_size} per update"
    )
    print(f"{total_steps} updates planned, warmup {config.warmup_steps}")

    # ---- run -----------------------------------------------------------------
    torch.cuda.reset_peak_memory_stats()
    started = time.monotonic()
    trainer.train(resume_from_checkpoint=True if args.resume else None)
    elapsed = time.monotonic() - started

    if args.memory_test:
        peak = torch.cuda.max_memory_reserved() / 1024**3
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        per_step = elapsed / MEMORY_TEST_STEPS
        full_steps = math.ceil(
            len(fit_examples) / args.effective_batch_size * args.epochs
        )
        print("\n===== memory test =====")
        print(f"batch size {args.batch_size}, longest sequences only")
        print(f"peak GPU memory: {peak:.1f} of {total:.1f} GiB")
        print(f"time per update: {per_step:.0f}s on the longest sequences")
        print(
            f"a full run is {full_steps} updates; at this worst-case speed that "
            f"would be {full_steps * per_step / 3600:.1f} hours (real runs are faster)"
        )
        return

    final = out_dir / "final"
    trainer.save_model(str(final))
    run_config = {
        **vars(args),
        "model": MODEL_ID,
        "lora_alpha": 2 * args.rank,
        "lora_targets": LORA_TARGETS,
        "fit_examples": len(fit),
        "val_examples": len(val),
        "validation_databases": val_dbs,
        "updates": total_steps,
        "training_hours": round(elapsed / 3600, 2),
    }
    with open(out_dir / "run_config.json", "w", encoding="utf-8") as f:
        json.dump(run_config, f, indent=2)
    print(f"\nSaved final adapter to {final} after {elapsed / 3600:.2f} hours")


if __name__ == "__main__":
    main()
