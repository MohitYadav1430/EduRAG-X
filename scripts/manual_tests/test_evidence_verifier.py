from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline
from src.edurag_x.rag.evidence_verifier import EvidenceVerifier
from src.edurag_x.rag.retriever import Retriever


print("\n========== DOCUMENT INGESTION ==========")

pipeline = DocumentIngestionPipeline()

result = pipeline.ingest_pdf(
    "data/sample_documents/dbms_sample.pdf"
)

print("Document:", result["source"])
print("Pages:", result["pages"])
print("Chunks:", result["chunks"])


print("\n========== EVIDENCE RETRIEVAL ==========")

retriever = Retriever(pipeline.vector_store)

retrieved_chunks = retriever.retrieve(
    "Database normalization and primary keys",
    top_k=4
)

print("Retrieved Chunks:", len(retrieved_chunks))


answer = """
1. Normalization reduces data redundancy.
2. Primary keys eliminate all duplicate data from a database.
"""

verifier = EvidenceVerifier()

result = verifier.verify(
    answer=answer,
    retrieved_chunks=retrieved_chunks
)


print("\n========== VERIFICATION RESULTS ==========")

print("Status:", result["verification_status"])
if result.get("error"):
    print("ERROR DETAILS:", result["error"])

print("Total Claims:", result.get("total_claims", 0))
print("Supported:", result.get("supported_claims", 0))
print("Unsupported:", result.get("unsupported_claims", 0))
print("Uncertain:", result.get("uncertain_claims", 0))

print(
    "Invalid Evidence References:",
    result.get("invalid_evidence_references", 0)
)


for index, claim in enumerate(result.get("claims", []), start=1):

    print(f"\nClaim {index}: {claim.get('claim')}")
    print("Classification:", claim.get("status"))
    print("Evidence:", claim.get("evidence"))

    print(
        "Evidence References Valid:",
        claim.get("evidence_references_valid")
    )

    print(
        "Invalid References:",
        claim.get("invalid_evidence_references")
    )

    print("Reason:", claim.get("reason"))


print("\n========== TEST COMPLETE ==========")

