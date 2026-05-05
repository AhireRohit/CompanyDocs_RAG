from __future__ import annotations

from typing import List


def split_into_word_chunks(text: str, chunk_size: int = 500, overlap: int = 80) -> List[str]:
    """Split text into chunks by word count with overlap."""
    words = text.split()
    if not words:
        return []

    chunks: List[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end == len(words):
            break
        start = max(0, end - overlap)
    return chunks
