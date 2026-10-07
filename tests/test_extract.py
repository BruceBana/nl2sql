import pytest

from nl2sql.extract import extract_sql

Q = "SELECT count(*) FROM singer"

CASES = [
    # (description, raw model output, expected SQL)
    ("plain", Q, Q),
    ("trailing semicolon", Q + ";", Q),
    ("sql fence", f"```sql\n{Q}\n```", Q),
    ("bare fence", f"```\n{Q};\n```", Q),
    ("prose before fence", f"Here is the query:\n\n```sql\n{Q}\n```", Q),
    ("prose after fence", f"```sql\n{Q}\n```\nThis counts the singers.", Q),
    ("unclosed fence", f"```sql\n{Q}", Q),
    ("prose before, no fence", f"The answer is:\n{Q}", Q),
    ("prose after, no fence", f"{Q}\n\nThis counts all singers.", Q),
    ("two statements", f"{Q}; SELECT 1;", Q),
    (
        "semicolon inside a string",
        "SELECT name FROM t WHERE note = 'a;b';",
        "SELECT name FROM t WHERE note = 'a;b'",
    ),
    (
        "multi-line query kept whole",
        "```sql\nSELECT name\nFROM singer\nWHERE age > 20\n```",
        "SELECT name\nFROM singer\nWHERE age > 20",
    ),
    (
        "CTE",
        "```sql\nWITH x AS (SELECT 1) SELECT * FROM x;\n```",
        "WITH x AS (SELECT 1) SELECT * FROM x",
    ),
    ("lower case", "select count(*) from singer", "select count(*) from singer"),
    ("no SQL at all", "I cannot answer that.", "I cannot answer that."),
    ("empty", "", ""),
]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(raw, expected) for _, raw, expected in CASES],
    ids=[description for description, _, _ in CASES],
)
def test_extract_sql(raw, expected):
    assert extract_sql(raw) == expected
