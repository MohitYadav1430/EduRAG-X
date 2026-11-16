import csv
import tempfile
import time
from pathlib import Path

from src.edurag_x.ingestion.document_pipeline import (
    DocumentIngestionPipeline
)

from src.edurag_x.rag.retriever import Retriever
from src.edurag_x.rag.keyword_retriever import KeywordRetriever
from src.edurag_x.rag.hybrid_retriever import HybridRetriever


PROJECT_ROOT = Path(__file__).resolve().parent.parent

GROUND_TRUTH_FILE = (
    PROJECT_ROOT / "docs" / "chunk_level_ground_truth.csv"
)

PDF_FILES = [
    PROJECT_ROOT / "data" / "sample_documents" / "dbms_sample.pdf",
    PROJECT_ROOT / "data" / "sample_documents" / "dbms_transactions_sample.pdf"
]

TOP_K = 3
RRF_K = 60


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
        if expected_chunks
        else 0.0
    )

    reciprocal_rank = 0.0

    for rank, chunk_id in enumerate(retrieved_ids, start=1):

        if chunk_id in expected_chunks:
            reciprocal_rank = 1 / rank
            break

    return precision, recall, reciprocal_rank


def evaluate_retriever(
    retriever,
    method_name,
    test_cases,
    output_rows
):

    print(f"\n========== {method_name.upper()} EVALUATION ==========")

    retrieval_times = []

    for case in test_cases:

        query = case["query"]
        query_type = case["query_type"]

        expected_chunks = {
            chunk.strip()
            for chunk in case["expected_relevant_chunks"].split(";")
            if chunk.strip()
        }

        start_time = time.perf_counter()

        results = retriever.retrieve(
            query,
            top_k=TOP_K
        )

        elapsed_time = time.perf_counter() - start_time

        retrieval_times.append(elapsed_time)

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

            "mrr": (
                round(mrr, 4)
                if mrr != "" else ""
            ),

            "retrieval_time_seconds": round(elapsed_time, 4),

            "no_chunks_retrieved": no_chunks_retrieved,

            "retrieved_chunk_ids": "; ".join(retrieved_ids)
        })

        print("\nQuery:", query)
        print("Retrieved chunks:", retrieved_ids)
        print("Retrieval time:", round(elapsed_time, 4), "seconds")

        if query_type == "relevant":

            print("Precision@3:", precision)
            print("Recall@3:", recall)
            print("MRR:", mrr)

        else:

            print("Unrelated query retrieved chunks:", len(results))

    average_time = (
        sum(retrieval_times) / len(retrieval_times)
        if retrieval_times else 0.0
    )

    print(
        f"\nAverage retrieval time ({method_name}):",
        round(average_time, 4),
        "seconds"
    )


def main():

    print("\n========== HYBRID RETRIEVAL EVALUATION ==========")

    with open(
        GROUND_TRUTH_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        test_cases = list(csv.DictReader(file))

    if not test_cases:
        raise ValueError("Ground truth dataset is empty.")

    output_rows = []

    with tempfile.TemporaryDirectory() as temp_dir:

        pipeline = DocumentIngestionPipeline(
            storage_dir=temp_dir
        )

        print("\n========== DOCUMENT INGESTION ==========")

        for pdf_path in PDF_FILES:

            if not pdf_path.exists():
                raise FileNotFoundError(pdf_path)

            result = pipeline.ingest_pdf(pdf_path)

            print(
                f"{result['source']}: "
                f"{result['chunks']} chunks"
            )

        vector_store = pipeline.vector_store

        print(
            "\nTotal indexed chunks:",
            vector_store.total_vectors()
        )

        semantic_retriever = Retriever(
            vector_store=vector_store,
            embedding_engine=pipeline.embedding_engine
        )

        keyword_retriever = KeywordRetriever(
            vector_store=vector_store
        )

        hybrid_retriever = HybridRetriever(
            semantic_retriever=semantic_retriever,
            keyword_retriever=keyword_retriever,
            rrf_k=RRF_K
        )

        evaluate_retriever(
            semantic_retriever,
            "Semantic",
            test_cases,
            output_rows
        )

        evaluate_retriever(
            keyword_retriever,
            "BM25",
            test_cases,
            output_rows
        )

        evaluate_retriever(
            hybrid_retriever,
            "Hybrid",
            test_cases,
            output_rows
        )

        output_file = (
            PROJECT_ROOT
            / "docs"
            / "hybrid_retrieval_evaluation_results.csv"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=output_rows[0].keys()
            )

            writer.writeheader()
            writer.writerows(output_rows)

        print("\n========== EVALUATION COMPLETED ==========")

        print("Total evaluation records:", len(output_rows))

        print("Results saved to:", output_file)


if __name__ == "__main__":
    main()