from src.edurag_x.rag.citation_validator import CitationValidator

validator = CitationValidator()

retrieved_chunks = [
    {"source": "dbms_sample.pdf", "page_number": 1, "text": "Normalization"},
    {"source": "dbms_sample.pdf", "page_number": 2, "text": "Primary Key"},
    {"source": "dbms_sample.pdf", "page_number": 3, "text": "Foreign Key"}
]

test_cases = [
    (
        "Single Page",
        "[Source: dbms_sample.pdf, Page: 1]"
    ),
    (
        "Multiple Pages",
        "[Source: dbms_sample.pdf, Page: 1, Page: 2]"
    ),
    (
        "Page Range",
        "[Source: dbms_sample.pdf, Pages: 1-3]"
    ),
    (
        "Fake Source",
        "[Source: fake.pdf, Page: 5]"
    ),
    (
        "Missing Citation",
        "Database normalization reduces redundancy."
    )
]

print("\n========== CITATION VALIDATOR V2 ==========")

for name, answer in test_cases:

    result = validator.validate(answer, retrieved_chunks)

    print(f"\nTest: {name}")
    print("Total Citations:", result["total_citations"])
    print("Valid:", result["valid_citations"])
    print("Invalid:", result["invalid_citations"])
    print("Missing:", result["missing_citations"])
    print("All Valid:", result["all_valid"])

print("\n========== TEST COMPLETE ==========")
