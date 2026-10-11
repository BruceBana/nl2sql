"""Write out every question where two runs disagree, for error analysis.

    uv run python scripts/diff_runs.py results/dev_zero_shot.jsonl \
        results/dev_qlora_r16_final.jsonl --out results/dev_diff.md

The output has two sections:

  fixed   wrong in the first run, right in the second
  broken  right in the first run, wrong in the second

Within each section the cases are shuffled with a fixed seed, so the first ten
are a fair random sample rather than ten questions on the same database.
Each case shows the question, the gold SQL, both answers and some automatic
tags, with a blank "Category:" line for you to fill in.

A summary table at the top counts how often each tag appears in each section.
A tag that is common among the fixed cases and rare among the broken ones
points to something fine-tuning changed for the better, and vice versa.
"""

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from nl2sql.diff import tags


def load(path: str) -> dict[int, dict]:
    with open(path, encoding="utf-8") as f:
        return {r["index"]: r for r in map(json.loads, f) if r["gold_error"] is None}


def case_block(n: int, a: dict, b: dict, case_tags: list[str], names) -> str:
    def answer(record: dict) -> str:
        error = (
            f"\n\n*Did not run:* `{record['pred_error']}`"
            if record["pred_error"]
            else ""
        )
        return f"```sql\n{record['pred_sql']}\n```{error}"

    return (
        f"### {n}. `{a['db_id']}` (question #{a['index']})\n\n"
        f"**Question:** {a['question']}\n\n"
        f"**Gold:**\n```sql\n{a['gold_sql']}\n```\n\n"
        f"**{names[0]}:**\n{answer(a)}\n\n"
        f"**{names[1]}:**\n{answer(b)}\n\n"
        f"**Auto tags:** {', '.join(case_tags) or 'none'}\n\n"
        f"**Category:** \n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("before")
    parser.add_argument("after")
    parser.add_argument("--out", required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    a, b = load(args.before), load(args.after)
    names = (Path(args.before).stem, Path(args.after).stem)
    shared = sorted(a.keys() & b.keys())
    groups = {
        "fixed": [i for i in shared if not a[i]["correct"] and b[i]["correct"]],
        "broken": [i for i in shared if a[i]["correct"] and not b[i]["correct"]],
    }
    rng = random.Random(args.seed)
    for indices in groups.values():
        rng.shuffle(indices)

    all_tags = {
        i: tags(
            a[i]["pred_sql"], b[i]["pred_sql"], a[i]["pred_error"], b[i]["pred_error"]
        )
        for indices in groups.values()
        for i in indices
    }
    counts = {
        name: Counter(t for i in idx for t in all_tags[i])
        for name, idx in groups.items()
    }

    lines = [
        f"# Where the runs disagree: {names[0]} vs {names[1]}",
        "",
        (
            f"{len(shared)} questions compared. Fixed: {len(groups['fixed'])}. "
            f"Broken: {len(groups['broken'])}."
        ),
        "",
        (
            "Cases in each section are in random order (seed "
            f"{args.seed}), so the first ten are a fair sample."
        ),
        "",
        "## Auto tag counts",
        "",
        "| Tag | Fixed | Broken |",
        "|---|---|---|",
    ]
    every_tag = sorted(
        set(counts["fixed"]) | set(counts["broken"]),
        key=lambda t: -(counts["fixed"][t] + counts["broken"][t]),
    )
    lines += [
        f"| {t} | {counts['fixed'][t]} | {counts['broken'][t]} |" for t in every_tag
    ]

    for name, indices in groups.items():
        heading = {
            "fixed": f"Fixed: wrong in {names[0]}, right in {names[1]}",
            "broken": f"Broken: right in {names[0]}, wrong in {names[1]}",
        }[name]
        lines += ["", f"## {heading}", ""]
        lines += [
            case_block(n, a[i], b[i], all_tags[i], names)
            for n, i in enumerate(indices, start=1)
        ]

    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"fixed: {len(groups['fixed'])}, broken: {len(groups['broken'])}")
    print("\ntag                                     fixed  broken")
    for t in every_tag:
        print(f"{t:<40}{counts['fixed'][t]:>5}{counts['broken'][t]:>8}")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
