from unittest.mock import Mock

import pytest

from src.edurag_x.rag.rag_pipeline import RAGPipeline


def test_complete_rag_workflow():

    question = "What is database normalization?"

    retrieved_chunks = [
        {
            "source": "dbms_sample.pdf",
            "page_number": 1,
            "text": "Normalization reduces data redundancy."
        }
    ]

    retriever = Mock()
    retriever.retrieve.return_value = retrieved_chunks

    answer_generator = Mock()
    answer_generator.generate_answer.return_value = (
        "Normalization reduces data redundancy. "
        "[Source: dbms_sample.pdf, Page: 1]"
    )

    citation_validator = Mock()
    citation_validator.validate.return_value = {
        "total_citations": 1,
        "valid_citations": 1,
        "invalid_citations": 0,
        "missing_citations": False,
        "all_valid": True
    }

    evidence_verifier = Mock()
    evidence_verifier.verify.return_value = {
        "verification_status": "COMPLETED",
        "claims": [
            {
                "claim": "Normalization reduces data redundancy.",
                "status": "SUPPORTED"
            }
        ]
    }

    pipeline = RAGPipeline(
        retriever=retriever,
        answer_generator=answer_generator,
        citation_validator=citation_validator,
        evidence_verifier=evidence_verifier
    )

    result = pipeline.answer_question(question)

    assert result["question"] == question
    assert result["status"] == "COMPLETED"
    assert result["answer"] is not None
    assert result["error"] is None
    assert result["retrieved_chunks"] == retrieved_chunks
    assert result["citation_validation"]["all_valid"] is True
    assert result["evidence_verification"]["verification_status"] == "COMPLETED"

    retriever.retrieve.assert_called_once_with(question, top_k=5)
    answer_generator.generate_answer.assert_called_once_with(
        question, retrieved_chunks
    )
    citation_validator.validate.assert_called_once_with(
        result["answer"], retrieved_chunks
    )
    evidence_verifier.verify.assert_called_once_with(
        result["answer"], retrieved_chunks
    )


def test_rag_pipeline_rejects_empty_question():

    retriever = Mock()

    pipeline = RAGPipeline(
        retriever=retriever,
        answer_generator=Mock(),
        citation_validator=Mock(),
        evidence_verifier=Mock()
    )

    with pytest.raises(ValueError, match="Question cannot be empty."):
        pipeline.answer_question("")

    retriever.retrieve.assert_not_called()


def test_answer_generation_failure_stops_validation():

    question = "What is database normalization?"

    retrieved_chunks = [
        {
            "source": "dbms_sample.pdf",
            "page_number": 1,
            "text": "Normalization reduces data redundancy."
        }
    ]

    retriever = Mock()
    retriever.retrieve.return_value = retrieved_chunks

    answer_generator = Mock()
    answer_generator.generate_answer.side_effect = RuntimeError(
        "Answer generation failed: API unavailable"
    )

    citation_validator = Mock()
    evidence_verifier = Mock()

    pipeline = RAGPipeline(
        retriever=retriever,
        answer_generator=answer_generator,
        citation_validator=citation_validator,
        evidence_verifier=evidence_verifier
    )

    result = pipeline.answer_question(question)

    assert result["question"] == question
    assert result["status"] == "ANSWER_GENERATION_FAILED"
    assert result["answer"] is None
    assert "API unavailable" in result["error"]
    assert result["retrieved_chunks"] == retrieved_chunks
    assert result["citation_validation"] is None
    assert result["evidence_verification"] is None

    citation_validator.validate.assert_not_called()
    evidence_verifier.verify.assert_not_called()
