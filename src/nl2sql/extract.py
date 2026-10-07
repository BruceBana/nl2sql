"""Pull a single SQL statement out of raw model output.

Models wrap SQL in markdown fences, add a sentence before or after it, or emit
several statements. Execution needs exactly one clean statement, so everything
the model generates passes through extract_sql first.

If nothing that looks like SQL is found, the stripped text is returned as is.
It will then fail to execute and be scored as wrong, which is the honest
outcome. This function never tries to repair a query.
"""

import re

_FENCE = re.compile(r"```[a-zA-Z]*[ \t]*\n?(.*?)(?:```|\Z)", re.DOTALL)
_SQL_START = re.compile(r"\b(?:SELECT|WITH)\b", re.IGNORECASE)
_BLANK_LINE = re.compile(r"\n[ \t]*\n")


def _first_statement(sql: str) -> str:
    """Cut at the first semicolon that is not inside a quoted string."""
    in_quote = None
    for position, char in enumerate(sql):
        if in_quote:
            if char == in_quote:
                in_quote = None
        elif char in "'\"`":
            in_quote = char
        elif char == ";":
            return sql[:position]
    return sql


def extract_sql(raw: str) -> str:
    text = raw.strip()

    fenced = _FENCE.search(text)
    if fenced:
        # Fenced block: trust its contents. An unclosed fence (generation hit
        # the token limit) is treated as running to the end of the text.
        text = fenced.group(1).strip()
        start = _SQL_START.search(text)
        if start:
            text = text[start.start() :]
    else:
        # No fence: drop any prose before the query, and anything after the
        # first blank line that follows it.
        start = _SQL_START.search(text)
        if start:
            text = text[start.start() :]
            text = _BLANK_LINE.split(text, maxsplit=1)[0]

    return _first_statement(text).strip()
