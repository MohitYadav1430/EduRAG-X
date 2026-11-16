from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline
from src.edurag_x.rag.retriever import Retriever
from src.edurag_x.rag.rag_pipeline import RAGPipeline


def main():

    pdf_path = "data/sample_documents/dbms_sample.pdf"
    question = "How can duplicate data in a database be reduced?"

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

    print("\n========== 2. RAG PIPELINE INITIALIZATION ==========")

    retriever = Retriever(
        vector_store=ingestion.vector_store,
        embedding_engine=ingestion.embedding_engine
    )

    rag_pipeline = RAGPipeline(retriever=retriever)

    print("RAG pipeline initialized successfully.")

    print("\n========== 3. QUESTION AND ANSWER ==========")
    print("Question:", question)

    result = rag_pipeline.answer_question(
        question=question,
        top_k=3
    )

    print("\n========== 4. RETRIEVED EVIDENCE ==========")

    for index, chunk in enumerate(result["retrieved_chunks"], start=1):
        print(f"\nChunk {index}")
        print("Source:", chunk["source"])
        print("Page:", chunk["page_number"])
        print("Similarity:", chunk.get("similarity_score"))
        print("Text:", chunk["text"][:300])

    print("\n========== 5. GENERATED ANSWER ==========")
    print(result["answer"])

    print("\n========== 6. CITATION VALIDATION ==========")

    citation = result["citation_validation"]

    print("Total citations:", citation["total_citations"])
    print("Valid citations:", citation["valid_citations"])
    print("Invalid citations:", citation["invalid_citations"])
    print("All citations valid:", citation["all_valid"])

    print("\n========== 7. EVIDENCE VERIFICATION ==========")

    verification = result["evidence_verification"]

    print("Verification status:", verification["verification_status"])
    print("Total claims:", verification.get("total_claims", 0))
    print("Supported claims:", verification.get("supported_claims", 0))
    print("Unsupported claims:", verification.get("unsupported_claims", 0))
    print("Uncertain claims:", verification.get("uncertain_claims", 0))
    print(
        "Invalid evidence references:",
        verification.get("invalid_evidence_references", 0)
    )

    for index, claim in enumerate(verification.get("claims", []), start=1):
        print(f"\nClaim {index}:", claim.get("claim"))
        print("Status:", claim.get("status"))
        print("Reason:", claim.get("reason"))

    print("\n========== END-TO-END TEST COMPLETE ==========")


if __name__ == "__main__":
    main()
