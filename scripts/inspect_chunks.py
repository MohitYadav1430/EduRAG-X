from pathlib import Path

from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_FILES = [
    PROJECT_ROOT / "data" / "sample_documents" / "dbms_sample.pdf",
    PROJECT_ROOT / "data" / "sample_documents" / "dbms_transactions_sample.pdf"
]


def main():

    pipeline = DocumentIngestionPipeline()

    print("\n========== CHUNK INSPECTION ==========")

    total_chunks = 0

    for pdf_path in PDF_FILES:

        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)

        extracted_pages = pipeline.pdf_processor.extract_text(pdf_path)

        chunks = pipeline.text_chunker.split_text(extracted_pages)

        print(f"\nDocument: {pdf_path.name}")
        print(f"Total chunks: {len(chunks)}")

        for chunk in chunks:

            total_chunks += 1

            print("\n-----------------------------------")
            print(f"Chunk ID: {chunk['chunk_id']}")
            print(f"Source: {chunk['source']}")
            print(f"Page: {chunk['page_number']}")
            print(f"Characters: {len(chunk['text'])}")
            print("\nChunk Text:")
            print(chunk["text"])

    print("\n========== SUMMARY ==========")
    print("Total chunks across documents:", total_chunks)


if __name__ == "__main__":
    main()

