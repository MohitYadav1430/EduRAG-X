from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline
from src.edurag_x.rag.retriever import Retriever
from src.edurag_x.rag.rag_pipeline import RAGPipeline


def main():

    pdf_path = "data/sample_documents/dbms_sample.pdf"
    question = "Explain ACID properties in DBMS."

    print("\n========== 1. DOCUMENT INGESTION ==========")

    ingestion = DocumentIngestionPipeline()
    ingestion_result = ingestion.ingest_pdf(pdf_path)

    print("Document:", ingestion_result["source"])
    print("Pages:", ingestion_result["pages"])
    print("Chunks:", ingestion_result["chunks"])
    print("Vectors stored:", ingestion_result["vectors_stored"])

    if ingestion_result["vectors_stored"] == 0:
        print("ERROR: No document vectors were stored.")
        return

    retriever = Retriever(
        vector_store=ingestion.vector_store,
        embedding_engine=ingestion.embedding_engine
    )

    rag_pipeline = RAGPipeline(retriever=retriever)

    print("\n========== 2. UNSUPPORTED QUESTION ==========")
    print("Student Question:", question)

    result = rag_pipeline.answer_question(
        question,
        top_k=3
    )

    print("\n========== 3. RETRIEVED DOCUMENTS ==========")

    for index, chunk in enumerate(result["retrieved_chunks"], start=1):
        print(f"\nChunk {index}")
        print("Source:", chunk["source"])
        print("Page:", chunk["page_number"])
        print("Similarity:", round(chunk["similarity_score"], 4))

    print("\n========== 4. AI RESPONSE ==========")
    print(result["answer"])

    print("\n========== 5. CITATION VALIDATION ==========")

    citation = result["citation_validation"]

    print("Total citations:", citation["total_citations"])
    print("Valid citations:", citation["valid_citations"])
    print("Invalid citations:", citation["invalid_citations"])
    print("All citations valid:", citation["all_valid"])

    print("\n========== 6. EVIDENCE VERIFICATION ==========")

    verification = result["evidence_verification"]

    print("Verification status:", verification["verification_status"])
    print("Total claims:", verification.get("total_claims", 0))
    print("Supported claims:", verification.get("supported_claims", 0))
    print("Unsupported claims:", verification.get("unsupported_claims", 0))
    print("Uncertain claims:", verification.get("uncertain_claims", 0))

    for index, claim in enumerate(verification.get("claims", []), start=1):
        print(f"\nClaim {index}:", claim.get("claim"))
        print("Status:", claim.get("status"))
        print("Reason:", claim.get("reason"))

    print("\n========== UNSUPPORTED QUESTION TEST COMPLETE ==========")


if __name__ == "__main__":
    main()
