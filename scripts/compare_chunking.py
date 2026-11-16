from pathlib import Path

from src.edurag_x.ingestion.pdf_processor import PDFProcessor
from src.edurag_x.ingestion.text_chunker import TextChunker
from src.edurag_x.ingestion.sentence_chunker import SentenceAwareChunker


def compare_chunking():

    pdf_processor = PDFProcessor()

    fixed_chunker = TextChunker(
        chunk_size=800,
        chunk_overlap=150
    )

    sentence_chunker = SentenceAwareChunker(
        chunk_size=800,
        chunk_overlap=150
    )

    pdf_files = [
        Path("data/sample_documents/dbms_sample.pdf"),
        Path("data/sample_documents/dbms_transactions_sample.pdf")
    ]

    for pdf_path in pdf_files:

        print("\n" + "=" * 70)
        print(f"PDF: {pdf_path.name}")
        print("=" * 70)

        pages = pdf_processor.extract_text(pdf_path)

        fixed_chunks = fixed_chunker.split_text(pages)
        sentence_chunks = sentence_chunker.split_text(pages)

        print("\nFIXED-SIZE CHUNKING")
        print("-" * 40)
        print(f"Total chunks: {len(fixed_chunks)}")

        print("\nSENTENCE-AWARE CHUNKING")
        print("-" * 40)
        print(f"Total chunks: {len(sentence_chunks)}")

        print("\nDETAILED COMPARISON")
        print("-" * 40)

        for method_name, chunks in [
            ("Fixed-Size", fixed_chunks),
            ("Sentence-Aware", sentence_chunks)
        ]:

            lengths = [len(chunk["text"]) for chunk in chunks]

            if lengths:
                average_length = sum(lengths) / len(lengths)
                maximum_length = max(lengths)
            else:
                average_length = 0
                maximum_length = 0

            print(f"\n{method_name}:")
            print(f"  Total chunks: {len(chunks)}")
            print(f"  Average chunk length: {average_length:.2f}")
            print(f"  Maximum chunk length: {maximum_length}")

        print("\nFIRST CHUNK EXAMPLES")
        print("-" * 40)

        if fixed_chunks:
            print("\nFixed-Size:")
            print(fixed_chunks[0]["text"])

        if sentence_chunks:
            print("\nSentence-Aware:")
            print(sentence_chunks[0]["text"])


if __name__ == "__main__":
    compare_chunking()