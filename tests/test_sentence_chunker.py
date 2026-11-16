import pytest

from src.edurag_x.ingestion.sentence_chunker import SentenceAwareChunker


def test_text_is_split_into_multiple_chunks():

    chunker = SentenceAwareChunker(
        chunk_size=50,
        chunk_overlap=10
    )

    text = (
        "Database systems store information. "
        "Normalization reduces redundancy. "
        "Primary keys identify records."
    )

    pages = [{
        "page_number": 1,
        "text": text,
        "source": "sample.pdf"
    }]

    chunks = chunker.split_text(pages)

    assert len(chunks) > 1


def test_sentence_boundaries_are_preserved():

    chunker = SentenceAwareChunker(
        chunk_size=40,
        chunk_overlap=10
    )

    pages = [{
        "page_number": 1,
        "text": (
            "Database systems store information. "
            "Normalization reduces redundancy."
        ),
        "source": "sample.pdf"
    }]

    chunks = chunker.split_text(pages)

    assert chunks[0]["text"] == (
        "Database systems store information."
    )


def test_chunk_size_limit():

    chunker = SentenceAwareChunker(
        chunk_size=50,
        chunk_overlap=10
    )

    pages = [{
        "page_number": 1,
        "text": (
            "Database systems store information. "
            "Normalization reduces redundancy. "
            "Primary keys identify records."
        ),
        "source": "sample.pdf"
    }]

    chunks = chunker.split_text(pages)

    for chunk in chunks:
        assert len(chunk["text"]) <= 50


def test_sentence_overlap_is_maintained():

    chunker = SentenceAwareChunker(
        chunk_size=40,
        chunk_overlap=20
    )

    pages = [{
        "page_number": 1,
        "text": (
            "First sentence. "
            "Second sentence. "
            "Third sentence."
        ),
        "source": "sample.pdf"
    }]

    chunks = chunker.split_text(pages)

    assert len(chunks) > 1
    assert "Second sentence." in chunks[0]["text"]
    assert "Second sentence." in chunks[1]["text"]


def test_empty_text_returns_no_chunks():

    chunker = SentenceAwareChunker()

    pages = [{
        "page_number": 1,
        "text": "   ",
        "source": "sample.pdf"
    }]

    assert chunker.split_text(pages) == []


def test_invalid_chunk_size_is_rejected():

    with pytest.raises(ValueError):
        SentenceAwareChunker(
            chunk_size=0,
            chunk_overlap=0
        )


def test_invalid_overlap_is_rejected():

    with pytest.raises(ValueError):
        SentenceAwareChunker(
            chunk_size=10,
            chunk_overlap=10
        )


def test_numbered_headings_are_not_split():

    chunker = SentenceAwareChunker()

    text = (
        "1. Introduction to DBMS "
        "2. Database Normalization "
        "3. First Normal Form."
    )

    sentences = chunker.split_sentences(text)

    assert sentences == [
        "1. Introduction to DBMS 2. Database Normalization 3. First Normal Form."
    ]


def test_chunk_size_limit_with_overlap():

    chunker = SentenceAwareChunker(
        chunk_size=50,
        chunk_overlap=20
    )

    pages = [{
        "page_number": 1,
        "text": (
            "AAAAAAAAAAAAAA. "
            + "B" * 44
            + "."
        ),
        "source": "sample.pdf"
    }]

    chunks = chunker.split_text(pages)

    assert len(chunks) > 1

    for chunk in chunks:
        assert len(chunk["text"]) <= 50