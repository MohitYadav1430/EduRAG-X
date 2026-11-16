import csv
import tempfile
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
        if expected_chunks else 0.0
    )

    reciprocal_rank = 0.0

    for rank, chunk_id in enumerate(retrieved_ids, start=1):

        if chunk_id in expected_chunks:
            reciprocal_rank = 1 / rank
            break

    return relevant_count, precision, recall, reciprocal_rank


def main():

    print("\n========== HYBRID THRESHOLD EVALUATION ==========")

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

        print("\n========== QUERY EVALUATION ==========")

        for case in test_cases:

            query = case["query"]
            query_type = case["query_type"]

            expected_chunks = {
                chunk.strip()
                for chunk in case["expected_relevant_chunks"].split(";")
                if chunk.strip()
            }

            print("\nQuestion:", query)

            # Generate semantic and keyword results only once per query.
            semantic_results = semantic_retriever.retrieve(
                query,
                top_k=TOP_K
            )

            keyword_results = keyword_retriever.retrieve(
                query,
                top_k=TOP_K
            )

            for threshold in THRESHOLDS:

                threshold_name = (
                    "None" if threshold is None else str(threshold)
                )

                if threshold is None:

                    filtered_semantic = semantic_results

                else:

                    filtered_semantic = [
                        result
                        for result in semantic_results
                        if (
                            result.get("similarity_score") is not None
                            and result["similarity_score"] >= threshold
                        )
                    ]

                # BM25 results remain unchanged across thresholds.
                hybrid_results = (
                    hybrid_retriever._reciprocal_rank_fusion(
                        filtered_semantic,
                        keyword_results,
                        TOP_K
                    )
                )

                retrieved_ids = [
                    f"{result['source']}:{result['chunk_id']}"
                    for result in hybrid_results
                ]

                relevant_count = ""
                precision = ""
                recall = ""
                mrr = ""
                relevant_query_covered = ""

                if query_type == "relevant":

                    (
                        relevant_count,
                        precision,
                        recall,
                        mrr
                    ) = calculate_metrics(
                        hybrid_results,
                        expected_chunks
                    )

                    relevant_query_covered = relevant_count > 0

                elif query_type == "unrelated":

                    relevant_query_covered = ""

                else:

                    raise ValueError(
                        f"Unknown query type: {query_type}"
                    )

                no_chunks_retrieved = len(hybrid_results) == 0

                output_rows.append({

                    "query": query,
                    "query_type": query_type,
                    "threshold": threshold_name,

                    "semantic_chunks_after_threshold": len(
                        filtered_semantic
                    ),

                    "keyword_chunks": len(keyword_results),

                    "retrieved_chunks": len(hybrid_results),

                    "relevant_chunks_found": relevant_count,

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

                    "relevant_query_covered": relevant_query_covered,

                    "no_chunks_retrieved": no_chunks_retrieved,

                    "retrieved_chunk_ids": "; ".join(retrieved_ids)
                })

                print(
                    f"Threshold: {threshold_name} | "
                    f"Semantic: {len(filtered_semantic)} | "
                    f"BM25: {len(keyword_results)} | "
                    f"Hybrid: {len(hybrid_results)} | "
                    f"Results: {retrieved_ids}"
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

            unrelated_rows = [
                row for row in output_rows
                if row["query_type"] == "unrelated"
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

            average_mrr = sum(
                row["mrr"]
                for row in relevant_rows
            ) / len(relevant_rows)

            coverage = sum(
                row["relevant_query_covered"]
                for row in relevant_rows
            ) / len(relevant_rows)

            unrelated_abstention_rate = (
                sum(
                    row["no_chunks_retrieved"]
                    for row in unrelated_rows
                ) / len(unrelated_rows)
                if unrelated_rows else 0.0
            )

            print(f"\nThreshold: {threshold_name}")
            print(f"Mean Precision@3: {average_precision:.4f}")
            print(f"Mean Recall@3: {average_recall:.4f}")
            print(f"Mean MRR: {average_mrr:.4f}")
            print(f"Relevant Query Coverage: {coverage:.4f}")
            print(
                "Unrelated Query Abstention Rate:",
                f"{unrelated_abstention_rate:.4f}"
            )

        output_file = (
            PROJECT_ROOT
            / "docs"
            / "hybrid_threshold_evaluation_results.csv"
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