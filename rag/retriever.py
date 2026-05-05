from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class FaissRetriever:
    def __init__(
        self,
        index_path: str = "vector_store/index.faiss",
        metadata_path: str = "vector_store/metadata.json",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        self.model = SentenceTransformer(model_name)

        if not self.index_path.exists():
            raise FileNotFoundError(f"Missing FAISS index at: {self.index_path}")
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"Missing metadata file at: {self.metadata_path}")

        self.index = faiss.read_index(str(self.index_path))
        with self.metadata_path.open("r", encoding="utf-8") as f:
            self.metadata: List[Dict[str, Any]] = json.load(f)

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        query_vector = self.model.encode([query], normalize_embeddings=True)
        query_vector = np.array(query_vector, dtype="float32")

        scores, indices = self.index.search(query_vector, top_k)
        results: List[Dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            item = dict(self.metadata[idx])
            item["score"] = float(score)
            results.append(item)
        return results
