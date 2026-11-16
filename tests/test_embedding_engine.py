from unittest.mock import Mock, patch
import pytest

from src.edurag_x.llm.embedding_engine import EmbeddingEngine


@patch("src.edurag_x.llm.embedding_engine.genai.Client")
def test_embed_documents_returns_embeddings(mock_client_class):
    mock_client = Mock()
    mock_client_class.return_value = mock_client

    mock_response = Mock()
    mock_response.embeddings = [
        Mock(values=[0.1, 0.2, 0.3])
    ]
    mock_client.models.embed_content.return_value = mock_response

    engine = EmbeddingEngine()
    result = engine.embed_documents(["Database Management System"])

    assert len(result) == 1
    assert len(result[0]) == 3
    mock_client.models.embed_content.assert_called_once()


@patch("src.edurag_x.llm.embedding_engine.genai.Client")
def test_embed_query_returns_embedding(mock_client_class):
    mock_client = Mock()
    mock_client_class.return_value = mock_client

    mock_response = Mock()
    mock_response.embeddings = [
        Mock(values=[0.4, 0.5, 0.6])
    ]
    mock_client.models.embed_content.return_value = mock_response

    engine = EmbeddingEngine()
    result = engine.embed_query("What is DBMS?")

    assert len(result) == 3
    mock_client.models.embed_content.assert_called_once()


@patch("src.edurag_x.llm.embedding_engine.genai.Client")
def test_empty_documents_return_empty_list(mock_client_class):
    engine = EmbeddingEngine()

    result = engine.embed_documents([])

    assert result == []
    mock_client_class.return_value.models.embed_content.assert_not_called()


@patch("src.edurag_x.llm.embedding_engine.genai.Client")
def test_empty_document_text_is_rejected(mock_client_class):
    engine = EmbeddingEngine()

    with pytest.raises(ValueError):
        engine.embed_documents(["   "])


@patch("src.edurag_x.llm.embedding_engine.genai.Client")
def test_empty_query_is_rejected(mock_client_class):
    engine = EmbeddingEngine()

    with pytest.raises(ValueError):
        engine.embed_query("")
