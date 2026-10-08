import sqlite3

import pytest

from nl2sql.execute import execute


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


def test_runs_a_query(db):
    result = execute(db, "SELECT name FROM singer WHERE age = 30")
    assert result.ok
    assert sorted(result.rows) == [("Ann",), ("Cy",)]


def test_bad_sql_is_an_error_not_an_exception(db):
    result = execute(db, "SELEC name FROM singer")
    assert not result.ok
    assert result.rows is None


def test_prose_is_an_error(db):
    assert not execute(db, "I cannot answer that.").ok


def test_empty_query_is_an_error(db):
    assert execute(db, "  ").error == "empty query"


def test_database_is_read_only(db):
    assert not execute(db, "DELETE FROM singer").ok
    assert len(execute(db, "SELECT * FROM singer").rows) == 3


def test_runaway_query_times_out(db):
    endless = (
        "WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n) "
        "SELECT count(*) FROM n"
    )
    result = execute(db, endless, timeout=0.2)
    assert result.error.startswith("timeout")


def test_row_cap(db):
    assert "rows returned" in execute(db, "SELECT * FROM singer", max_rows=2).error


def test_missing_database_fails_loudly(tmp_path):
    with pytest.raises(FileNotFoundError):
        execute(tmp_path / "nope.sqlite", "SELECT 1")
