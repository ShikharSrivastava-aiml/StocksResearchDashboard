"""
Text Processing Utilities
Text cleaning and formatting functions
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Fix messy transcripts from API output.
    Removes excessive whitespace and fixes formatting.
    """
    if not text:
        return ""

    # Remove line breaks within words
    text = re.sub(r"(?<=\w)\n(?=\w)", "", text)

    # Replace multiple line breaks with single space
    text = re.sub(r"[\n\r]+", " ", text)

    # Replace multiple spaces with single space
    text = re.sub(r"\s{2,}", " ", text)

    # Fix spacing around "up" with numbers
    text = re.sub(r",?\s*up\s*(\d+)", r", up \1", text)

    # Fix spacing between numbers and letters
    text = re.sub(r"(\d)([A-Za-z])", r"\1 \2", text)

    # Remove spaces before punctuation
    text = re.sub(r"\s([,.!?])", r"\1", text)

    return text.strip()


def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs at sentence boundaries."""
    paragraphs = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [p.strip() for p in paragraphs if p.strip()]


def highlight_search_term(text: str, search_term: str) -> str:
    """Highlight search term in text using markdown bold."""
    if not search_term:
        return text

    return re.sub(
        f"({re.escape(search_term)})",
        r"**\1**",
        text,
        flags=re.IGNORECASE
    )


def extract_longest_sentence(text: str, max_length: int = 100) -> str:
    """Extract the longest sentence from text."""
    sentences = re.split(r'[.!?]+', text)
    if not sentences:
        return ""

    longest = max(sentences, key=len).strip()
    if len(longest) > max_length:
        longest = longest[:max_length] + "..."

    return longest