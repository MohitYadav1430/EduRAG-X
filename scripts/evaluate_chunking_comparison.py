import csv
from pathlib import Path

from src.edurag_x.ingestion.pdf_processor import PDFProcessor
from src.edurag_x.ingestion.text_chunker import TextChunker
from src.edurag_x.ingestion.sentence_chunker import SentenceAwareChunker
from src.edurag_x.llm.embedding_engine import EmbeddingEngine
from src.edurag_x.rag.vector_store import VectorStore


PROJECT_ROOT = Path(__file__).resolve().parent.parent

GROUND_TRUTH_FILE = (
    PROJECT_ROOT / "docs" / "chunking_comparison_ground_truth.csv"
)

PDF_FILES = [
    PROJECT_ROOT / "data" / "sample_documents" / "dbms_sample.pdf",
    PROJECT_ROOT / "data" / "sample_documents" / "dbms_transactions_sample.pdf"
]

TOP_K = 3

CHUNKERS = {
    "fixed_size": TextChunker(
        chunk_size=800,
        chunk_overlap=150
    ),
    "sentence_aware": SentenceAwareChunker(
        chunk_size=800,
        chunk_overlap=150
    )
}


def calculate_metrics(results, expected_chunks):

    retrieved_ids = [
        f"{result['source']}:{result['chunk_id']}"
        for result in results
    ]

    relevant_count = sum(
        1 for chunk_id in retrieved_ids
        if chunk_id in expected_chunks
    )

    precision = relevant_count / TOP_K

    recall = (
        relevant_count / len(expected_chunks)
        if expected_chunks else 0.0
    )

    reciprocal_rank = 0.0

    for rank, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in expected_chunks:
            reciprocal_rank = 1 / rank
            break

    return precision, recall, reciprocal_rank


def load_ground_truth():

    with open(
        GROUND_TRUTH_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        return list(csv.DictReader(file))


def build_vector_store(chunker, pdf_processor, embedding_engine):

    vector_store = VectorStore()

    for pdf_path in PDF_FILES:

        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)

        pages = pdf_processor.extract_text(pdf_path)

        chunks = chunker.split_text(pages)

        if not chunks:
            continue

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = embedding_engine.embed_documents(texts)

        vector_store.add_documents(
            chunks,
            embeddings
        )

    return vector_store


def main():

    print("\n========== CHUNKING RETRIEVAL COMPARISON ==========")

    test_cases = load_ground_truth()

    if not test_cases:
        raise ValueError("Ground truth dataset is empty.")

    pdf_processor = PDFProcessor()
    embedding_engine = EmbeddingEngine()

    vector_stores = {}

    # Build a separate vector store for each chunking method.
    for method_name, chunker in CHUNKERS.items():

        print(f"\nBuilding vector store: {method_name}")

        vector_store = build_vector_store(
            chunker,
            pdf_processor,
            embedding_engine
        )

        vector_stores[method_name] = vector_store

        print(
            "Indexed chunks:",
            vector_store.total_vectors()
        )

    # Generate each query embedding only once.
    print("\nGenerating query embeddings...")

    query_embeddings = {}

    for case in test_cases:

        query = case["query"]

        query_embeddings[query] = (
            embedding_engine.embed_query(query)
        )

    output_rows = []

    print("\n========== EVALUATION ==========")

    for case in test_cases:

        query = case["query"]
        query_type = case["query_type"]

        print("\nQuery:", query)

        for method_name, vector_store in vector_stores.items():

            expected_field = (
                "fixed_expected_chunks"
                if method_name == "fixed_size"
                else "sentence_expected_chunks"
            )

            expected_chunks = {
                chunk.strip()
                for chunk in case[expected_field].split(";")
                if chunk.strip()
            }

            results = vector_store.search(
                query_embeddings[query],
                top_k=TOP_K
            )

            retrieved_ids = [
                f"{result['source']}:{result['chunk_id']}"
                for result in results
            ]

            if query_type == "relevant":

                precision, recall, mrr = calculate_metrics(
                    results,
                    expected_chunks
                )

            else:

                precision = ""
                recall = ""
                mrr = ""

            no_chunks_retrieved = len(results) == 0

            output_rows.append({

                "method": method_name,
                "query": query,
                "query_type": query_type,
                "retrieved_chunks": len(results),

                "precision_at_3": (
                    round(precision, 4)
                    if precision != "" else ""
                ),

                "recall_at_3": (
                    round(recall, 4)
                    if recall != "" else ""
                ),

                "reciprocal_rank": (
                    round(mrr, 4)
                    if mrr != "" else ""
                ),

                "no_chunks_retrieved": no_chunks_retrieved,

                "retrieved_chunk_ids": "; ".join(retrieved_ids)
            })

            print(f"\nMethod: {method_name}")
            print("Retrieved:", retrieved_ids)
            print("Precision@3:", precision)
            print("Recall@3:", recall)
            print("MRR:", mrr)

    output_file = (
        PROJECT_ROOT
        / "docs"
        / "chunking_retrieval_comparison_results.csv"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=output_rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(output_rows)

    print("\n========== COMPLETED ==========")
    print("Total evaluation records:", len(output_rows))
    print("Results saved to:", output_file)


if __name__ == "__main__":
    main()