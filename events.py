import json


def _event(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def text(chunk: str) -> str:
    return _event({"response": chunk})


def action(name: str, **payload) -> str:
    return _event({"action": name, **payload})


def done() -> str:
    return "data: [DONE]\n\n"
