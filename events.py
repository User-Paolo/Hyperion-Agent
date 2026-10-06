import json


def encode(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def text(chunk: str) -> str:
    return encode({"response": chunk})


def done() -> str:
    return "data: [DONE]\n\n"
