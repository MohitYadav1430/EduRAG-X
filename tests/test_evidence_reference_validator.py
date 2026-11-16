from src.edurag_x.rag.evidence_reference_validator import EvidenceReferenceValidator


def get_validator():
    return EvidenceReferenceValidator()


def get_documents():
    return [
        {
            "source": "dbms_sample.pdf",
            "page_number": 1,
            "text": "Normalization reduces data redundancy."
        },
        {
            "source": "dbms_sample.pdf",
            "page_number": 2,
            "text": "Normalization improves data consistency."
        }
    ]


def test_valid_evidence_reference():

    validator = get_validator()

    claims = [{
        "claim": "Normalization reduces data redundancy.",
        "status": "SUPPORTED",
        "evidence": [
            {"source": "dbms_sample.pdf", "page": 1}
        ]
    }]

    result = validator.validate(claims, get_documents())

    assert result["valid_claims"] == 1
    assert result["invalid_claims"] == 0
    assert result["results"][0]["final_status"] == "SUPPORTED"


def test_fake_filename_rejected():

    validator = get_validator()

    claims = [{
        "claim": "Test claim",
        "status": "SUPPORTED",
        "evidence": [
            {"source": "fake.pdf", "page": 1}
        ]
    }]

    result = validator.validate(claims, get_documents())

    assert result["invalid_claims"] == 1
    assert result["results"][0]["final_status"] == "UNCERTAIN"


def test_nonexistent_page_rejected():

    validator = get_validator()

    claims = [{
        "claim": "Test claim",
        "status": "SUPPORTED",
        "evidence": [
            {"source": "dbms_sample.pdf", "page": 10}
        ]
    }]

    result = validator.validate(claims, get_documents())

    assert result["invalid_claims"] == 1
    assert result["results"][0]["final_status"] == "UNCERTAIN"


def test_missing_evidence_rejected():

    validator = get_validator()

    claims = [{
        "claim": "Test claim",
        "status": "SUPPORTED",
        "evidence": []
    }]

    result = validator.validate(claims, get_documents())

    assert result["invalid_claims"] == 1
    assert result["results"][0]["final_status"] == "UNCERTAIN"


def test_unsupported_claim_remains_unsupported():

    validator = get_validator()

    claims = [{
        "claim": "Primary keys eliminate all duplicate data.",
        "status": "UNSUPPORTED",
        "evidence": []
    }]

    result = validator.validate(claims, get_documents())

    assert result["results"][0]["original_status"] == "UNSUPPORTED"
    assert result["results"][0]["final_status"] == "UNSUPPORTED"


