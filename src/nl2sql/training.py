"""Turn Spider examples into training records, and check them.

Each record is in TRL's conversational "prompt-completion" format:

    {"prompt":     [system message, user message],
     "completion": [assistant message holding the gold SQL]}

With this format the trainer computes the loss on the completion only, so the
model is trained to write the SQL, not to reproduce the schema and question.

The messages come from the same build_messages() used at evaluation, so the
model is trained on exactly the prompt it will later be tested with.
"""

from nl2sql.prompt import build_messages, render
from nl2sql.schema import Schema, serialise


def build_records(
    examples: list[dict], schemas: dict[str, Schema], fmt: str
) -> list[dict]:
    schema_text: dict[str, str] = {}
    records = []
    for example in examples:
        db_id = example["db_id"]
        if db_id not in schema_text:
            schema_text[db_id] = serialise(schemas[db_id], fmt)
        messages = build_messages(
            schema_text[db_id], example["question"], fmt, sql=example["query"]
        )
        records.append({"prompt": messages[:-1], "completion": messages[-1:]})
    return records


def render_full(tokenizer, record: dict) -> str:
    """The whole training sequence as text: prompt followed by the answer."""
    return render(tokenizer, record["prompt"] + record["completion"])


def prompt_mismatches(tokenizer, records: list[dict]) -> list[int]:
    """Indices of records whose training text does not start with the eval prompt.

    At evaluation the model sees render(prompt). In training it sees the full
    sequence. If the first is not an exact prefix of the second, the model is
    trained on a slightly different prompt from the one it is tested on, and
    the before/after comparison is no longer like for like.
    """
    return [
        i
        for i, record in enumerate(records)
        if not render_full(tokenizer, record).startswith(
            render(tokenizer, record["prompt"])
        )
    ]


def token_lengths(tokenizer, records: list[dict]) -> list[int]:
    """Number of tokens in each full training sequence."""
    texts = [render_full(tokenizer, record) for record in records]
    encoded = tokenizer(texts, add_special_tokens=False)["input_ids"]
    return [len(ids) for ids in encoded]
