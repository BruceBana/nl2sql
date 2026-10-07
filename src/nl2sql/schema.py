"""Load Spider schemas and serialise them into prompt text.

Two formats are implemented behind one interface so they can be compared on
equal terms:

  ddl      CREATE TABLE statements with column types, primary and foreign keys
  compact  one line per table, no types, foreign keys listed at the end

Adding a third format later means writing one function and registering it in
SERIALISERS. Nothing else in the project needs to change.
"""

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

_PLAIN_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


@dataclass(frozen=True)
class Column:
    name: str
    type: str


@dataclass(frozen=True)
class Table:
    name: str
    columns: tuple[Column, ...]
    primary_key: tuple[str, ...]


@dataclass(frozen=True)
class ForeignKey:
    table: str
    column: str
    ref_table: str
    ref_column: str


@dataclass(frozen=True)
class Schema:
    db_id: str
    tables: tuple[Table, ...]
    foreign_keys: tuple[ForeignKey, ...]


def _parse(entry: dict) -> Schema:
    """Turn one tables.json entry into a Schema.

    tables.json stores columns as one flat list of [table_index, column_name].
    Index 0 is a placeholder [-1, "*"]. Primary and foreign keys refer to
    positions in that flat list, so they are resolved back to names here.
    """
    table_names = entry["table_names_original"]
    flat_columns = entry["column_names_original"]
    types = entry["column_types"]

    # Composite primary keys appear as nested lists in some versions of the file.
    pk_indices: set[int] = set()
    for item in entry["primary_keys"]:
        pk_indices.update(item if isinstance(item, list) else [item])

    columns: list[list[Column]] = [[] for _ in table_names]
    primary: list[list[str]] = [[] for _ in table_names]
    for index, (table_index, name) in enumerate(flat_columns):
        if table_index < 0:
            continue
        columns[table_index].append(Column(name, types[index]))
        if index in pk_indices:
            primary[table_index].append(name)

    def locate(column_index: int) -> tuple[str, str]:
        table_index, name = flat_columns[column_index]
        return table_names[table_index], name

    foreign_keys = tuple(
        ForeignKey(*locate(source), *locate(target))
        for source, target in entry["foreign_keys"]
    )
    tables = tuple(
        Table(name, tuple(columns[i]), tuple(primary[i]))
        for i, name in enumerate(table_names)
    )
    return Schema(entry["db_id"], tables, foreign_keys)


def load_schemas(tables_json: str | Path) -> dict[str, Schema]:
    """Read a Spider tables file and return {db_id: Schema}."""
    with open(tables_json, encoding="utf-8") as f:
        return {entry["db_id"]: _parse(entry) for entry in json.load(f)}


def quote(identifier: str) -> str:
    """Double-quote names SQLite would not accept bare, such as "Home Town"."""
    if _PLAIN_IDENTIFIER.fullmatch(identifier):
        return identifier
    return '"' + identifier.replace('"', '""') + '"'


def to_ddl(schema: Schema) -> str:
    """CREATE TABLE statements: types, primary keys and foreign keys inline."""
    statements = []
    for table in schema.tables:
        single_pk = table.primary_key[0] if len(table.primary_key) == 1 else None
        lines = []
        for column in table.columns:
            line = f"  {quote(column.name)} {column.type}"
            if column.name == single_pk:
                line += " PRIMARY KEY"
            lines.append(line)
        if len(table.primary_key) > 1:
            names = ", ".join(quote(name) for name in table.primary_key)
            lines.append(f"  PRIMARY KEY ({names})")
        for fk in schema.foreign_keys:
            if fk.table == table.name:
                lines.append(
                    f"  FOREIGN KEY ({quote(fk.column)}) REFERENCES "
                    f"{quote(fk.ref_table)}({quote(fk.ref_column)})"
                )
        body = ",\n".join(lines)
        statements.append(f"CREATE TABLE {quote(table.name)} (\n{body}\n);")
    return "\n\n".join(statements)


def to_compact(schema: Schema) -> str:
    """One line per table, no types. Primary keys starred, foreign keys last."""
    lines = []
    for table in schema.tables:
        names = ", ".join(
            quote(c.name) + ("*" if c.name in table.primary_key else "")
            for c in table.columns
        )
        lines.append(f"{quote(table.name)}({names})")
    if schema.foreign_keys:
        lines.append("Foreign keys:")
        lines.extend(
            f"{quote(fk.table)}.{quote(fk.column)} = "
            f"{quote(fk.ref_table)}.{quote(fk.ref_column)}"
            for fk in schema.foreign_keys
        )
    return "\n".join(lines)


SERIALISERS: dict[str, Callable[[Schema], str]] = {
    "ddl": to_ddl,
    "compact": to_compact,
}


def serialise(schema: Schema, fmt: str) -> str:
    """Serialise a schema in the named format ('ddl' or 'compact')."""
    return SERIALISERS[fmt](schema)
