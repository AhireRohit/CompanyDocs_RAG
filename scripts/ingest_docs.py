from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from rag.chunker import split_into_word_chunks
from rag.text_cleaner import clean_html_to_text

SOURCES_PATH = PROJECT_ROOT / "data" / "sources.txt"
OUTPUT_PATH = PROJECT_ROOT / "data" / "chunks.json"


def read_sources(path: Path) -> List[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    urls = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
    return urls


def fetch_page(url: str, timeout: int = 25) -> str:
    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "CompanyDocs-RAG-Assistant/1.0"},
    )
    response.raise_for_status()
    return response.text


def extract_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled Page"
    return title


def build_chunks(urls: List[str]) -> List[Dict]:
    all_chunks: List[Dict] = []
    chunk_id = 1

    for url in tqdm(urls, desc="Ingesting pages"):
        try:
            html = fetch_page(url)
            title = extract_title(html)
            text = clean_html_to_text(html)
            if not text:
                continue

            chunks = split_into_word_chunks(text, chunk_size=500, overlap=80)
            for chunk_text in chunks:
                all_chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "title": title,
                        "url": url,
                        "text": chunk_text,
                        "word_count": len(chunk_text.split()),
                    }
                )
                chunk_id += 1
        except Exception as exc:
            print(f"[WARN] Failed to ingest {url}: {exc}")
            continue

    return all_chunks


def main() -> None:
    if not SOURCES_PATH.exists():
        raise FileNotFoundError(f"Could not find source list at {SOURCES_PATH}")

    urls = read_sources(SOURCES_PATH)
    if not urls:
        raise ValueError("No URLs found in data/sources.txt")

    chunks = build_chunks(urls)
    OUTPUT_PATH.write_text(json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Saved {len(chunks)} chunks to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
