import sqlite3

import pytest

from nl2sql.evaluate import order_matters, results_match, score_example, summarise

GOLD = [("Ann", 30), ("Bob", 25), ("Cy", 30)]

CASES = [
    # (description, gold, pred, ordered, expected)
    ("identical", GOLD, GOLD, False, True),
    ("rows shuffled, order ignored", GOLD, GOLD[::-1], False, True),
    ("rows shuffled, order enforced", GOLD, GOLD[::-1], True, False),
    ("columns swapped", GOLD, [(a, n) for n, a in GOLD], False, True),
    ("columns swapped, ordered", GOLD, [(a, n) for n, a in GOLD], True, True),
    ("wrong value", GOLD, [("Ann", 30), ("Bob", 26), ("Cy", 30)], False, False),
    ("missing row", GOLD, GOLD[:2], False, False),
    ("extra column", GOLD, [(n, a, 1) for n, a in GOLD], False, False),
    ("duplicates counted", [(1,), (1,)], [(1,)], False, False),
    ("duplicates equal", [(1,), (1,), (2,)], [(2,), (1,), (1,)], False, True),
    ("both empty", [], [], False, True),
    ("float noise", [(0.1 + 0.2,)], [(0.3,)], False, True),
    ("int equals float", [(2,)], [(2.0,)], False, True),
    ("null values", [(None, 1)], [(None, 1)], False, True),
    # Same values per column but paired differently across rows: must not match.
    ("columns right, rows mispaired", [(1, 2), (2, 1)], [(1, 1), (2, 2)], False, False),
    ("two identical columns", [(1, 1), (2, 2)], [(1, 1), (2, 2)], False, True),
]


@pytest.mark.parametrize(
    ("gold", "pred", "ordered", "expected"),
    [case[1:] for case in CASES],
    ids=[case[0] for case in CASES],
)
def test_results_match(gold, pred, ordered, expected):
    assert results_match(gold, pred, ordered) is expected


def test_order_matters():
    assert order_matters("SELECT name FROM singer ORDER BY age")
    assert order_matters("select name from singer order  by age desc limit 1")
    assert not order_matters("SELECT name FROM singer WHERE note = 'reorder'")


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "toy.sqlite"
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE singer (id INTEGER, name TEXT, age INTEGER);
        INSERT INTO singer VALUES (1, 'Ann', 30), (2, 'Bob', 25), (3, 'Cy', 30);
        """
    )
    connection.commit()
    connection.close()
    return path


def test_score_example(db):
    gold = "SELECT count(*) FROM singer WHERE age > 26"

    same_meaning = score_example(
        db, gold, "SELECT COUNT(id) FROM singer WHERE age >= 27"
    )
    assert same_meaning.correct

    wrong = score_example(db, gold, "SELECT count(*) FROM singer")
    assert not wrong.correct
    assert wrong.pred_error is None

    broken = score_example(db, gold, "SELECT count(* FROM singer")
    assert not broken.correct
    assert broken.pred_error is not None

    bad_gold = score_example(db, "SELECT nope FROM singer", gold)
    assert bad_gold.gold_error is not None


def test_summarise_excludes_gold_errors(db):
    gold = "SELECT count(*) FROM singer"
    scores = [
        score_example(db, gold, gold),
        score_example(db, gold, "SELECT 1"),
        score_example(db, gold, "not sql"),
        score_example(db, "SELECT nope FROM singer", gold),
    ]
    summary = summarise(scores)
    assert summary["examples"] == 4
    assert summary["gold_errors_excluded"] == 1
    assert summary["scored"] == 3
    assert summary["correct"] == 1
    assert summary["execution_accuracy"] == round(1 / 3, 4)
    assert summary["pred_did_not_run"] == 1
