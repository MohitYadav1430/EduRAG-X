from src.edurag_x.rag.evidence_reference_validator import EvidenceReferenceValidator


validator = EvidenceReferenceValidator()

retrieved_chunks = [
    {
        "source": "dbms_sample.pdf",
        "page_number": 1,
        "text": "Normalization reduces data redundancy."
    },
    {
        "source": "dbms_sample.pdf",
        "page_number": 2,
        "text": "Benefits of normalization."
    }
]

test_cases = [
    {
        "claim": "Correct filename and page",
        "status": "SUPPORTED",
        "evidence": [
            {"source": "dbms_sample.pdf", "page": 1}
        ]
    },
    {
        "claim": "Correct filename but wrong page",
        "status": "SUPPORTED",
        "evidence": [
            {"source": "dbms_sample.pdf", "page": 10}
        ]
    },
    {
        "claim": "Wrong filename",
        "status": "SUPPORTED",
        "evidence": [
            {"source": "fake.pdf", "page": 1}
        ]
    },
    {
        "claim": "Missing evidence",
        "status": "SUPPORTED",
        "evidence": []
    }
]

print("\n========== EVIDENCE REFERENCE VALIDATION ==========")

result = validator.validate(
    claims=test_cases,
    retrieved_chunks=retrieved_chunks
)

for item in result["results"]:

    print("\nClaim:", item["claim"])
    print("Valid:", item["evidence_references_valid"])
    print("Invalid References:", item["invalid_references"])

print("\n========== SUMMARY ==========")
print("Total Claims:", result["total_claims"])
print("Valid Claims:", result["valid_claims"])
print("Invalid Claims:", result["invalid_claims"])

print("\n========== TEST COMPLETE ==========")
