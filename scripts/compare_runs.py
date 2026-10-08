"""Compare two runs over the same questions, question by question.

    uv run python scripts/compare_runs.py results/A.jsonl results/B.jsonl

Because both runs answered the same questions, the informative cases are the
ones where they disagree: A right and B wrong, or the reverse. Questions both
got right or both got wrong say nothing about which is better.
"""

import json
import math
import sys
from pathlib import Path


def load(path: str) -> dict[int, dict]:
    with open(path, encoding="utf-8") as f:
        records = [json.loads(line) for line in f]
    # Leave out examples whose gold query failed, as the accuracy figure does.
    return {r["index"]: r for r in records if r["gold_error"] is None}


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    path_a, path_b = sys.argv[1], sys.argv[2]
    a, b = load(path_a), load(path_b)
    shared = sorted(a.keys() & b.keys())
    if not shared:
        sys.exit("The two files have no questions in common.")
    if len(shared) < max(len(a), len(b)):
        print(f"Note: comparing only the {len(shared)} questions in both files.")

    both = sum(a[i]["correct"] and b[i]["correct"] for i in shared)
    only_a = sum(a[i]["correct"] and not b[i]["correct"] for i in shared)
    only_b = sum(b[i]["correct"] and not a[i]["correct"] for i in shared)
    neither = len(shared) - both - only_a - only_b

    n = len(shared)
    print(f"A = {Path(path_a).name}")
    print(f"B = {Path(path_b).name}")
    print(f"questions compared: {n}")
    print(f"A accuracy: {(both + only_a) / n:.1%}")
    print(f"B accuracy: {(both + only_b) / n:.1%}")
    print(f"both right:   {both}")
    print(f"only A right: {only_a}")
    print(f"only B right: {only_b}")
    print(f"both wrong:   {neither}")

    # Rough check: if A and B were equally good, the disagreements would split
    # about evenly, and a gap this big would be unusual (about 1 time in 20).
    gap, noise = abs(only_a - only_b), 2 * math.sqrt(only_a + only_b)
    verdict = "larger than" if gap > noise else "within"
    print(f"\ngap of {gap} is {verdict} the noise level of about {noise:.1f}")


if __name__ == "__main__":
    main()
