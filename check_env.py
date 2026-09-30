"""Phase 0 smoke test for the NL-to-SQL project.

Checks, in order:
  1. PyTorch sees the RTX 5080 and has Blackwell (sm_120) kernels
  2. Spider is unzipped and a gold query executes against its SQLite DB
  3. bitsandbytes + transformers can load Qwen2.5-Coder-7B-Instruct in 4-bit NF4
     and generate one SQL completion on the GPU

Run from the project root:  uv run python check_env.py
"""

import json
import sqlite3
import time
from pathlib import Path

import torch

MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"
DATA_ROOT = Path("data")


def check_torch():
    print("\n[1/3] PyTorch + GPU")
    print(f"  torch {torch.__version__} | built for CUDA {torch.version.cuda}")
    assert torch.cuda.is_available(), (
        "CUDA not available. Check the Windows NVIDIA driver, and that you are "
        "running inside WSL (nvidia-smi should work there)."
    )
    print(
        f"  GPU: {torch.cuda.get_device_name(0)} | capability {torch.cuda.get_device_capability(0)}"
    )
    archs = torch.cuda.get_arch_list()
    print(f"  Compiled archs: {archs}")
    if not any("120" in a for a in archs):
        print("  WARNING: no sm_120 in this build. Expect 'no kernel image' errors.")
    a = torch.randn(4096, 4096, device="cuda", dtype=torch.bfloat16)
    (a @ a).sum().item()
    torch.cuda.synchronize()
    print("  bf16 matmul on GPU: OK")


def check_spider():
    print("\n[2/3] Spider data")
    dev_files = sorted(DATA_ROOT.rglob("dev.json"))
    assert dev_files, (
        f"No dev.json under {DATA_ROOT.resolve()}. Unzip Spider into data/ first."
    )
    dev_json = dev_files[0]
    spider_dir = dev_json.parent
    db_dir = spider_dir / "database"
    n_dbs = len(list(db_dir.glob("*/*.sqlite")))
    examples = json.loads(dev_json.read_text())
    print(f"  Spider dir: {spider_dir}")
    print(f"  dev examples: {len(examples)} | DBs in database/: {n_dbs}")

    ex = examples[0]
    db_path = db_dir / ex["db_id"] / f"{ex['db_id']}.sqlite"
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(ex["query"]).fetchall()
    print(f"  Q: {ex['question']}")
    print(f"  Gold SQL: {ex['query']}")
    print(f"  Result ({len(rows)} rows): {rows[:5]}")
    print("  Gold query executes against its DB: OK")


def check_model():
    print("\n[3/3] Qwen2.5-Coder-7B in 4-bit")
    import bitsandbytes as bnb
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    print(f"  transformers {transformers.__version__} | bitsandbytes {bnb.__version__}")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, quantization_config=bnb_config, device_map="cuda:0"
    )
    print(
        f"  Loaded in {time.time() - t0:.0f}s on {model.device} | "
        f"VRAM allocated {torch.cuda.memory_allocated() / 1e9:.1f} GB"
    )

    messages = [
        {
            "role": "system",
            "content": "You are a SQL expert. Reply with one SQLite query and nothing else.",
        },
        {
            "role": "user",
            "content": (
                "CREATE TABLE singer (singer_id INT, name TEXT, country TEXT, age INT);\n\n"
                "Question: How many singers are from France?"
            ),
        },
    ]
    prompt = tok.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    print("  ---- rendered prompt (read this once) ----")
    print(prompt)
    print("  ------------------------------------------")

    inputs = tok(prompt, return_tensors="pt").to(model.device)
    t0 = time.time()
    out = model.generate(**inputs, max_new_tokens=64, do_sample=False)
    new_tokens = out[0, inputs["input_ids"].shape[1] :]
    elapsed = time.time() - t0
    print(
        f"  Generated {len(new_tokens)} tokens in {elapsed:.1f}s ({len(new_tokens) / elapsed:.1f} tok/s)"
    )
    print(f"  Model output: {tok.decode(new_tokens, skip_special_tokens=True).strip()}")
    print(f"  Peak VRAM: {torch.cuda.max_memory_allocated() / 1e9:.1f} GB")


if __name__ == "__main__":
    check_torch()
    check_spider()
    check_model()
    print("\nPhase 0 complete.")
