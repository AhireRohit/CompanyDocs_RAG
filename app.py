from __future__ import annotations

from pathlib import Path
from typing import List

import gradio as gr

from rag.answer_builder import build_grounded_answer
from rag.retriever import FaissRetriever

PROJECT_ROOT = Path(__file__).resolve().parent
INDEX_PATH = PROJECT_ROOT / "vector_store" / "index.faiss"
METADATA_PATH = PROJECT_ROOT / "vector_store" / "metadata.json"


def format_sources(sources: List[str]) -> str:
    if not sources:
        return "No sources available."
    return "\n".join([f"- {url}" for url in sources])


def answer_question(question: str) -> tuple[str, str, str]:
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", "No sources.", "0.0"

    try:
        retriever = FaissRetriever(index_path=str(INDEX_PATH), metadata_path=str(METADATA_PATH))
    except Exception as exc:
        return (
            f"Retriever is not ready: {exc}\nRun ingestion and indexing scripts first.",
            "No sources.",
            "0.0",
        )

    retrieved = retriever.search(question, top_k=4)
    answer_data = build_grounded_answer(question, retrieved)

    answer = answer_data.get("answer", "No answer.")
    sources = format_sources(answer_data.get("sources", []))
    confidence = str(answer_data.get("confidence", 0.0))
    return answer, sources, confidence


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="CompanyDocs RAG Assistant") as demo:
        gr.Markdown("# CompanyDocs RAG Assistant")
        gr.Markdown(
            "Ask questions about the indexed GitLab handbook/docs pages. "
            "The answer is grounded in retrieved chunks and always shows sources."
        )

        with gr.Row():
            question_box = gr.Textbox(label="Question", placeholder="Ask a documentation question")
        ask_button = gr.Button("Ask")

        answer_box = gr.Textbox(label="Answer", lines=7)
        sources_box = gr.Markdown(label="Sources")
        confidence_box = gr.Textbox(label="Confidence (top similarity score)")

        ask_button.click(
            fn=answer_question,
            inputs=[question_box],
            outputs=[answer_box, sources_box, confidence_box],
        )

        gr.Examples(
            examples=[
                "What is GitLab's approach to remote work?",
                "How does GitLab describe values?",
                "What are the rules for communication?",
                "What is GitLab's stock price forecast next year?",
            ],
            inputs=question_box,
        )

    return demo


if __name__ == "__main__":
    app = build_demo()
    app.launch()
