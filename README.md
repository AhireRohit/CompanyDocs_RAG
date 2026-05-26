---
title: CompanyDocs RAG Assistant
emoji: 📚
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.14.0
app_file: app.py
pinned: false
---

# CompanyDocs RAG Assistant

A beginner-friendly Retrieval-Augmented Generation (RAG) chatbot that answers questions using a curated set of public GitLab handbook/docs pages.  
It runs fully on free and open-source tools, works locally, and can be deployed on Hugging Face Spaces.

## Why I built this

I wanted a resume project that is practical and easy to explain in interviews:

- Scrape real company documentation pages
- Build a vector index with free embeddings
- Retrieve evidence chunks and answer with citations
- Evaluate retrieval quality with a small custom benchmark

The code avoids heavy abstractions so each file is easy to study line by line.

## Tech stack

- Python
- Gradio (UI)
- `sentence-transformers/all-MiniLM-L6-v2` (embeddings)
- FAISS (vector search)
- Requests + BeautifulSoup (data ingestion/cleaning)

## Project structure

```text
company-docs-rag-assistant/
  app.py
  requirements.txt
  README.md
  .gitignore
  data/
    sources.txt
    chunks.json
  scripts/
    ingest_docs.py
    build_index.py
  rag/
    text_cleaner.py
    chunker.py
    retriever.py
    answer_builder.py
  vector_store/
    index.faiss
    metadata.json
  evaluation/
    eval_questions.json
    evaluate_retrieval.py
    compare_baseline.py
    results.json
```

## Architecture (plain-text diagram)

```text
data/sources.txt
      |
      v
scripts/ingest_docs.py ---> data/chunks.json
      |
      v
scripts/build_index.py ---> vector_store/index.faiss + metadata.json
      |
      v
app.py (Gradio UI) ---> rag/retriever.py ---> top-k chunks
      |
      v
rag/answer_builder.py ---> grounded answer + source URLs
      |
      v
evaluation/*.py ---> retrieval metrics in evaluation/results.json
```

## Local setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/ingest_docs.py
python scripts/build_index.py
python evaluation/evaluate_retrieval.py
python evaluation/compare_baseline.py
python app.py
```

Windows PowerShell activation command:

```powershell
.\venv\Scripts\Activate.ps1
```

## How the app behaves

- Retrieves top 4 relevant chunks for each question
- Builds answer only from retrieved chunk text
- Shows source URLs used
- Returns fallback for unsupported questions:
  - `I could not find this in the indexed documentation.`
- Does not use paid APIs or external hosted LLM APIs

## Evaluation design

`evaluation/eval_questions.json` contains a small custom set of supported and unsupported questions.

`evaluation/evaluate_retrieval.py` reports:

- FAISS top-1 accuracy
- FAISS top-4 accuracy
- average retrieval time
- citation coverage
- unsupported-query rejection accuracy

`evaluation/compare_baseline.py` compares:

- keyword-search top-4 accuracy
- FAISS top-4 accuracy
- percentage-point improvement
- average retrieval time for both

## Metrics

Metrics are read from `evaluation/results.json` after running both evaluation scripts.

Current metrics:

```json
{}
```

Notes:

- The evaluation set is custom-made and small.
- Scores are useful for project comparison, not a production benchmark.
- This is not a production-ready chatbot.

## Deploy on Hugging Face Spaces (free)

1. Create a new Hugging Face Space.
2. Select **Gradio** as the SDK.
3. Upload this project (or connect the GitHub repo).
4. Ensure `app.py` is at the repo root.
5. Ensure `requirements.txt` is present.
6. Space will install dependencies and run automatically.

