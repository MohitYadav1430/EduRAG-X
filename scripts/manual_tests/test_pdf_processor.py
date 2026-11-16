from src.edurag_x.ingestion.pdf_processor import PDFProcessor

processor = PDFProcessor()

pdf_path = "data/sample_documents/sample.pdf"

pages = processor.extract_text(pdf_path)

print("\n========== PDF PROCESSING TEST ==========")

for page in pages:
    print(f"\nSource: {page['source']}")
    print(f"Page Number: {page['page_number']}")
    print(f"Extracted Text:\n{page['text']}")

print("\nTotal Pages Extracted:", len(pages))
print("=========================================")
