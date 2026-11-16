import pytest

from src.edurag_x.rag.vector_store import VectorStore


def sample_chunks():
    return [
        {"chunk_id": 1, "text": "Database management system", "source": "dbms.pdf", "page_number": 1},
        {"chunk_id": 2, "text": "Operating system concepts", "source": "os.pdf", "page_number": 2},
        {"chunk_id": 3, "text": "Computer networks", "source": "cn.pdf", "page_number": 3}
    ]


def sample_embeddings():
    return [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ]


def test_documents_are_stored():
    store = VectorStore()

    total = store.add_documents(sample_chunks(), sample_embeddings())

    assert total == 3
    assert len(store.documents) == 3


def test_total_vectors_count():
    store = VectorStore()

    store.add_documents(sample_chunks(), sample_embeddings())

    assert store.total_vectors() == 3


def test_similarity_search_returns_relevant_result():
    store = VectorStore()
    store.add_documents(sample_chunks(), sample_embeddings())

    results = store.search([1.0, 0.0, 0.0], top_k=1)

    assert len(results) == 1
    assert results[0]["chunk_id"] == 1
    assert results[0]["similarity_score"] == pytest.approx(1.0)


def test_top_k_limit():
    store = VectorStore()
    store.add_documents(sample_chunks(), sample_embeddings())

    results = store.search([1.0, 0.0, 0.0], top_k=2)

    assert len(results) == 2


def test_search_on_empty_store_is_rejected():
    store = VectorStore()

    with pytest.raises(ValueError):
        store.search([1.0, 0.0, 0.0])


def test_embedding_dimension_mismatch_is_rejected():
    store = VectorStore()
    store.add_documents(sample_chunks(), sample_embeddings())

    with pytest.raises(ValueError):
        store.search([1.0, 0.0])


def test_vector_store_save(tmp_path):
    store = VectorStore()
    store.add_documents(sample_chunks(), sample_embeddings())

    result = store.save(tmp_path)

    assert result is True
    assert (tmp_path / "index.faiss").exists()
    assert (tmp_path / "documents.json").exists()


def test_vector_store_load_and_search(tmp_path):
    original_store = VectorStore()
    original_store.add_documents(sample_chunks(), sample_embeddings())

    original_store.save(tmp_path)

    loaded_store = VectorStore.load(tmp_path)

    assert loaded_store.total_vectors() == 3
    assert loaded_store.documents == sample_chunks()

    results = loaded_store.search([1.0, 0.0, 0.0], top_k=1)

    assert results[0]["chunk_id"] == 1
    assert results[0]["similarity_score"] == pytest.approx(1.0)


def test_vector_store_load_missing_files(tmp_path):
    with pytest.raises(FileNotFoundError):
        VectorStore.load(tmp_path)


def test_score_documents_returns_cosine_similarity():
    store = VectorStore()
    chunks = sample_chunks()
    store.add_documents(chunks, sample_embeddings())

    results = store.score_documents(
        [1.0, 0.0, 0.0],
        [chunks[0], chunks[1]]
    )

    assert len(results) == 2
    assert results[0]["similarity_score"] == pytest.approx(1.0)
    assert results[1]["similarity_score"] == pytest.approx(0.0)


def test_score_documents_preserves_original_metadata():
    store = VectorStore()
    chunks = sample_chunks()
    store.add_documents(chunks, sample_embeddings())

    results = store.score_documents(
        [1.0, 0.0, 0.0],
        [chunks[0]]
    )

    assert results[0]["chunk_id"] == 1
    assert results[0]["source"] == "dbms.pdf"
    assert "similarity_score" not in chunks[0]


def test_score_documents_rejects_unknown_document():
    store = VectorStore()
    store.add_documents(sample_chunks(), sample_embeddings())

    unknown_document = {
        "chunk_id": 99,
        "text": "Unknown content",
        "source": "unknown.pdf",
        "page_number": 1
    }

    with pytest.raises(ValueError, match="Document not found"):
        store.score_documents(
            [1.0, 0.0, 0.0],
            [unknown_document]
        )


def test_score_documents_rejects_zero_query_vector():
    store = VectorStore()
    store.add_documents(sample_chunks(), sample_embeddings())

    with pytest.raises(ValueError, match="zero vector"):
        store.score_documents(
            [0.0, 0.0, 0.0],
            [sample_chunks()[0]]
        )
