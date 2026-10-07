"""Build the chat messages sent to the model.

The same function builds zero-shot prompts, training examples and fine-tuned
inference prompts. That is deliberate: if the baseline and the fine-tuned model
saw different prompts, the before/after comparison would not be valid.
"""

SYSTEM_PROMPT = (
    "You are an expert in SQLite. Given a database schema and a question, "
    "write one SQLite query that answers the question. "
    "Return only the SQL query, with no explanation."
)

# The compact format stars primary keys, so the prompt has to say so.
FORMAT_NOTES = {
    "ddl": "",
    "compact": "Columns marked * are primary keys.\n",
}


def build_user_message(schema_text: str, question: str, fmt: str = "ddl") -> str:
    return (
        f"Database schema:\n{FORMAT_NOTES[fmt]}{schema_text}\n\n"
        f"Question: {question.strip()}"
    )


def build_messages(
    schema_text: str, question: str, fmt: str = "ddl", sql: str | None = None
) -> list[dict[str, str]]:
    """Chat messages for one example.

    Leave sql as None for inference. Pass the gold query to get a full training
    example with the assistant turn filled in.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_message(schema_text, question, fmt)},
    ]
    if sql is not None:
        messages.append({"role": "assistant", "content": sql.strip()})
    return messages


def render(tokenizer, messages: list[dict[str, str]]) -> str:
    """Turn messages into the exact string the model sees.

    Always goes through the tokenizer's own chat template rather than a
    hand-written one. For inference the template appends the opening of the
    assistant turn so the model starts writing SQL straight away.
    """
    is_inference = messages[-1]["role"] != "assistant"
    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=is_inference
    )
