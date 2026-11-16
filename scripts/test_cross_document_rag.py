from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline
from src.edurag_x.rag.retriever import Retriever
from src.edurag_x.rag.rag_pipeline import RAGPipeline


# Step 1: Initialize ingestion pipeline
ingestion_pipeline = DocumentIngestionPipeline()

pdf_files = [
    "data/sample_documents/dbms_sample.pdf",
    "data/sample_documents/dbms_transactions_sample.pdf"
]

print("\n========== INGESTING MULTIPLE DOCUMENTS ==========")

for pdf_path in pdf_files:
    result = ingestion_pipeline.ingest_pdf(pdf_path)

    print("\nDocument:", result["source"])
    print("Pages:", result["pages"])
    print("Chunks:", result["chunks"])

print("\nTotal vectors stored:",
      ingestion_pipeline.vector_store.total_vectors())


# Step 2: Initialize retriever
retriever = Retriever(
    vector_store=ingestion_pipeline.vector_store,
    embedding_engine=ingestion_pipeline.embedding_engine
)


# Step 3: Initialize complete RAG pipeline
rag_pipeline = RAGPipeline(retriever=retriever)


# Step 4: Ask a question requiring both documents
question = (
    "Explain database normalization and ACID properties. "
    "How do they contribute to database reliability?"
)

print("\n========== CROSS-DOCUMENT RAG TEST ==========")
print("\nQuestion:", question)


# Step 5: Generate answer and verify evidence
result = rag_pipeline.answer_question(
    question,
    top_k=5
)


# Step 6: Display retrieved documents
print("\n========== RETRIEVED EVIDENCE ==========")

for rank, chunk in enumerate(result["retrieved_chunks"], start=1):
    print(f"\nResult {rank}")
    print("Source:", chunk.get("source"))
    print("Page:", chunk.get("page_number"))
    print("Similarity:", chunk.get("similarity_score"))
    print("Text:", chunk.get("text", "")[:250])


# Step 7: Display generated answer
print("\n========== GENERATED ANSWER ==========")
print(result["answer"])


# Step 8: Display citation validation
print("\n========== CITATION VALIDATION ==========")
print(result["citation_validation"])


# Step 9: Display evidence verification
print("\n========== EVIDENCE VERIFICATION ==========")
print(result["evidence_verification"])


print("\n========== CROSS-DOCUMENT TEST COMPLETED ==========")
