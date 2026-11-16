import csv
import tempfile
from pathlib import Path

from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline
from src.edurag_x.rag.retriever import Retriever


PROJECT_ROOT = Path(__file__).resolve().parent.parent

GROUND_TRUTH_FILE = (
    PROJECT_ROOT / "docs" / "chunk_level_ground_truth.csv"
)

PDF_FILES = [
    PROJECT_ROOT / "data" / "sample_documents" / "dbms_sample.pdf",
    PROJECT_ROOT / "data" / "sample_documents" / "dbms_transactions_sample.pdf"
]

TOP_K = 3

THRESHOLDS = [None, 0.50, 0.60, 0.70]


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


def main():

    print("\n========== CHUNK-LEVEL THRESHOLD EVALUATION ==========")

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

        retriever = Retriever(
            vector_store=vector_store,
            embedding_engine=pipeline.embedding_engine
        )

        available_chunks = {
            f"{document['source']}:{document['chunk_id']}"
            for document in vector_store.documents
        }

        print("\n========== QUERY EVALUATION ==========")

        for case in test_cases:

            query = case["query"]
            query_type = case["query_type"]

            expected_chunks = {
                chunk.strip()
                for chunk in case["expected_relevant_chunks"].split(";")
                if chunk.strip()
            }

            if query_type == "relevant":

                missing_chunks = expected_chunks - available_chunks

                if not expected_chunks:
                    raise ValueError(
                        f"Relevant query has no expected chunks: {query}"
                    )

                if missing_chunks:
                    raise ValueError(
                        f"Expected chunks not indexed: {missing_chunks}"
                    )

            elif query_type == "unrelated":

                if expected_chunks:
                    raise ValueError(
                        f"Unrelated query should not have expected chunks: {query}"
                    )

            else:
                raise ValueError(
                    f"Unknown query type: {query_type}"
                )

            print("\nQuestion:", query)

            # Generate query embedding and retrieve all indexed chunks once.
            base_results = retriever.retrieve(
                query,
                top_k=vector_store.total_vectors()
            )

            # Apply each threshold locally to avoid repeated API calls.
            for threshold in THRESHOLDS:

                threshold_name = (
                    "None" if threshold is None else str(threshold)
                )

                if threshold is None:

                    filtered_results = base_results

                else:

                    filtered_results = [
                        result for result in base_results
                        if result.get("similarity_score", -1) >= threshold
                    ]

                # Keep only the top K chunks after threshold filtering.
                results = filtered_results[:TOP_K]

                retrieved_ids = [
                    f"{result['source']}:{result['chunk_id']}"
                    for result in results
                ]

                if query_type == "relevant":

                    precision, recall, mrr = calculate_metrics(
                        results,
                        expected_chunks
                    )

                    abstained = ""

                else:

                    precision = ""
                    recall = ""
                    mrr = ""

                    abstained = len(results) == 0

                output_rows.append({

                    "query": query,
                    "query_type": query_type,
                    "threshold": threshold_name,
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

                    "no_chunks_after_threshold": abstained,

                    "retrieved_chunk_ids": "; ".join(retrieved_ids)
                })

                print(
                    f"Threshold: {threshold_name} | "
                    f"Chunks: {len(results)} | "
                    f"Precision@3: {precision} | "
                    f"Recall@3: {recall} | "
                    f"RR: {mrr} | "
                    f"No chunks after threshold: {abstained}"
                )

        print("\n========== AGGREGATE METRICS ==========")

        for threshold in THRESHOLDS:

            threshold_name = (
                "None" if threshold is None else str(threshold)
            )

            relevant_rows = [
                row for row in output_rows
                if row["query_type"] == "relevant"
                and row["threshold"] == threshold_name
            ]

            if not relevant_rows:
                continue

            average_precision = sum(
                row["precision_at_3"]
                for row in relevant_rows
            ) / len(relevant_rows)

            average_recall = sum(
                row["recall_at_3"]
                for row in relevant_rows
            ) / len(relevant_rows)

            mean_reciprocal_rank = sum(
                row["reciprocal_rank"]
                for row in relevant_rows
            ) / len(relevant_rows)

            print(
                f"\nThreshold: {threshold_name}"
                f"\nMean Precision@3: {average_precision:.4f}"
                f"\nMean Recall@3: {average_recall:.4f}"
                f"\nMRR: {mean_reciprocal_rank:.4f}"
            )

        output_file = (
            PROJECT_ROOT
            / "docs"
            / "chunk_level_threshold_results.csv"
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
        print("Results saved to:", output_file)


if __name__ == "__main__":
    main()