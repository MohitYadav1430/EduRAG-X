import pytest

from unittest.mock import Mock

from src.edurag_x.rag.keyword_retriever import KeywordRetriever


@pytest.fixture
def vector_store():

    store = Mock()

    store.documents = [
        {
            "chunk_id": 1,
            "text": "Database transactions follow ACID properties.",
            "source": "dbms.pdf",
            "page_number": 1
        },
        {
            "chunk_id": 2,
            "text": "SQL indexing improves database query performance.",
            "source": "sql.pdf",
            "page_number": 2
        },
        {
            "chunk_id": 3,
            "text": "Photosynthesis converts sunlight into chemical energy.",
            "source": "biology.pdf",
            "page_number": 1
        }
    ]

    return store


def test_keyword_retriever_returns_matching_document(vector_store):

    retriever = KeywordRetriever(vector_store)

    results = retriever.retrieve("ACID database transactions")

    assert len(results) > 0
    assert results[0]["chunk_id"] == 1
    assert results[0]["keyword_score"] > 0


def test_keyword_retriever_respects_top_k(vector_store):

    retriever = KeywordRetriever(vector_store)

    results = retriever.retrieve(
        "database SQL",
        top_k=1
    )

    assert len(results) <= 1


def test_keyword_retriever_rejects_empty_query(vector_store):

    retriever = KeywordRetriever(vector_store)

    with pytest.raises(
        ValueError,
        match="Search query cannot be empty."
    ):
        retriever.retrieve("")


def test_keyword_retriever_returns_empty_for_irrelevant_query(vector_store):

    retriever = KeywordRetriever(vector_store)

    results = retriever.retrieve(
        "quantum mechanics"
    )

    assert results == []


def test_keyword_retriever_handles_empty_vector_store():

    store = Mock()
    store.documents = []

    retriever = KeywordRetriever(store)

    results = retriever.retrieve("database")

    assert results == []


def test_keyword_retriever_rejects_invalid_top_k(vector_store):

    retriever = KeywordRetriever(vector_store)

    with pytest.raises(
        ValueError,
        match="top_k must be greater than zero."
    ):
        retriever.retrieve("database", top_k=0)
def test_keyword_retriever_refreshes_after_new_documents_are_added(vector_store):

    retriever = KeywordRetriever(vector_store)

    initial_count = len(retriever.documents)

    vector_store.documents.append({
        "chunk_id": 4,
        "text": "Machine learning uses training data and prediction models.",
        "source": "ml.pdf",
        "page_number": 1
    })

    results = retriever.retrieve("machine learning training")

    assert len(retriever.documents) == initial_count + 1
    assert results[0]["chunk_id"] == 4


def test_keyword_retriever_refreshes_after_document_text_changes(vector_store):

    retriever = KeywordRetriever(vector_store)

    vector_store.documents[0]["text"] = (
        "Artificial intelligence and neural networks."
    )

    results = retriever.retrieve("neural networks")

    assert len(results) > 0
    assert results[0]["chunk_id"] == 1


def test_keyword_retriever_handles_documents_with_no_tokens():

    store = Mock()
    store.documents = [
        {
            "chunk_id": 1,
            "text": "!!! ... ???",
            "source": "empty.pdf",
            "page_number": 1
        }
    ]

    retriever = KeywordRetriever(store)

    assert retriever.retrieve("database") == []