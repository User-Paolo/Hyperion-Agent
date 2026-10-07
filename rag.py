import json
import logging
import math
import re
from pathlib import Path

import httpx
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

log = logging.getLogger("hyperion")

INDEX = Path(__file__).parent / "knowledge" / "index.json"

# Retrieval limits
TOP_K = 4
MIN_SCORE = 0.45
SHORT_QUESTION_WORDS = 6
KEYWORD_WEIGHT = 0.1
CITE_MARGIN = 0.08

RAG_RULES = """Answer the user's question using the sources below. They come from the HYPER-AI
project documents and the HyperAI IDE documentation. Base the answer on them and do not invent
details that are not in them. If they do not answer the question, say that the HYPER-AI
documents do not cover it, and only add a short general answer if the question is about cloud,
edge, IoT or deployment. Keep the answer short and do not list the sources yourself."""


class Retriever:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        data = json.loads(INDEX.read_text())
        self.model = data["model"]
        self.chunks = data["chunks"]
        self.vectors = [normalize(chunk["vector"]) for chunk in self.chunks]

        # Rare words weigh more
        self.words = [terms(f"{chunk['label']} {chunk['text']}") for chunk in self.chunks]
        total = len(self.words)
        counts: dict[str, int] = {}
        for words in self.words:
            for word in words:
                counts[word] = counts.get(word, 0) + 1
        self.idf = {word: math.log(1 + total / count) for word, count in counts.items()}

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "input": [f"search_query: {text}"]},
            )
        response.raise_for_status()
        return normalize(response.json()["data"][0]["embedding"])

    async def search(self, query: str, k: int = TOP_K) -> list[tuple[float, dict]]:
        vector = await self.embed(query)
        wanted = terms(query)
        scored = []
        for other, chunk, words in zip(self.vectors, self.chunks, self.words, strict=True):
            similarity = sum(a * b for a, b in zip(vector, other, strict=True))
            scored.append((similarity + KEYWORD_WEIGHT * self.overlap(wanted, words), similarity, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [(score, chunk) for score, similarity, chunk in scored[:k] if similarity >= MIN_SCORE]

    def overlap(self, wanted: set[str], words: set[str]) -> float:
        total = sum(self.idf.get(word, 0.0) for word in wanted)
        if not total:
            return 0.0
        return sum(self.idf.get(word, 0.0) for word in wanted & words) / total


STOP_WORDS = {
    "the", "and", "for", "are", "what", "which", "how", "does", "can", "with", "that", "this",
    "from", "into", "why", "did", "about", "use", "used", "uses", "its", "has", "have", "you",
    "your", "show", "tell", "me", "hyper", "hyperai", "do", "is", "of", "to", "in", "a", "an",
}


def terms(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 1 and w not in STOP_WORDS}


def normalize(vector: list[float]) -> list[float]:
    length = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / length for value in vector]


def search_query(text: str, history: list[BaseMessage]) -> str:
    # Short follow-ups need the previous question
    if len(text.split()) < SHORT_QUESTION_WORDS:
        previous = [m.content for m in history if m.type == "human"]
        if previous:
            return f"{previous[-1]} {text}"
    return text


def document_title(chunk: dict) -> str:
    return chunk["label"].split(" > ")[0]


def build_messages(
    system_prompt: str, history: list[BaseMessage], text: str, hits: list[tuple[float, dict]]
) -> list[BaseMessage]:
    if hits:
        sources = "\n\n".join(
            f"[{n}] {chunk['label']}\n{chunk['text']}" for n, (_, chunk) in enumerate(hits, 1)
        )
        system = f"{system_prompt}\n\n{RAG_RULES}\n\nSources:\n\n{sources}"
    else:
        system = f"{system_prompt}\n\nNo HYPER-AI document matched this question. Say so briefly."
    return [SystemMessage(system), *history, HumanMessage(text)]


def sources_line(hits: list[tuple[float, dict]]) -> str:
    # Cite only the closest matches
    best = hits[0][0] if hits else 0.0
    titles = list(dict.fromkeys(document_title(c) for score, c in hits if score >= best - CITE_MARGIN))
    return "\n\nSources: " + "; ".join(titles) if titles else ""
