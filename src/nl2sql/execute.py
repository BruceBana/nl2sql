"""Run one SQL query against a SQLite database, safely.

Model-written SQL is untrusted, so three guards apply:

  read-only   the database is opened read-only, so a stray DROP or DELETE
              cannot damage the Spider data
  timeout     a query that runs too long (usually an accidental cross join)
              is interrupted
  row cap     a query that returns a huge result is stopped before it fills
              memory

A failed query is not an exception here. It comes back as an ExecutionResult
with an error message, because "the model wrote SQL that does not run" is a
normal outcome that gets scored as wrong.
"""

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

TIMEOUT_SECONDS = 30.0
MAX_ROWS = 1_000_000


@dataclass(frozen=True)
class ExecutionResult:
    rows: list[tuple] | None  # None when the query failed
    error: str | None  # None when the query ran

    @property
    def ok(self) -> bool:
        return self.error is None


def execute(
    db_path: str | Path,
    sql: str,
    timeout: float = TIMEOUT_SECONDS,
    max_rows: int = MAX_ROWS,
) -> ExecutionResult:
    path = Path(db_path).resolve()
    if not path.exists():
        # A missing database is a setup problem, not a wrong answer. Fail loudly
        # instead of quietly scoring every query against it as an error.
        raise FileNotFoundError(f"Database not found: {path}")
    if not sql.strip():
        return ExecutionResult(None, "empty query")

    connection = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)
    # A few Spider databases contain bytes that are not valid UTF-8.
    connection.text_factory = lambda raw: raw.decode("utf-8", errors="replace")
    # SQLite calls this every 10,000 steps. Returning True interrupts the query.
    deadline = time.monotonic() + timeout
    connection.set_progress_handler(lambda: time.monotonic() > deadline, 10_000)
    try:
        rows = connection.execute(sql).fetchmany(max_rows + 1)
    except (sqlite3.Error, sqlite3.Warning, ValueError) as error:
        if time.monotonic() > deadline:
            return ExecutionResult(None, f"timeout after {timeout:g}s")
        return ExecutionResult(None, f"{type(error).__name__}: {error}")
    finally:
        connection.close()

    if len(rows) > max_rows:
        return ExecutionResult(None, f"more than {max_rows} rows returned")
    return ExecutionResult(rows, None)
