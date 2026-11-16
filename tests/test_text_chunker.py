import pytest
from src.edurag_x.ingestion.text_chunker import TextChunker


def test_text_is_split_into_chunks():
    chunker = TextChunker(chunk_size=10, chunk_overlap=2)
    pages = [{"page_number": 1, "text": "abcdefghijklmnopqrstuvwxyz", "source": "sample.pdf"}]
    chunks = chunker.split_text(pages)
    assert len(chunks) > 1
    assert chunks[0]["text"] == "abcdefghij"


def test_chunk_size_limit():
    chunker = TextChunker(chunk_size=10, chunk_overlap=2)
    pages = [{"page_number": 1, "text": "abcdefghijklmnopqrstuvwxyz", "source": "sample.pdf"}]
    chunks = chunker.split_text(pages)
    for chunk in chunks:
        assert len(chunk["text"]) <= 10


def test_chunk_overlap_is_maintained():
    chunker = TextChunker(chunk_size=10, chunk_overlap=3)
    pages = [{"page_number": 1, "text": "abcdefghijklmnopqrstuvwxyz", "source": "sample.pdf"}]
    chunks = chunker.split_text(pages)
    assert chunks[0]["text"][-3:] == chunks[1]["text"][:3]


def test_empty_text_returns_no_chunks():
    chunker = TextChunker()
    pages = [{"page_number": 1, "text": "   ", "source": "sample.pdf"}]
    chunks = chunker.split_text(pages)
    assert chunks == []


def test_invalid_chunk_size_is_rejected():
    with pytest.raises(ValueError):
        TextChunker(chunk_size=0, chunk_overlap=0)
