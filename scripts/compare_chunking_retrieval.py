import csv
from pathlib import Path

from src.edurag_x.ingestion.pdf_processor import PDFProcessor
from src.edurag_x.ingestion.text_chunker import TextChunker
from src.edurag_x.ingestion.sentence_chunker import SentenceAwareChunker


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_FILES = [
    PROJECT_ROOT / "data" / "sample_documents" / "dbms_sample.pdf",
    PROJECT_ROOT / "data" / "sample_documents" / "dbms_transactions_sample.pdf"
]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "docs"
    / "chunking_comparison_inventory.csv"
)


def main():

    print("\n========== CHUNKING COMPARISON INVENTORY ==========")

    pdf_processor = PDFProcessor()

    chunkers = {
        "fixed_size": TextChunker(
            chunk_size=800,
            chunk_overlap=150
        ),
        "sentence_aware": SentenceAwareChunker(
            chunk_size=800,
            chunk_overlap=150
        )
    }

    inventory_rows = []

    for pdf_path in PDF_FILES:

        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)

        pages = pdf_processor.extract_text(pdf_path)

        print(f"\nPDF: {pdf_path.name}")

        for method_name, chunker in chunkers.items():

            chunks = chunker.split_text(pages)

            print(
                f"{method_name}: {len(chunks)} chunks"
            )

            for chunk in chunks:

                inventory_rows.append({
                    "method": method_name,
                    "source": chunk["source"],
                    "chunk_id": chunk["chunk_id"],
                    "page_number": chunk["page_number"],
                    "chunk_length": len(chunk["text"]),
                    "text": chunk["text"]
                })

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        fieldnames = [
            "method",
            "source",
            "chunk_id",
            "page_number",
            "chunk_length",
            "text"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(inventory_rows)

    print("\n========== COMPLETED ==========")

    print("Total inventory records:", len(inventory_rows))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()