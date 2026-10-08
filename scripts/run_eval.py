"""Generate SQL for a set of Spider questions and score it.

Run from the project root. Examples:

    # quick check that everything works (16 questions)
    uv run python scripts/run_eval.py --split train --limit 16

    # the full dev set
    uv run python scripts/run_eval.py --split dev --format ddl

Each run writes two files to results/:

    <name>.jsonl         one line per question: the raw reply, the extracted
                         SQL, and whether it was correct
    <name>.summary.json  the headline numbers and the settings used
"""

import argparse
import json
import random
import time
from pathlib import Path

from nl2sql.evaluate import score_example, score_to_dict, summarise
from nl2sql.extract import extract_sql
from nl2sql.prompt import build_messages, render
from nl2sql.schema import SERIALISERS, load_schemas, serialise
from nl2sql.spider import db_path, find_spider_root, load_examples, tables_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--split", choices=("train", "dev", "test"), default="dev")
    parser.add_argument("--format", choices=tuple(SERIALISERS), default="ddl")
    parser.add_argument(
        "--limit", type=int, help="score a random sample of this many questions"
    )
    parser.add_argument("--seed", type=int, default=0, help="seed for --limit")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--name", help="output file name (default: built from args)")
    return parser.parse_args()


def choose_indices(total: int, limit: int | None, seed: int) -> list[int]:
    """Which examples to run. The same seed always picks the same sample."""
    if limit is None or limit >= total:
        return list(range(total))
    return sorted(random.Random(seed).sample(range(total), limit))


def main() -> None:
    args = parse_args()
    # Imported here so that --help works without loading PyTorch.
    from nl2sql.generate import MODEL_ID, generate, load_model, load_tokenizer

    root = find_spider_root()
    examples = load_examples(root, args.split)
    schemas = load_schemas(tables_path(root, args.split))
    indices = choose_indices(len(examples), args.limit, args.seed)
    print(f"{args.split}: running {len(indices)} of {len(examples)} questions")

    tokenizer = load_tokenizer()
    schema_text = {db: serialise(s, args.format) for db, s in schemas.items()}
    prompts = [
        render(
            tokenizer,
            build_messages(
                schema_text[examples[i]["db_id"]],
                examples[i]["question"],
                args.format,
            ),
        )
        for i in indices
    ]

    model = load_model()
    started = time.monotonic()
    replies = generate(model, tokenizer, prompts, args.batch_size, args.max_new_tokens)
    generation_seconds = time.monotonic() - started

    records, scores = [], []
    for i, reply in zip(indices, replies, strict=True):
        example = examples[i]
        pred_sql = extract_sql(reply)
        score = score_example(
            db_path(root, args.split, example["db_id"]), example["query"], pred_sql
        )
        scores.append(score)
        records.append(
            {
                "index": i,
                "split": args.split,
                "db_id": example["db_id"],
                "question": example["question"],
                "gold_sql": example["query"],
                "raw_reply": reply,
                "pred_sql": pred_sql,
                **score_to_dict(score),
            }
        )

    summary = {
        **summarise(scores),
        "model": MODEL_ID,
        "split": args.split,
        "format": args.format,
        "limit": args.limit,
        "seed": args.seed,
        "batch_size": args.batch_size,
        "max_new_tokens": args.max_new_tokens,
        "generation_seconds": round(generation_seconds, 1),
    }

    name = args.name or f"{args.split}_{args.format}_{len(indices)}"
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / f"{name}.jsonl", "w", encoding="utf-8") as f:
        f.writelines(
            json.dumps(record, ensure_ascii=False) + "\n" for record in records
        )
    with open(out_dir / f"{name}.summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"\nSaved results/{name}.jsonl and results/{name}.summary.json")


if __name__ == "__main__":
    main()
