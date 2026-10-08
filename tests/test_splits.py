import json

from nl2sql.spider import (
    VALIDATION_MAX_PER_DATABASE,
    VALIDATION_MIN_QUESTIONS,
    load_examples,
    validation_databases,
)


def fake_train(sizes: dict[str, int]) -> list[dict]:
    return [
        {"db_id": db_id, "question": f"q{i}", "query": "SELECT 1"}
        for db_id, n in sizes.items()
        for i in range(n)
    ]


SIZES = {f"db{i}": 30 + (i * 7) % 60 for i in range(40)} | {"huge": 600}


def test_validation_is_deterministic():
    train = fake_train(SIZES)
    assert validation_databases(train) == validation_databases(train)


def test_validation_size_and_eligibility():
    train = fake_train(SIZES)
    chosen = validation_databases(train)
    assert "huge" not in chosen
    assert all(SIZES[db] <= VALIDATION_MAX_PER_DATABASE for db in chosen)
    total = sum(SIZES[db] for db in chosen)
    # Enough to tell checkpoints apart, without taking much training data.
    assert VALIDATION_MIN_QUESTIONS <= total < VALIDATION_MIN_QUESTIONS + 100


def test_fit_and_val_partition_train(tmp_path):
    train = fake_train(SIZES)
    (tmp_path / "train_spider.json").write_text(json.dumps(train[:1000]))
    (tmp_path / "train_others.json").write_text(json.dumps(train[1000:]))

    fit = load_examples(tmp_path, "fit")
    val = load_examples(tmp_path, "val")
    fit_dbs = {ex["db_id"] for ex in fit}
    val_dbs = {ex["db_id"] for ex in val}

    assert len(fit) + len(val) == len(train)
    assert not fit_dbs & val_dbs  # no database appears in both
