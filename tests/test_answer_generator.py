from unittest.mock import Mock, patch
import pytest

from src.edurag_x.rag.answer_generator import GroundedAnswerGenerator


@patch("src.edurag_x.rag.answer_generator.genai.Client")
def test_generate_answer_returns_response(mock_client_class):
    mock_client = Mock()
    mock_client_class.return_value = mock_client

    mock_response = Mock()
    mock_response.text = "DBMS manages databases. [Source: dbms.pdf, Page: 1]"
    mock_client.models.generate_content.return_value = mock_response

    generator = GroundedAnswerGenerator()

    chunks = [
        {
            "source": "dbms.pdf",
            "page_number": 1,
            "text": "A DBMS is software used to manage databases."
        }
    ]

    result = generator.generate_answer("What is DBMS?", chunks)

    assert "DBMS manages databases" in result
    mock_client.models.generate_content.assert_called_once()


@patch("src.edurag_x.rag.answer_generator.genai.Client")
def test_prompt_contains_document_context(mock_client_class):
    mock_client = Mock()
    mock_client_class.return_value = mock_client

    mock_response = Mock()
    mock_response.text = "Test answer"
    mock_client.models.generate_content.return_value = mock_response

    generator = GroundedAnswerGenerator()

    chunks = [
        {
            "source": "dbms.pdf",
            "page_number": 2,
            "text": "Normalization reduces data redundancy."
        }
    ]

    generator.generate_answer("What is normalization?", chunks)

    call_arguments = mock_client.models.generate_content.call_args.kwargs
    prompt = call_arguments["contents"]

    assert "dbms.pdf" in prompt
    assert "PAGE: 2" in prompt
    assert "Normalization reduces data redundancy." in prompt


@patch("src.edurag_x.rag.answer_generator.genai.Client")
def test_empty_question_is_rejected(mock_client_class):
    generator = GroundedAnswerGenerator()

    with pytest.raises(ValueError):
        generator.generate_answer("", [])


@patch("src.edurag_x.rag.answer_generator.genai.Client")
def test_empty_retrieved_chunks_return_abstention(mock_client_class):
    generator = GroundedAnswerGenerator()

    result = generator.generate_answer("What is DBMS?", [])

    assert "could not find relevant information" in result


@patch("src.edurag_x.rag.answer_generator.genai.Client")
def test_api_error_raises_runtime_error(mock_client_class):
    mock_client = Mock()
    mock_client_class.return_value = mock_client

    mock_client.models.generate_content.side_effect = Exception("API unavailable")

    generator = GroundedAnswerGenerator()

    chunks = [
        {
            "source": "dbms.pdf",
            "page_number": 1,
            "text": "DBMS manages databases."
        }
    ]

    with pytest.raises(
        RuntimeError,
        match="Answer generation failed: API unavailable"
    ):
        generator.generate_answer("What is DBMS?", chunks)
