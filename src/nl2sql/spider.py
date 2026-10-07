"""Locate the Spider dataset on disk and load its example files."""

import json
from pathlib import Path

# Which example files and which schema file belong to each split.
SPLIT_FILES = {
    "train": ("train_spider.json", "train_others.json"),
    "dev": ("dev.json",),
    "test": ("test.json",),
}
TABLES_FILES = {
    "train": "tables.json",
    "dev": "tables.json",
    "test": "test_tables.json",
}


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


def load_examples(root: Path, split: str) -> list[dict]:
    """Load every example for a split. Each has 'db_id', 'question', 'query'."""
    examples = []
    for name in SPLIT_FILES[split]:
        with open(root / name, encoding="utf-8") as f:
            examples.extend(json.load(f))
    return examples


def tables_path(root: Path, split: str) -> Path:
    """Path to the schema file that covers the given split."""
    return root / TABLES_FILES[split]
