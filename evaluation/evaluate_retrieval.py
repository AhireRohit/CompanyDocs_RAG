from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from rag.answer_builder import build_grounded_answer
from rag.retriever import FaissRetriever

EVAL_PATH = PROJECT_ROOT / "evaluation" / "eval_questions.json"
RESULTS_PATH = PROJECT_ROOT / "evaluation" / "results.json"


def load_eval_questions() -> List[Dict[str, Any]]:
    with EVAL_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def evaluate() -> Dict[str, Any]:
    retriever = FaissRetriever(
        index_path=str(PROJECT_ROOT / "vector_store" / "index.faiss"),
        metadata_path=str(PROJECT_ROOT / "vector_store" / "metadata.json"),
    )
    questions = load_eval_questions()

    top1_hits = 0
    top4_hits = 0
    total_supported = 0
    citation_hits = 0
    unsupported_total = 0
    unsupported_correct = 0
    times: List[float] = []

    for item in questions:
        question = item["question"]
        expected = item.get("expected_source", "")
        supported = bool(item.get("supported", True))

        start = time.perf_counter()
        retrieved = retriever.search(question, top_k=4)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

        top_sources = [x.get("url", "") for x in retrieved]
        top1_source = top_sources[0] if top_sources else ""

        if supported and expected:
            total_supported += 1
            if top1_source == expected:
                top1_hits += 1
            if expected in top_sources:
                top4_hits += 1

            answer_data = build_grounded_answer(question, retrieved)
            if answer_data.get("supported"):
                cited_sources = answer_data.get("sources", [])
                if expected in cited_sources:
                    citation_hits += 1
        else:
            unsupported_total += 1
            answer_data = build_grounded_answer(question, retrieved)
            if not answer_data.get("supported", False):
                unsupported_correct += 1

    avg_time = sum(times) / len(times) if times else 0.0
    citation_coverage = citation_hits / total_supported if total_supported else 0.0
    unsupported_rejection_acc = unsupported_correct / unsupported_total if unsupported_total else 0.0

    return {
        "total_questions": len(questions),
        "faiss_top_1_accuracy": round(top1_hits / total_supported, 4) if total_supported else 0.0,
        "faiss_top_4_accuracy": round(top4_hits / total_supported, 4) if total_supported else 0.0,
        "average_retrieval_time_seconds": round(avg_time, 4),
        "citation_coverage": round(citation_coverage, 4),
        "unsupported_query_rejection_accuracy": round(unsupported_rejection_acc, 4),
    }


def main() -> None:
    metrics = evaluate()
    RESULTS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Saved evaluation metrics to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
