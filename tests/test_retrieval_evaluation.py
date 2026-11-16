from scripts.evaluate_retrieval import (
    get_unique_documents,
    calculate_metrics
)


def test_duplicate_documents_are_removed():

    results = [
        {"source": "dbms_sample.pdf", "similarity_score": 0.95},
        {"source": "dbms_sample.pdf", "similarity_score": 0.85},
        {"source": "dbms_transactions_sample.pdf", "similarity_score": 0.75}
    ]

    unique = get_unique_documents(results)

    assert len(unique) == 2


def test_highest_ranked_chunk_is_preserved():

    results = [
        {"source": "dbms_sample.pdf", "similarity_score": 0.95},
        {"source": "dbms_sample.pdf", "similarity_score": 0.85}
    ]

    unique = get_unique_documents(results)

    assert unique[0]["similarity_score"] == 0.95


def test_precision_recall_and_mrr():

    results = [
        {"source": "dbms_sample.pdf"},
        {"source": "dbms_transactions_sample.pdf"}
    ]

    precision, recall, mrr = calculate_metrics(
        results,
        {"dbms_sample.pdf"}
    )

    assert precision == 0.5
    assert recall == 1.0
    assert mrr == 1.0


def test_relevant_document_at_second_rank():

    results = [
        {"source": "dbms_transactions_sample.pdf"},
        {"source": "dbms_sample.pdf"}
    ]

    precision, recall, mrr = calculate_metrics(
        results,
        {"dbms_sample.pdf"}
    )

    assert precision == 0.5
    assert recall == 1.0
    assert mrr == 0.5


def test_no_relevant_document_found():

    results = [
        {"source": "dbms_transactions_sample.pdf"}
    ]

    precision, recall, mrr = calculate_metrics(
        results,
        {"dbms_sample.pdf"}
    )

    assert precision == 0.0
    assert recall == 0.0
    assert mrr == 0.0

