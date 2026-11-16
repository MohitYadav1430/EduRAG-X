import csv
import tempfile
from pathlib import Path

from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline
from src.edurag_x.rag.retriever import Retriever


PROJECT_ROOT = Path(__file__).resolve().parent.parent

GROUND_TRUTH_FILE = (
    PROJECT_ROOT / "docs" / "retrieval_ground_truth.csv"
)

PDF_FILES = [
    PROJECT_ROOT / "data" / "sample_documents" / "dbms_sample.pdf",
    PROJECT_ROOT / "data" / "sample_documents" / "dbms_transactions_sample.pdf"
]

TOP_K = 2

THRESHOLDS = [None, 0.50, 0.60, 0.70]


def get_unique_documents(results):
    """Keep only the highest-ranked result for each source."""

    unique_documents = []
    seen_sources = set()

    for result in results:
        source = result.get("source")

        if source and source not in seen_sources:
            unique_documents.append(result)
            seen_sources.add(source)

    return unique_documents


def calculate_metrics(results, expected_sources):

    relevant_count = sum(
        1 for result in results
        if result.get("source") in expected_sources
    )

    precision = relevant_count / TOP_K

    recall = (
        relevant_count / len(expected_sources)
        if expected_sources
        else 0.0
    )

    reciprocal_rank = 0.0

    for rank, result in enumerate(results, start=1):

        if result.get("source") in expected_sources:
            reciprocal_rank = 1 / rank
            break

    return precision, recall, reciprocal_rank


def main():

    print("\n========== RETRIEVAL QUALITY EVALUATION ==========")

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
            "\nTotal vectors:",
            vector_store.total_vectors()
        )

        retriever = Retriever(
            vector_store=vector_store,
            embedding_engine=pipeline.embedding_engine
        )

        available_sources = {
            document.get("source")
            for document in vector_store.documents
        }

        print("\n========== QUERY EVALUATION ==========")

        for case in test_cases:

            query = case["query"]
            query_type = case["query_type"]

            expected_sources = {
                source.strip()
                for source in case["expected_relevant_sources"].split(";")
                if source.strip()
            }

            if query_type == "relevant":

                missing_sources = (
                    expected_sources - available_sources
                )

                if missing_sources:
                    raise ValueError(
                        f"Expected documents not indexed: "
                        f"{missing_sources}"
                    )

            print("\nQuestion:", query)

            base_results = retriever.retrieve(
                query,
                top_k=vector_store.total_vectors()
            )

            # Remove duplicate chunks from the same PDF.
            unique_results = get_unique_documents(base_results)

            for threshold in THRESHOLDS:

                if threshold is None:
                    results = unique_results
                    threshold_name = "None"

                else:
                    results = [
                        result for result in unique_results
                        if result.get("similarity_score", -1)
                        >= threshold
                    ]

                    threshold_name = str(threshold)

                if query_type == "relevant":

                    precision, recall, mrr = calculate_metrics(
                        results,
                        expected_sources
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
                    "retrieved_documents": len(results),
                    "precision_at_2": (
                        round(precision, 4)
                        if precision != "" else ""
                    ),
                    "recall_at_2": (
                        round(recall, 4)
                        if recall != "" else ""
                    ),
                    "reciprocal_rank": (
                        round(mrr, 4)
                        if mrr != "" else ""
                    ),
                    "no_documents_after_threshold": abstained,
                    "retrieved_sources": "; ".join(
                        result.get("source", "")
                        for result in results
                    )
                })

                print(
                    f"Threshold: {threshold_name} | "
                    f"Documents: {len(results)} | "
                    f"Precision@2: {precision} | "
                    f"Recall@2: {recall} | "
                    f"RR: {mrr} | "
                    f"No documents after threshold: {abstained}"
                )

        # Calculate average metrics for relevant queries.
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
                row["precision_at_2"]
                for row in relevant_rows
            ) / len(relevant_rows)

            average_recall = sum(
                row["recall_at_2"]
                for row in relevant_rows
            ) / len(relevant_rows)

            mean_reciprocal_rank = sum(
                row["reciprocal_rank"]
                for row in relevant_rows
            ) / len(relevant_rows)

            print(
                f"\nThreshold: {threshold_name}"
                f"\nMean Precision@2: {average_precision:.4f}"
                f"\nMean Recall@2: {average_recall:.4f}"
                f"\nMRR: {mean_reciprocal_rank:.4f}"
            )

        output_file = (
            PROJECT_ROOT
            / "docs"
            / "retrieval_evaluation_results.csv"
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

