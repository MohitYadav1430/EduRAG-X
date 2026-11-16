import json
from unittest.mock import Mock, patch

import pytest

from src.edurag_x.rag.evidence_verifier import EvidenceVerifier


def sample_chunks():
    return [
        {
            "source": "dbms.pdf",
            "page_number": 1,
            "text": "Normalization reduces data redundancy."
        }
    ]


def create_response(claims):
    response = Mock()
    response.text = json.dumps({
        "verification_status": "COMPLETED",
        "claims": claims
    })
    return response


@patch("src.edurag_x.rag.evidence_verifier.genai.Client")
def test_supported_claim_is_verified(mock_client_class):
    mock_client = Mock()
    mock_client_class.return_value = mock_client

    mock_client.models.generate_content.return_value = create_response([
        {
            "claim": "Normalization reduces data redundancy.",
            "status": "SUPPORTED",
            "evidence": [{"source": "dbms.pdf", "page": 1}],
            "reason": "Directly supported by the document."
        }
    ])

    verifier = EvidenceVerifier()
    result = verifier.verify("Normalization reduces redundancy.", sample_chunks())

    assert result["total_claims"] == 1
    assert result["supported_claims"] == 1
    assert result["claims"][0]["status"] == "SUPPORTED"
    assert result["claims"][0]["evidence_references_valid"] is True


@patch("src.edurag_x.rag.evidence_verifier.genai.Client")
def test_unsupported_claim_is_identified(mock_client_class):
    mock_client = Mock()
    mock_client_class.return_value = mock_client

    mock_client.models.generate_content.return_value = create_response([
        {
            "claim": "DBMS always uses machine learning.",
            "status": "UNSUPPORTED",
            "evidence": [],
            "reason": "The document does not mention this."
        }
    ])

    verifier = EvidenceVerifier()
    result = verifier.verify("DBMS always uses machine learning.", sample_chunks())

    assert result["unsupported_claims"] == 1
    assert result["claims"][0]["status"] == "UNSUPPORTED"


@patch("src.edurag_x.rag.evidence_verifier.genai.Client")
def test_invalid_evidence_reference_downgrades_claim(mock_client_class):
    mock_client = Mock()
    mock_client_class.return_value = mock_client

    mock_client.models.generate_content.return_value = create_response([
        {
            "claim": "Normalization reduces data redundancy.",
            "status": "SUPPORTED",
            "evidence": [{"source": "fake.pdf", "page": 1}],
            "reason": "Claim appears supported."
        }
    ])

    verifier = EvidenceVerifier()
    result = verifier.verify("Normalization reduces redundancy.", sample_chunks())

    assert result["claims"][0]["original_status"] == "SUPPORTED"
    assert result["claims"][0]["status"] == "UNCERTAIN"
    assert result["claims"][0]["evidence_references_valid"] is False
    assert result["claims_with_invalid_evidence"] == 1


@patch("src.edurag_x.rag.evidence_verifier.genai.Client")
def test_empty_answer_is_rejected(mock_client_class):
    verifier = EvidenceVerifier()

    with pytest.raises(ValueError):
        verifier.verify("", sample_chunks())


@patch("src.edurag_x.rag.evidence_verifier.genai.Client")
def test_empty_retrieved_chunks_return_insufficient_evidence(mock_client_class):
    verifier = EvidenceVerifier()

    result = verifier.verify("What is normalization?", [])

    assert result["verification_status"] == "INSUFFICIENT_EVIDENCE"
    assert result["claims"] == []


@patch("src.edurag_x.rag.evidence_verifier.genai.Client")
def test_invalid_json_returns_verification_failed(mock_client_class):
    mock_client = Mock()
    mock_client_class.return_value = mock_client

    response = Mock()
    response.text = "This is not valid JSON"

    mock_client.models.generate_content.return_value = response

    verifier = EvidenceVerifier()
    result = verifier.verify("Explain normalization.", sample_chunks())

    assert result["verification_status"] == "VERIFICATION_FAILED"
    assert result["claims"] == []
    assert "error" in result
