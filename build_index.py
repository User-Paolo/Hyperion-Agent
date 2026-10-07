import json
import os
import re
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://legion1.di.uoa.gr/v1"
EMBED_MODEL = "nomic-embed-text"
KNOWLEDGE = Path(__file__).parent / "knowledge"
INDEX = KNOWLEDGE / "index.json"

# Chunking limits
MAX_CHARS = 1200
MIN_CHARS = 60
BATCH = 16


def sections(text: str, ide_doc: bool) -> list[tuple[str, str, str]]:
    title, heading, lines, found = "", "", [], []
    for line in text.splitlines():
        match = re.match(r"^(#{1,4})\s+(.*)", line)
        if match and not in_code(lines):
            if lines:
                found.append((title, heading, "\n".join(lines).strip()))
            lines = []
            if len(match.group(1)) == 1:
                title, heading = match.group(2).strip(), ""
                if ide_doc:
                    title = f"HyperAI IDE docs: {title}"
            else:
                heading = match.group(2).strip()
        else:
            lines.append(line)
    if lines:
        found.append((title, heading, "\n".join(lines).strip()))
    return [s for s in found if s[2]]


def in_code(lines: list[str]) -> bool:
    return sum(line.startswith("```") for line in lines) % 2 == 1


def paragraphs(body: str) -> list[str]:
    parts, current = [], []
    for block in re.split(r"\n\s*\n", body):
        current.append(block)
        # Keep code blocks whole
        if not in_code(current):
            parts.append("\n\n".join(current).strip())
            current = []
    if current:
        parts.append("\n\n".join(current).strip())
    return [p for p in parts if p and p != "---"]


def chunks(path: Path) -> list[dict]:
    result = []
    ide_doc = path.parent.name == "ide"
    for title, heading, body in sections(path.read_text(), ide_doc):
        label = f"{title} > {heading}" if heading else title
        current = ""
        for para in paragraphs(body):
            if current and len(current) + len(para) > MAX_CHARS:
                result.append({"label": label, "text": current})
                current = ""
            current = f"{current}\n\n{para}".strip()
        if current:
            result.append({"label": label, "text": current})
    source = path.relative_to(KNOWLEDGE).as_posix()
    return [{"source": source, **chunk} for chunk in result if len(chunk["text"]) >= MIN_CHARS]


def embed(texts: list[str], api_key: str) -> list[list[float]]:
    response = httpx.post(
        f"{BASE_URL}/embeddings",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": EMBED_MODEL, "input": texts},
        timeout=120,
    )
    response.raise_for_status()
    data = sorted(response.json()["data"], key=lambda item: item["index"])
    return [item["embedding"] for item in data]


def main() -> None:
    api_key = os.environ.get("API_KEY", "")
    if not api_key:
        sys.exit("API_KEY is not set")

    items = [chunk for path in sorted(KNOWLEDGE.rglob("*.md")) for chunk in chunks(path)]
    for start in range(0, len(items), BATCH):
        batch = items[start : start + BATCH]
        vectors = embed([f"search_document: {item['label']}\n\n{item['text']}" for item in batch], api_key)
        for item, vector in zip(batch, vectors, strict=True):
            item["vector"] = [round(value, 6) for value in vector]

    INDEX.write_text(json.dumps({"model": EMBED_MODEL, "chunks": items}))
    print(f"Indexed {len(items)} chunks from {len({i['source'] for i in items})} files into {INDEX}")


if __name__ == "__main__":
    main()
