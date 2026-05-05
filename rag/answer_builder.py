from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


FALLBACK_MESSAGE = "I could not find this in the indexed documentation."


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9]+", text.lower()))


def _best_supporting_sentences(question: str, chunks: List[Dict[str, Any]], max_sentences: int = 4) -> List[str]:
    question_tokens = _tokenize(question)
    scored_sentences: List[Tuple[int, str]] = []

    for chunk in chunks:
        text = chunk.get("text", "")
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 35:
                continue
            sentence_tokens = _tokenize(sentence)
            overlap = len(question_tokens.intersection(sentence_tokens))
            if overlap > 0:
                scored_sentences.append((overlap, sentence))

    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    selected = [sentence for _, sentence in scored_sentences[:max_sentences]]
    return selected


def build_grounded_answer(question: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not retrieved_chunks:
        return {"answer": FALLBACK_MESSAGE, "sources": [], "supported": False}

    best_score = retrieved_chunks[0].get("score", 0.0)
    if best_score < 0.28:
        return {"answer": FALLBACK_MESSAGE, "sources": [], "supported": False}

    supporting_sentences = _best_supporting_sentences(question, retrieved_chunks)
    if not supporting_sentences:
        return {"answer": FALLBACK_MESSAGE, "sources": [], "supported": False}

    answer = " ".join(supporting_sentences)
    sources = []
    seen = set()
    for item in retrieved_chunks:
        url = item.get("url", "")
        if url and url not in seen:
            seen.add(url)
            sources.append(url)

    return {
        "answer": answer.strip(),
        "sources": sources,
        "supported": True,
        "confidence": round(float(best_score), 3),
    }
