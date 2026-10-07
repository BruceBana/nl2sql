import sqlite3

import pytest

from nl2sql.prompt import build_messages
from nl2sql.schema import _parse, quote, serialise

# A cut-down entry in the same shape as Spider's tables.json.
ENTRY = {
    "db_id": "toy",
    "table_names_original": ["singer", "concert", "singer_in_concert"],
    "column_names_original": [
        [-1, "*"],
        [0, "Singer_ID"],
        [0, "Name"],
        [0, "Home Town"],
        [1, "concert_ID"],
        [1, "Year"],
        [2, "concert_ID"],
        [2, "Singer_ID"],
    ],
    "column_types": [
        "text",
        "number",
        "text",
        "text",
        "number",
        "text",
        "number",
        "number",
    ],
    "primary_keys": [1, 4, [6, 7]],
    "foreign_keys": [[6, 4], [7, 1]],
}


@pytest.fixture
def schema():
    return _parse(ENTRY)


def test_parse_resolves_keys_to_names(schema):
    singer, _concert, link = schema.tables
    assert [c.name for c in singer.columns] == ["Singer_ID", "Name", "Home Town"]
    assert singer.primary_key == ("Singer_ID",)
    assert link.primary_key == ("concert_ID", "Singer_ID")
    first = schema.foreign_keys[0]
    assert (first.table, first.column) == ("singer_in_concert", "concert_ID")
    assert (first.ref_table, first.ref_column) == ("concert", "concert_ID")


def test_quote_only_when_needed():
    assert quote("Name") == "Name"
    assert quote("Home Town") == '"Home Town"'


def test_ddl_is_valid_sqlite(schema):
    """The strongest check available: SQLite itself accepts the DDL."""
    ddl = serialise(schema, "ddl")
    connection = sqlite3.connect(":memory:")
    connection.executescript(ddl)
    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()
    assert {name for (name,) in tables} == {"singer", "concert", "singer_in_concert"}


def test_compact_format(schema):
    assert serialise(schema, "compact") == (
        'singer(Singer_ID*, Name, "Home Town")\n'
        "concert(concert_ID*, Year)\n"
        "singer_in_concert(concert_ID*, Singer_ID*)\n"
        "Foreign keys:\n"
        "singer_in_concert.concert_ID = concert.concert_ID\n"
        "singer_in_concert.Singer_ID = singer.Singer_ID"
    )


def test_compact_is_shorter_than_ddl(schema):
    assert len(serialise(schema, "compact")) < len(serialise(schema, "ddl"))


def test_messages_for_inference_and_training(schema):
    text = serialise(schema, "ddl")
    inference = build_messages(text, "How many singers? ")
    assert [m["role"] for m in inference] == ["system", "user"]
    assert inference[1]["content"].endswith("Question: How many singers?")

    training = build_messages(text, "How many singers?", sql=" SELECT 1 ")
    assert training[-1] == {"role": "assistant", "content": "SELECT 1"}
    # Identical up to the assistant turn, so train and inference prompts match.
    assert training[:2] == build_messages(text, "How many singers?")
