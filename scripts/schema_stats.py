"""Measure prompt length for each schema format across the Spider splits.

Run from the project root:

    uv run python scripts/schema_stats.py

Needs only the tokenizer, not the model, so it uses no GPU and takes seconds.
It prints one fully rendered prompt per format (read these once), then the
token-length distribution per split, then the databases with the longest
prompts. Those numbers are the evidence for the schema cap decision.
"""

import statistics
from collections import Counter

from transformers import AutoTokenizer

from nl2sql.prompt import build_messages, render
from nl2sql.schema import SERIALISERS, load_schemas, serialise
from nl2sql.spider import find_spider_root, load_examples, tables_path

MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct"
SPLITS = ("train", "dev", "test")


def percentile(sorted_values: list[int], fraction: float) -> int:
    return sorted_values[
        min(len(sorted_values) - 1, int(fraction * len(sorted_values)))
    ]


def prompt_lengths(tokenizer, schemas, examples, fmt) -> list[tuple[int, str]]:
    """Token count of the full rendered prompt for every example."""
    schema_text = {db_id: serialise(s, fmt) for db_id, s in schemas.items()}
    prompts = [
        render(
            tokenizer,
            build_messages(schema_text[ex["db_id"]], ex["question"], fmt),
        )
        for ex in examples
    ]
    encoded = tokenizer(prompts, add_special_tokens=False)["input_ids"]
    return [(len(ids), ex["db_id"]) for ids, ex in zip(encoded, examples)]


def main() -> None:
    root = find_spider_root()
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    print(f"Spider folder: {root}\n")

    medians: dict[tuple[str, str], float] = {}
    shown_example = False
    for split in SPLITS:
        try:
            examples = load_examples(root, split)
            schemas = load_schemas(tables_path(root, split))
        except FileNotFoundError as error:
            print(f"[{split}] skipped, file missing: {error.filename}\n")
            continue

        if not shown_example:
            first = examples[0]
            for fmt in SERIALISERS:
                text = serialise(schemas[first["db_id"]], fmt)
                messages = build_messages(text, first["question"], fmt)
                print(f"===== rendered prompt, format = {fmt} =====")
                print(render(tokenizer, messages))
                print()
            shown_example = True

        n_dbs = len({ex["db_id"] for ex in examples})
        print(f"===== {split}: {len(examples)} examples, {n_dbs} databases =====")
        print(f"{'format':<9}{'median':>8}{'p95':>8}{'p99':>8}{'max':>8}")
        for fmt in SERIALISERS:
            lengths = prompt_lengths(tokenizer, schemas, examples, fmt)
            counts = sorted(n for n, _ in lengths)
            medians[split, fmt] = statistics.median(counts)
            print(
                f"{fmt:<9}{medians[split, fmt]:>8.0f}{percentile(counts, 0.95):>8}"
                f"{percentile(counts, 0.99):>8}{counts[-1]:>8}"
            )

            longest: dict[str, int] = {}
            for n, db_id in lengths:
                longest[db_id] = max(n, longest.get(db_id, 0))
            per_db = Counter(db_id for _, db_id in lengths)
            top = sorted(longest.items(), key=lambda item: -item[1])[:5]
            for db_id, n in top:
                print(f"    {n:>6} tokens  {db_id} ({per_db[db_id]} examples)")
        saving = 1 - medians[split, "compact"] / medians[split, "ddl"]
        print(f"compact is {saving:.0%} shorter than ddl at the median\n")


if __name__ == "__main__":
    main()
