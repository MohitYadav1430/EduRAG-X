import pytest
from unittest.mock import Mock

from src.edurag_x.rag.evidence_relevance_filter import (
    EvidenceRelevanceFilter
)


@pytest.fixture
def sample_documents():
    return [
        {
            "chunk_id": 1,
            "text": "Database normalization reduces redundancy.",
            "source": "dbms.pdf",
            "page_number": 1
        },
        {
            "chunk_id": 2,
            "text": "Operating systems manage processes.",
            "source": "os.pdf",
            "page_number": 2
        }
    ]


def test_filter_keeps_relevant_chunks(sample_documents):

    vector_store = Mock()

    vector_store.score_documents.return_value = [
        {**sample_documents[0], "similarity_score": 0.85},
        {**sample_documents[1], "similarity_score": 0.30}
    ]

    relevance_filter = EvidenceRelevanceFilter(
        vector_store,
        min_relevance=0.60
    )

    results = relevance_filter.filter(
        [1.0, 0.0, 0.0],
        sample_documents
    )

    assert len(results) == 1
    assert results[0]["chunk_id"] == 1
    assert results[0]["similarity_score"] == 0.85


def test_filter_rejects_irrelevant_chunks(sample_documents):

    vector_store = Mock()

    vector_store.score_documents.return_value = [
        {**sample_documents[0], "similarity_score": 0.20},
        {**sample_documents[1], "similarity_score": 0.35}
    ]

    relevance_filter = EvidenceRelevanceFilter(
        vector_store,
        min_relevance=0.60
    )

    results = relevance_filter.filter(
        [1.0, 0.0, 0.0],
        sample_documents
    )

    assert results == []


def test_filter_handles_empty_input():

    vector_store = Mock()

    relevance_filter = EvidenceRelevanceFilter(vector_store)

    results = relevance_filter.filter(
        [1.0, 0.0, 0.0],
        []
    )

    assert results == []
    vector_store.score_documents.assert_not_called()


def test_filter_rejects_invalid_threshold():

    vector_store = Mock()

    with pytest.raises(ValueError):
        EvidenceRelevanceFilter(
            vector_store,
            min_relevance=1.5
        )


def test_filter_preserves_original_documents(sample_documents):

    vector_store = Mock()

    vector_store.score_documents.return_value = [
        {**sample_documents[0], "similarity_score": 0.85}
    ]

    relevance_filter = EvidenceRelevanceFilter(
        vector_store,
        min_relevance=0.60
    )

    relevance_filter.filter(
        [1.0, 0.0, 0.0],
        sample_documents[:1]
    )

    assert "similarity_score" not in sample_documents[0]
    assert sample_documents[0]["chunk_id"] == 1


def test_filter_accepts_threshold_boundary(sample_documents):

    vector_store = Mock()

    vector_store.score_documents.return_value = [
        {**sample_documents[0], "similarity_score": 0.60}
    ]

    relevance_filter = EvidenceRelevanceFilter(
        vector_store,
        min_relevance=0.60
    )

    results = relevance_filter.filter(
        [1.0, 0.0, 0.0],
        sample_documents[:1]
    )

    assert len(results) == 1