from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from rag.retriever import FaissRetriever

EVAL_PATH = PROJECT_ROOT / "evaluation" / "eval_questions.json"
CHUNKS_PATH = PROJECT_ROOT / "data" / "chunks.json"
RESULTS_PATH = PROJECT_ROOT / "evaluation" / "results.json"


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9]+", text.lower()))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def keyword_search(query: str, chunks: List[Dict[str, Any]], top_k: int = 4) -> List[Dict[str, Any]]:
    query_tokens = _tokenize(query)
    scored: List[Tuple[int, Dict[str, Any]]] = []
    for chunk in chunks:
        text_tokens = _tokenize(chunk.get("text", ""))
        score = len(query_tokens.intersection(text_tokens))
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]


def main() -> None:
    questions = load_json(EVAL_PATH)
    chunks = load_json(CHUNKS_PATH)
    retriever = FaissRetriever(
        index_path=str(PROJECT_ROOT / "vector_store" / "index.faiss"),
        metadata_path=str(PROJECT_ROOT / "vector_store" / "metadata.json"),
    )

    supported = [q for q in questions if q.get("supported", True) and q.get("expected_source")]

    keyword_hits = 0
    faiss_hits = 0
    keyword_times: List[float] = []
    faiss_times: List[float] = []

    for q in supported:
        expected = q["expected_source"]
        question = q["question"]

        t0 = time.perf_counter()
        key_results = keyword_search(question, chunks, top_k=4)
        keyword_times.append(time.perf_counter() - t0)
        if expected in [x.get("url", "") for x in key_results]:
            keyword_hits += 1

        t1 = time.perf_counter()
        faiss_results = retriever.search(question, top_k=4)
        faiss_times.append(time.perf_counter() - t1)
        if expected in [x.get("url", "") for x in faiss_results]:
            faiss_hits += 1

    keyword_top4 = keyword_hits / len(supported) if supported else 0.0
    faiss_top4 = faiss_hits / len(supported) if supported else 0.0
    improvement = (faiss_top4 - keyword_top4) * 100

    comparison_metrics = {
        "keyword_top_4_accuracy": round(keyword_top4, 4),
        "faiss_top_4_accuracy": round(faiss_top4, 4),
        "retrieval_improvement_points": round(improvement, 2),
        "keyword_average_retrieval_time_seconds": round(sum(keyword_times) / len(keyword_times), 4)
        if keyword_times
        else 0.0,
        "faiss_average_retrieval_time_seconds": round(sum(faiss_times) / len(faiss_times), 4) if faiss_times else 0.0,
    }

    existing = {}
    if RESULTS_PATH.exists():
        existing = load_json(RESULTS_PATH)

    merged = {**existing, **comparison_metrics}
    RESULTS_PATH.write_text(json.dumps(merged, indent=2), encoding="utf-8")

    print(json.dumps(comparison_metrics, indent=2))
    print(f"Updated results in {RESULTS_PATH}")


if __name__ == "__main__":
    main()
