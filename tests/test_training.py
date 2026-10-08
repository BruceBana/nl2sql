from nl2sql.prompt import build_messages
from nl2sql.schema import _parse, serialise
from nl2sql.training import build_records, prompt_mismatches

ENTRY = {
    "db_id": "toy",
    "table_names_original": ["singer"],
    "column_names_original": [[-1, "*"], [0, "id"], [0, "name"]],
    "column_types": ["text", "number", "text"],
    "primary_keys": [1],
    "foreign_keys": [],
}
SCHEMAS = {"toy": _parse(ENTRY)}
EXAMPLES = [
    {
        "db_id": "toy",
        "question": "How many singers?",
        "query": "SELECT count(*) FROM singer",
    }
]


class ChatMLTokenizer:
    """Stand-in that renders chat messages the way Qwen's template does."""

    def __init__(self, extra_on_generation: str = ""):
        self.extra = extra_on_generation

    def apply_chat_template(
        self, messages, tokenize=False, add_generation_prompt=False
    ):
        text = "".join(
            f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in messages
        )
        if add_generation_prompt:
            text += "<|im_start|>assistant\n" + self.extra
        return text


def test_record_matches_eval_prompt():
    (record,) = build_records(EXAMPLES, SCHEMAS, "ddl")
    schema_text = serialise(SCHEMAS["toy"], "ddl")
    assert record["prompt"] == build_messages(schema_text, "How many singers?", "ddl")
    assert record["completion"] == [
        {"role": "assistant", "content": "SELECT count(*) FROM singer"}
    ]


def test_prefix_check_passes_for_consistent_template():
    records = build_records(EXAMPLES, SCHEMAS, "ddl")
    assert prompt_mismatches(ChatMLTokenizer(), records) == []


def test_prefix_check_catches_a_mismatch():
    # A template that adds something to the eval prompt that training never sees.
    records = build_records(EXAMPLES, SCHEMAS, "ddl")
    assert prompt_mismatches(ChatMLTokenizer("<think>\n"), records) == [0]
