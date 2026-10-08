"""Execution accuracy: does the predicted SQL return the same result as gold?

A prediction is correct when running it gives the same rows as running the
gold query on the same database. The comparison rules are:

  row order     ignored, unless the gold query has an ORDER BY
  duplicates    counted, so two identical rows are not the same as one
  column order  ignored, so SELECT name, age matches SELECT age, name
  floats        rounded to 6 decimal places before comparing

Known limits of this metric (state these in the README):

  * It uses one database per question. A wrong query can still return the
    right rows by coincidence, most often when both results are empty. The
    official Spider test-suite metric reduces this by using several databases.
  * ORDER BY is detected anywhere in the gold query, including subqueries.
  * Rows that tie on the ORDER BY column can legitimately come back in a
    different order and be marked wrong.
"""

import re
from collections import Counter
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from itertools import islice
from pathlib import Path

from nl2sql.execute import execute

_ORDER_BY = re.compile(r"\border\s+by\b", re.IGNORECASE)
_MAX_COLUMN_ORDERINGS = 10_000


def order_matters(gold_sql: str) -> bool:
    return bool(_ORDER_BY.search(gold_sql))


def _normalise(rows: list[tuple]) -> list[tuple]:
    return [
        tuple(round(v, 6) if isinstance(v, float) else v for v in row) for row in rows
    ]


def _column_orderings(candidates: list[list[int]]) -> Iterator[tuple[int, ...]]:
    """Every way to pair each gold column with a different predicted column.

    candidates[i] lists the predicted columns that could be gold column i.
    """

    def extend(chosen: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
        if len(chosen) == len(candidates):
            yield chosen
            return
        for column in candidates[len(chosen)]:
            if column not in chosen:
                yield from extend((*chosen, column))

    return extend(())


def results_match(gold: list[tuple], pred: list[tuple], ordered: bool) -> bool:
    """Compare two result sets under the rules in the module docstring."""
    if len(gold) != len(pred):
        return False
    if not gold:
        return True
    if len(gold[0]) != len(pred[0]):
        return False

    gold, pred = _normalise(gold), _normalise(pred)
    gold_columns = list(zip(*gold, strict=True))
    pred_columns = list(zip(*pred, strict=True))

    # A predicted column can only stand in for a gold column if it holds the
    # same values: in the same order when ordered, as a multiset otherwise.
    def summary(column: tuple) -> object:
        return column if ordered else Counter(column)

    gold_summaries = [summary(c) for c in gold_columns]
    pred_summaries = [summary(c) for c in pred_columns]
    candidates = [
        [j for j, p in enumerate(pred_summaries) if p == g] for g in gold_summaries
    ]
    if any(not options for options in candidates):
        return False

    gold_rows = gold if ordered else Counter(gold)
    for ordering in islice(_column_orderings(candidates), _MAX_COLUMN_ORDERINGS):
        reordered = [tuple(row[j] for j in ordering) for row in pred]
        if (reordered if ordered else Counter(reordered)) == gold_rows:
            return True
    return False


@dataclass(frozen=True)
class Score:
    correct: bool
    pred_error: str | None
    gold_error: str | None


def score_example(db_path: str | Path, gold_sql: str, pred_sql: str) -> Score:
    """Run gold and predicted SQL on one database and compare the results."""
    gold = execute(db_path, gold_sql)
    if not gold.ok:
        # The dataset's own query failed, so this example cannot be judged.
        return Score(False, None, gold.error)
    pred = execute(db_path, pred_sql)
    if not pred.ok:
        return Score(False, pred.error, None)
    correct = results_match(gold.rows, pred.rows, order_matters(gold_sql))
    return Score(correct, None, None)


def summarise(scores: list[Score]) -> dict:
    """Headline numbers for a run.

    Examples whose gold query fails are left out of the accuracy, and counted
    separately so the exclusion is visible.
    """
    gold_errors = sum(s.gold_error is not None for s in scores)
    scored = len(scores) - gold_errors
    correct = sum(s.correct for s in scores)
    return {
        "examples": len(scores),
        "gold_errors_excluded": gold_errors,
        "scored": scored,
        "correct": correct,
        "execution_accuracy": round(correct / scored, 4) if scored else None,
        "pred_did_not_run": sum(s.pred_error is not None for s in scores),
    }


def score_to_dict(score: Score) -> dict:
    return asdict(score)
