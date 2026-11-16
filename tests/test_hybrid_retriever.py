import pytest
from unittest.mock import Mock

from src.edurag_x.rag.hybrid_retriever import HybridRetriever


@pytest.fixture
def mock_retrievers():
    semantic = Mock()
    keyword = Mock()

    semantic.retrieve.return_value = [
        {
            "chunk_id": 1,
            "text": "Database transactions follow ACID properties.",
            "source": "dbms.pdf",
            "page_number": 1,
            "similarity_score": 0.90
        },
        {
            "chunk_id": 2,
            "text": "SQL indexing improves query performance.",
            "source": "sql.pdf",
            "page_number": 2,
            "similarity_score": 0.80
        }
    ]

    keyword.retrieve.return_value = [
        {
            "chunk_id": 2,
            "text": "SQL indexing improves query performance.",
            "source": "sql.pdf",
            "page_number": 2,
            "keyword_score": 2.5
        },
        {
            "chunk_id": 3,
            "text": "Database normalization reduces redundancy.",
            "source": "dbms.pdf",
            "page_number": 3,
            "keyword_score": 1.8
        }
    ]

    return semantic, keyword


def test_hybrid_retriever_combines_results(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword)
    results = retriever.retrieve("database query")
    assert len(results) == 3


def test_hybrid_retriever_ranks_common_document_higher(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword)
    results = retriever.retrieve("database query")
    assert results[0]["chunk_id"] == 2


def test_hybrid_retriever_adds_rrf_score(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword)
    results = retriever.retrieve("database query")

    for result in results:
        assert "rrf_score" in result
        assert result["rrf_score"] > 0


def test_hybrid_retriever_tracks_retrieval_sources(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword)
    results = retriever.retrieve("database query")

    common_document = next(
        result for result in results if result["chunk_id"] == 2
    )

    assert "semantic" in common_document["retrieval_sources"]
    assert "keyword" in common_document["retrieval_sources"]


def test_hybrid_retriever_respects_top_k(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword)
    results = retriever.retrieve("database query", top_k=2)
    assert len(results) == 2


def test_hybrid_retriever_rejects_empty_query(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword)

    with pytest.raises(ValueError, match="Search query cannot be empty."):
        retriever.retrieve("")


def test_hybrid_retriever_rejects_invalid_top_k(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword)

    with pytest.raises(ValueError, match="top_k must be greater than zero."):
        retriever.retrieve("database", top_k=0)


def test_hybrid_retriever_rejects_invalid_rrf_k(mock_retrievers):
    semantic, keyword = mock_retrievers

    with pytest.raises(ValueError, match="rrf_k must be a positive integer."):
        HybridRetriever(semantic, keyword, rrf_k=0)


def test_hybrid_retriever_passes_similarity_threshold(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword)

    retriever.retrieve("database query", min_similarity=0.70)

    semantic.retrieve.assert_called_once_with(
        "database query",
        top_k=5,
        min_similarity=0.70
    )


def test_rrf_score_is_calculated_exactly_for_common_document(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword, rrf_k=60)
    results = retriever.retrieve("database query")

    common = next(r for r in results if r["chunk_id"] == 2)

    expected = (1 / 62) + (1 / 61)

    assert common["rrf_score"] == pytest.approx(expected)


def test_semantic_only_document_has_correct_rrf_score(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword, rrf_k=60)
    results = retriever.retrieve("database query")

    document = next(r for r in results if r["chunk_id"] == 1)

    assert document["rrf_score"] == pytest.approx(1 / 61)
    assert document["retrieval_sources"] == ["semantic"]


def test_keyword_only_document_has_correct_rrf_score(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword, rrf_k=60)
    results = retriever.retrieve("database query")

    document = next(r for r in results if r["chunk_id"] == 3)

    assert document["rrf_score"] == pytest.approx(1 / 62)
    assert document["retrieval_sources"] == ["keyword"]


def test_retrieval_ranks_and_scores_are_preserved(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword)
    results = retriever.retrieve("database query")

    common = next(r for r in results if r["chunk_id"] == 2)

    assert common["semantic_rank"] == 2
    assert common["keyword_rank"] == 1
    assert common["similarity_score"] == 0.80
    assert common["keyword_score"] == 2.5


def test_same_document_is_merged_once(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword)
    results = retriever.retrieve("database query")

    matching = [r for r in results if r["chunk_id"] == 2]

    assert len(matching) == 1
    assert set(matching[0]["retrieval_sources"]) == {
        "semantic", "keyword"
    }


def test_results_are_sorted_by_rrf_score(mock_retrievers):
    semantic, keyword = mock_retrievers
    retriever = HybridRetriever(semantic, keyword)
    results = retriever.retrieve("database query")

    scores = [r["rrf_score"] for r in results]

    assert scores == sorted(scores, reverse=True)