"""Locate the Spider dataset on disk and load its example files.

Splits used in this project:

  train  the full Spider training set (train_spider.json + train_others.json)
  fit    train minus the validation databases: what the model is trained on
  val    every question on a few held-out training databases, used to choose
         between training checkpoints
  dev    the official dev set: used only for the before/after numbers
  test   the official test set
"""

import json
import random
from collections import Counter
from pathlib import Path

# Which example files and which schema file belong to each split.
SPLIT_FILES = {
    "train": ("train_spider.json", "train_others.json"),
    "dev": ("dev.json",),
    "test": ("test.json",),
}
DATABASE_DIRS = {
    "train": "database",
    "fit": "database",
    "val": "database",
    "dev": "database",
    "test": "test_database",
}
TABLES_FILES = {
    "train": "tables.json",
    "fit": "tables.json",
    "val": "tables.json",
    "dev": "tables.json",
    "test": "test_tables.json",
}

VALIDATION_SEED = 0
VALIDATION_MIN_QUESTIONS = 350
VALIDATION_MAX_PER_DATABASE = 100


def find_spider_root(data_dir: str | Path = "data") -> Path:
    """Return the folder that holds tables.json and dev.json.

    Searching for it means the code does not care whether the zip unpacked to
    data/spider or data/spider_data.
    """
    for tables in sorted(Path(data_dir).rglob("tables.json")):
        if "__MACOSX" in tables.parts:
            continue
        if (tables.parent / "dev.json").exists():
            return tables.parent
    raise FileNotFoundError(
        f"No Spider folder (tables.json next to dev.json) found under {data_dir}/"
    )


def validation_databases(train_examples: list[dict]) -> set[str]:
    """Pick whole training databases to hold out for validation.

    Holding out databases rather than random questions mirrors dev, where every
    question is on a database the model never saw in training. Databases with
    more than 100 questions are not eligible, so one large database cannot take
    over the validation set. A fixed seed means the choice never changes.
    """
    counts = Counter(example["db_id"] for example in train_examples)
    eligible = sorted(
        db_id for db_id, n in counts.items() if n <= VALIDATION_MAX_PER_DATABASE
    )
    random.Random(VALIDATION_SEED).shuffle(eligible)
    chosen: set[str] = set()
    total = 0
    for db_id in eligible:
        if total >= VALIDATION_MIN_QUESTIONS:
            break
        chosen.add(db_id)
        total += counts[db_id]
    return chosen


def load_examples(root: Path, split: str) -> list[dict]:
    """Load every example for a split. Each has 'db_id', 'question', 'query'."""
    if split in ("fit", "val"):
        train = load_examples(root, "train")
        held_out = validation_databases(train)
        want_held_out = split == "val"
        return [ex for ex in train if (ex["db_id"] in held_out) == want_held_out]

    examples = []
    for name in SPLIT_FILES[split]:
        with open(root / name, encoding="utf-8") as f:
            examples.extend(json.load(f))
    return examples


def tables_path(root: Path, split: str) -> Path:
    """Path to the schema file that covers the given split."""
    return root / TABLES_FILES[split]


def db_path(root: Path, split: str, db_id: str) -> Path:
    """Path to the SQLite file for one database."""
    return root / DATABASE_DIRS[split] / db_id / f"{db_id}.sqlite"
