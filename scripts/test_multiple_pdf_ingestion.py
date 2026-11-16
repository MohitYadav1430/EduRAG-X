from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline

pipeline = DocumentIngestionPipeline()

pdf_files = [
    "data/sample_documents/dbms_sample.pdf",
    "data/sample_documents/dbms_transactions_sample.pdf"
]

print("\n========== MULTIPLE PDF INGESTION ==========")

total_pages = 0
total_chunks = 0
total_vectors = 0

for pdf_path in pdf_files:

    result = pipeline.ingest_pdf(pdf_path)

    print("\nDocument:", result["source"])
    print("Pages:", result["pages"])
    print("Chunks:", result["chunks"])
    print("Vectors stored:", result["vectors_stored"])

    total_pages += result["pages"]
    total_chunks += result["chunks"]
    total_vectors += result["vectors_stored"]

print("\n========== FINAL SUMMARY ==========")
print("Total PDFs:", len(pdf_files))
print("Total Pages:", total_pages)
print("Total Chunks:", total_chunks)
print("Total Vectors:", total_vectors)
print("All documents ingested successfully!")
