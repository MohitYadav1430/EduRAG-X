from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline
from src.edurag_x.rag.retriever import Retriever


# Step 1: Create ingestion pipeline
pipeline = DocumentIngestionPipeline()

pdf_files = [
    "data/sample_documents/dbms_sample.pdf",
    "data/sample_documents/dbms_transactions_sample.pdf"
]

print("\n========== DOCUMENT INGESTION ==========")

for pdf_path in pdf_files:
    result = pipeline.ingest_pdf(pdf_path)

    print(f"\nDocument: {result['source']}")
    print(f"Pages: {result['pages']}")
    print(f"Chunks: {result['chunks']}")

# Step 2: Check actual vector count
print("\nTotal vectors in FAISS:", pipeline.vector_store.total_vectors())

# Step 3: Create retriever using the same vector store and embedding engine
retriever = Retriever(
    vector_store=pipeline.vector_store,
    embedding_engine=pipeline.embedding_engine
)

# Step 4: Test queries
test_questions = [
    "What are the ACID properties of a database transaction?",
    "What is database normalization?"
]

print("\n========== MULTIPLE PDF RETRIEVAL ==========")

for question in test_questions:

    print("\nQuestion:", question)

    results = retriever.retrieve(question, top_k=3)

    for rank, result in enumerate(results, start=1):

        print(f"\nResult {rank}")
        print("Source:", result.get("source"))
        print("Page:", result.get("page_number"))
        print("Similarity Score:", result.get("similarity_score"))
        print("Text:", result.get("text", "")[:300])

print("\n========== RETRIEVAL TEST COMPLETED ==========")
