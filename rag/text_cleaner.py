from __future__ import annotations

import re
from bs4 import BeautifulSoup


def clean_html_to_text(html: str) -> str:
    """Convert raw HTML into a readable plain-text string."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove noisy tags we do not want in the retrieval corpus.
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "form"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    # Collapse repeated blank lines and excessive whitespace.
    normalized = "\n".join(lines)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()
