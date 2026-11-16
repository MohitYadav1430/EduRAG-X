from unittest.mock import Mock
import pytest

from src.edurag_x.rag.retriever import Retriever


def test_retrieve_returns_relevant_documents():
    mock_store = Mock()
    mock_embedding = Mock()

    mock_embedding.embed_query.return_value = [0.1, 0.2, 0.3]

    expected_results = [
        {"chunk_id": 1, "text": "Database Management System", "similarity_score": 0.95}
    ]

    mock_store.search.return_value = expected_results

    retriever = Retriever(
        vector_store=mock_store,
        embedding_engine=mock_embedding
    )

    results = retriever.retrieve("What is DBMS?")

    assert results == expected_results
    mock_embedding.embed_query.assert_called_once_with("What is DBMS?")
    mock_store.search.assert_called_once_with(
        query_embedding=[0.1, 0.2, 0.3],
        top_k=5
    )


def test_custom_top_k_is_used():
    mock_store = Mock()
    mock_embedding = Mock()

    mock_embedding.embed_query.return_value = [0.1, 0.2, 0.3]
    mock_store.search.return_value = []

    retriever = Retriever(mock_store, mock_embedding)

    retriever.retrieve("Explain normalization", top_k=3)

    mock_store.search.assert_called_once_with(
        query_embedding=[0.1, 0.2, 0.3],
        top_k=3
    )


def test_empty_query_is_rejected():
    retriever = Retriever(Mock(), Mock())

    with pytest.raises(ValueError):
        retriever.retrieve("")


def test_invalid_top_k_is_rejected():
    retriever = Retriever(Mock(), Mock())

    with pytest.raises(ValueError):
        retriever.retrieve("What is DBMS?", top_k=0)


def test_minimum_similarity_filters_irrelevant_chunks():

    mock_store = Mock()
    mock_embedding = Mock()

    mock_embedding.embed_query.return_value = [0.1, 0.2, 0.3]

    mock_store.search.return_value = [
        {"chunk_id": 1, "similarity_score": 0.95},
        {"chunk_id": 2, "similarity_score": 0.72},
        {"chunk_id": 3, "similarity_score": 0.31}
    ]

    retriever = Retriever(mock_store, mock_embedding)

    results = retriever.retrieve(
        "What is DBMS?",
        min_similarity=0.60
    )

    assert len(results) == 2
    assert results[0]["chunk_id"] == 1
    assert results[1]["chunk_id"] == 2


def test_minimum_similarity_none_preserves_all_results():

    mock_store = Mock()
    mock_embedding = Mock()

    mock_embedding.embed_query.return_value = [0.1, 0.2, 0.3]

    expected_results = [
        {"chunk_id": 1, "similarity_score": 0.95},
        {"chunk_id": 2, "similarity_score": 0.20}
    ]

    mock_store.search.return_value = expected_results

    retriever = Retriever(mock_store, mock_embedding)

    results = retriever.retrieve("What is DBMS?")

    assert results == expected_results


@pytest.mark.parametrize("threshold", [-1.1, 1.1, float("nan"), float("inf")])
def test_invalid_similarity_threshold_is_rejected(threshold):

    retriever = Retriever(Mock(), Mock())

    with pytest.raises(ValueError):
        retriever.retrieve(
            "What is DBMS?",
            min_similarity=threshold
        )


def test_non_numeric_similarity_threshold_is_rejected():

    retriever = Retriever(Mock(), Mock())

    with pytest.raises(ValueError):
        retriever.retrieve(
            "What is DBMS?",
            min_similarity="high"
        )
