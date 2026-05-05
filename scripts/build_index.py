from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

CHUNKS_PATH = PROJECT_ROOT / "data" / "chunks.json"
INDEX_PATH = PROJECT_ROOT / "vector_store" / "index.faiss"
METADATA_PATH = PROJECT_ROOT / "vector_store" / "metadata.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_chunks(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing chunk file at {path}. Run scripts/ingest_docs.py first.")
    with path.open("r", encoding="utf-8") as f:
        chunks = json.load(f)
    if not isinstance(chunks, list) or not chunks:
        raise ValueError("Chunk file is empty. Run ingestion first.")
    return chunks


def build_faiss_index(chunks: List[Dict[str, Any]]) -> None:
    texts = [item["text"] for item in chunks]
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype="float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))
    METADATA_PATH.write_text(json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved FAISS index to {INDEX_PATH}")
    print(f"Saved metadata to {METADATA_PATH}")


def main() -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    chunks = load_chunks(CHUNKS_PATH)
    build_faiss_index(chunks)


if __name__ == "__main__":
    main()
