from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline
from src.edurag_x.rag.retriever import Retriever

# Initialize document pipeline
pipeline = DocumentIngestionPipeline()

# Ingest DBMS PDF
pdf_path = "data/sample_documents/dbms_sample.pdf"

print("\n========== DOCUMENT INGESTION ==========")

result = pipeline.ingest_pdf(pdf_path)

print("Source:", result["source"])
print("Pages:", result["pages"])
print("Chunks:", result["chunks"])
print("Vectors Stored:", result["vectors_stored"])

# Initialize retriever using the same vector store
retriever = Retriever(
    vector_store=pipeline.vector_store,
    embedding_engine=pipeline.embedding_engine
)

# Ask a semantic question
question = "How can duplicate data in a database be reduced?"

print("\n========== SEMANTIC RETRIEVAL ==========")
print("Student Question:", question)

results = retriever.retrieve(
    query=question,
    top_k=3
)

for result in results:
    print("\n----------------------------------------")
    print("Chunk ID:", result["chunk_id"])
    print("Source:", result["source"])
    print("Page Number:", result["page_number"])
    print("Similarity Score:", round(result["similarity_score"], 4))
    print("Retrieved Text:", result["text"])

print("\nTotal Retrieved Results:", len(results))
print("SEMANTIC RETRIEVAL: SUCCESS")
print("========================================")
