from pathlib import Path

import pytest

from app import utils


def test_generate_document_id_unique():
    ids = {utils.generate_document_id() for _ in range(10)}
    assert len(ids) == 10


def test_extract_keywords_returns_top_tokens():
    text = "Machine learning enables new machine learning systems"
    keywords = utils.extract_keywords(text, top_k=2)
    assert keywords[0] == "machine"
    assert "learning" in keywords


def test_load_document_markdown(tmp_path: Path):
    content = "# Heading\nSome content here."
    path = tmp_path / "test.md"
    path.write_text(content)
    parsed = utils.load_document(path)
    assert parsed.text.startswith("# Heading")
    assert len(parsed.sections) >= 1


def test_load_document_rejects_large_file(tmp_path: Path):
    path = tmp_path / "large.txt"
    path.write_bytes(b"0" * 1024 * 1024 * 2)
    with pytest.raises(utils.DocumentTooLargeError):
        utils.load_document(path, max_size_mb=1)
