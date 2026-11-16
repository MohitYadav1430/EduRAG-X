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
        "text": "Normalization improves data consistency."
    }
]

claims = [
    {
        "claim": "Normalization reduces data redundancy.",
        "status": "SUPPORTED",
        "evidence": [
            {"source": "dbms_sample.pdf", "page": 1}
        ]
    },
    {
        "claim": "Normalization improves data redundancy.",
        "status": "SUPPORTED",
        "evidence": [
            {"source": "fake.pdf", "page": 10}
        ]
    },
    {
        "claim": "Primary keys eliminate all duplicate data.",
        "status": "UNSUPPORTED",
        "evidence": []
    }
]

result = validator.validate(claims, retrieved_chunks)

print("\n========== AUTOMATIC DOWNGRADING TEST ==========")

for item in result["results"]:

    print("\nClaim:", item["claim"])
    print("Original Status:", item["original_status"])
    print("Final Status:", item["final_status"])
    print("Evidence Valid:", item["evidence_references_valid"])
    print("Invalid References:", item["invalid_references"])

print("\n========== SUMMARY ==========")
print("Total Claims:", result["total_claims"])
print("Valid Claims:", result["valid_claims"])
print("Invalid Claims:", result["invalid_claims"])
print("Downgraded Claims:", result["downgraded_claims"])

print("\n========== TEST COMPLETE ==========")
