from src.edurag_x.rag.citation_validator import CitationValidator

validator = CitationValidator()

retrieved_chunks = [
    {
        "source": "dbms_sample.pdf",
        "page_number": 1,
        "text": "Database normalization reduces data redundancy."
    },
    {
        "source": "dbms_sample.pdf",
        "page_number": 2,
        "text": "Normalization improves data consistency."
    }
]

answer = """
Database normalization reduces data redundancy.
[Source: dbms_sample.pdf, Page: 1]

Normalization improves data consistency.
[Source: dbms_sample.pdf, Page: 2]

This additional claim is unsupported.
[Source: fake.pdf, Page: 5]
"""

result = validator.validate(answer, retrieved_chunks)

print("\n========== CITATION VALIDATION TEST ==========")
print("Total Citations:", result["total_citations"])
print("Valid Citations:", result["valid_citations"])
print("Invalid Citations:", result["invalid_citations"])

for citation in result["citations"]:
    print("\nSource:", citation["source"])
    print("Pages:", citation["pages"])
    print("Valid:", citation["valid"])

print("\nAll Citations Valid:", result["all_valid"])
print("==============================================")
