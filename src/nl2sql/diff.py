"""Describe how two SQL answers to the same question differ.

These tags are hints for a human reading the cases, not a classification.
They compare the text of the two queries, so they say what changed, not why
one answer is right and the other wrong.
"""

import re

_SPACES = re.compile(r"\s+")
_AROUND_PUNCTUATION = re.compile(r"\s*([(),=<>*])\s*")


def normalise(sql: str) -> str:
    """Lower-case and tidy whitespace, so formatting differences disappear."""
    sql = _SPACES.sub(" ", sql.strip().lower())
    return _AROUND_PUNCTUATION.sub(r"\1", sql)


def _count(pattern: str, sql: str) -> int:
    return len(re.findall(pattern, sql, re.IGNORECASE))


def _has(pattern: str, sql: str) -> bool:
    return _count(pattern, sql) > 0


def tags(
    before: str, after: str, before_error: str | None, after_error: str | None
) -> list[str]:
    """Short labels for what changed between the two queries."""
    found = []
    if normalise(before) == normalise(after):
        found.append("identical SQL (result flipped anyway)")
    if before_error and not after_error:
        found.append("now runs")
    if after_error and not before_error:
        found.append("no longer runs")

    joins = (_count(r"\bjoin\b", before), _count(r"\bjoin\b", after))
    if joins[0] != joins[1]:
        found.append(f"joins {joins[0]}->{joins[1]}")
    selects = (_count(r"\bselect\b", before), _count(r"\bselect\b", after))
    if selects[0] != selects[1]:
        found.append(f"SELECTs {selects[0]}->{selects[1]} (subqueries/set ops)")

    for label, pattern in [
        ("DISTINCT", r"\bdistinct\b"),
        ("ORDER BY", r"\border\s+by\b"),
        ("LIMIT", r"\blimit\b"),
        ("GROUP BY", r"\bgroup\s+by\b"),
        ("HAVING", r"\bhaving\b"),
        ("T1/T2 aliases", r"\bt\d\b"),
    ]:
        was, now = _has(pattern, before), _has(pattern, after)
        if now and not was:
            found.append(f"{label} added")
        elif was and not now:
            found.append(f"{label} removed")
    return found
