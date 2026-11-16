from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline
from src.edurag_x.rag.retriever import Retriever
from src.edurag_x.rag.rag_pipeline import RAGPipeline


# Step 1: Ingest both PDF documents
ingestion_pipeline = DocumentIngestionPipeline()

pdf_files = [
    "data/sample_documents/dbms_sample.pdf",
    "data/sample_documents/dbms_transactions_sample.pdf"
]

print("\n========== DOCUMENT INGESTION ==========")

for pdf_path in pdf_files:
    result = ingestion_pipeline.ingest_pdf(pdf_path)

    print(
        f"{result['source']} | "
        f"Pages: {result['pages']} | "
        f"Chunks: {result['chunks']}"
    )


# Step 2: Initialize RAG pipeline
retriever = Retriever(
    vector_store=ingestion_pipeline.vector_store,
    embedding_engine=ingestion_pipeline.embedding_engine
)

rag_pipeline = RAGPipeline(retriever=retriever)


# Step 3: Ask an unrelated question
question = "Explain the process of photosynthesis in plants."

print("\n========== UNRELATED QUESTION TEST ==========")
print("\nQuestion:", question)


# Step 4: Execute RAG pipeline
result = rag_pipeline.answer_question(
    question,
    top_k=5
)


# Step 5: Display retrieved evidence
print("\n========== RETRIEVED DOCUMENTS ==========")

for rank, chunk in enumerate(result["retrieved_chunks"], start=1):
    print(f"\nResult {rank}")
    print("Source:", chunk.get("source"))
    print("Page:", chunk.get("page_number"))
    print("Similarity:", chunk.get("similarity_score"))


# Step 6: Display generated answer
print("\n========== GENERATED ANSWER ==========")
print(result["answer"])


# Step 7: Display citation validation
print("\n========== CITATION VALIDATION ==========")
print(result["citation_validation"])


# Step 8: Display evidence verification
print("\n========== EVIDENCE VERIFICATION ==========")
print(result["evidence_verification"])


print("\n========== TEST COMPLETED ==========")
