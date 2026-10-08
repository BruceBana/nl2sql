"""Load the model and generate text for a list of prompts.

Everything that touches the GPU lives in this file. Nothing here knows about
SQL or Spider: prompts go in as strings and raw replies come out as strings.
"""

import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"


def load_tokenizer(model_id: str = MODEL_ID):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    # Prompts in a batch have different lengths, so shorter ones are padded.
    # Padding must go on the left: the model continues from the last token, and
    # that has to be the end of the prompt, not padding.
    tokenizer.padding_side = "left"
    return tokenizer


def load_model(model_id: str = MODEL_ID):
    """Load the model in 4-bit NF4, the same quantisation used for training."""
    quantisation = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_id, quantization_config=quantisation, device_map={"": 0}
    )
    model.eval()
    return model


@torch.inference_mode()
def generate(
    model,
    tokenizer,
    prompts: list[str],
    batch_size: int = 8,
    max_new_tokens: int = 256,
) -> list[str]:
    """Greedy-decode a reply for every prompt. Output order matches input order.

    Greedy decoding always picks the most likely next token, so the same prompt
    gives the same reply every time. The sampling settings and repetition
    penalty that ship with the model are switched off explicitly, which keeps
    the evaluation deterministic and free of extra knobs.
    """
    # Longest prompts first: similar lengths share a batch (less padding), and
    # if the batch size is too big for the GPU it fails on the first batch.
    order = sorted(range(len(prompts)), key=lambda i: -len(prompts[i]))
    replies = [""] * len(prompts)

    for start in tqdm(range(0, len(order), batch_size), desc="generating"):
        indices = order[start : start + batch_size]
        batch = tokenizer(
            [prompts[i] for i in indices],
            return_tensors="pt",
            padding=True,
            add_special_tokens=False,
        ).to(model.device)
        output = model.generate(
            **batch,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=None,
            top_p=None,
            top_k=None,
            repetition_penalty=1.0,
            pad_token_id=tokenizer.pad_token_id,
        )
        # generate() returns prompt + reply. Keep only the reply.
        new_tokens = output[:, batch["input_ids"].shape[1] :]
        texts = tokenizer.batch_decode(new_tokens, skip_special_tokens=True)
        for i, text in zip(indices, texts, strict=True):
            replies[i] = text
    return replies
