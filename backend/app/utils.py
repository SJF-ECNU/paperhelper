from __future__ import annotations


import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple


@dataclass
class ParsedDocument:
    text: str
    sections: List[Tuple[str, str]]


SUPPORTED_EXTENSIONS = {".pdf", ".md", ".markdown", ".txt"}


class UnsupportedDocumentError(Exception):
    """Raised when the provided document type is not supported."""


class DocumentTooLargeError(Exception):
    """Raised when the provided document is too large."""


def generate_document_id() -> str:
    return uuid.uuid4().hex


def load_document(path: Path, max_size_mb: int = 25) -> ParsedDocument:
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise UnsupportedDocumentError(f"Unsupported file type: {path.suffix}")
    if path.stat().st_size > max_size_mb * 1024 * 1024:
        raise DocumentTooLargeError(f"File size exceeds {max_size_mb} MB limit")

    if path.suffix.lower() == ".pdf":
        text = _extract_pdf_text(path)
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")

    sections = _split_into_sections(text)
    return ParsedDocument(text=text, sections=sections)


def _extract_pdf_text(path: Path) -> str:
    try:
        import PyPDF2  # type: ignore
    except ModuleNotFoundError:
        data = path.read_bytes()
        return data.decode("latin-1", errors="ignore")

    text_fragments: List[str] = []
    reader = PyPDF2.PdfReader(str(path))
    for page in reader.pages:
        text_fragments.append(page.extract_text() or "")
    return "\n".join(text_fragments)


def _split_into_sections(text: str, chunk_size: int = 1200, overlap: int = 150) -> List[Tuple[str, str]]:
    words = text.split()
    if not words:
        return [("Empty", "")] 
    sections: List[Tuple[str, str]] = []
    start = 0
    while start < len(words):
        end = min(len(words), start + chunk_size)
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        heading = _infer_heading(chunk_text, len(sections) + 1)
        sections.append((heading, chunk_text))
        if end == len(words):
            break
        start = max(end - overlap, start + 1)
    return sections


def _infer_heading(chunk: str, idx: int) -> str:
    heading_match = re.search(r"^#+\s*(.+)$", chunk, re.MULTILINE)
    if heading_match:
        return heading_match.group(1).strip()
    first_sentence = chunk.strip().split(".")[0]
    if len(first_sentence) > 120:
        first_sentence = first_sentence[:117] + "..."
    return first_sentence or f"Section {idx}"


def build_embedding(section_text: str) -> List[float]:
    tokens = re.findall(r"[a-zA-Z]+", section_text.lower())
    vector = [0.0] * 10
    for token in tokens:
        bucket = hash(token) % len(vector)
        vector[bucket] += 1.0
    length = sum(vector) or 1.0
    return [value / length for value in vector]


def extract_keywords(text: str, top_k: int = 10) -> List[str]:
    tokens = re.findall(r"[a-zA-Z]{5,}", text.lower())
    frequency = {}
    for token in tokens:
        frequency[token] = frequency.get(token, 0) + 1
    sorted_tokens = sorted(frequency.items(), key=lambda item: item[1], reverse=True)
    return [token for token, _ in sorted_tokens[:top_k]]


def summarize_sections(sections: Iterable[Tuple[str, str]], max_sentences: int = 3) -> str:
    sentences: List[str] = []
    for _, body in sections:
        for sentence in re.split(r"(?<=[.!?])\s+", body.strip()):
            if sentence:
                sentences.append(sentence.strip())
    return " ".join(sentences[:max_sentences])
