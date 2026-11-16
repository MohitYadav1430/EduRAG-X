from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline

pipeline = DocumentIngestionPipeline()

pdf_path = "data/sample_documents/sample.pdf"

print("\n========== DOCUMENT PIPELINE TEST ==========")

result = pipeline.ingest_pdf(pdf_path)

print("\nIngestion Result:")
print("Source:", result["source"])
print("Pages Processed:", result["pages"])
print("Chunks Created:", result["chunks"])
print("Vectors Stored:", result["vectors_stored"])

print("\nTotal Vectors in FAISS:", pipeline.vector_store.total_vectors())

print("\nDOCUMENT INGESTION: SUCCESS")
print("============================================")
