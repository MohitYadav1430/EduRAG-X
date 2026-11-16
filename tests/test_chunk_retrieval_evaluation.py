from scripts.evaluate_chunk_retrieval import calculate_metrics


def test_all_relevant_chunks_retrieved():

    results = [
        {"source": "dbms_sample.pdf", "chunk_id": 1},
        {"source": "dbms_sample.pdf", "chunk_id": 4},
        {"source": "dbms_transactions_sample.pdf", "chunk_id": 1}
    ]

    expected = {
        "dbms_sample.pdf:1",
        "dbms_sample.pdf:4"
    }

    precision, recall, mrr = calculate_metrics(results, expected)

    assert precision == 2 / 3
    assert recall == 1.0
    assert mrr == 1.0


def test_relevant_chunk_at_second_rank():

    results = [
        {"source": "other.pdf", "chunk_id": 1},
        {"source": "dbms_sample.pdf", "chunk_id": 1}
    ]

    expected = {"dbms_sample.pdf:1"}

    precision, recall, mrr = calculate_metrics(results, expected)

    assert precision == 1 / 3
    assert recall == 1.0
    assert mrr == 0.5


def test_no_relevant_chunk_retrieved():

    results = [
        {"source": "other.pdf", "chunk_id": 1}
    ]

    expected = {"dbms_sample.pdf:1"}

    precision, recall, mrr = calculate_metrics(results, expected)

    assert precision == 0.0
    assert recall == 0.0
    assert mrr == 0.0


def test_multiple_relevant_chunks_at_different_ranks():

    results = [
        {"source": "dbms_sample.pdf", "chunk_id": 1},
        {"source": "other.pdf", "chunk_id": 2},
        {"source": "dbms_sample.pdf", "chunk_id": 4}
    ]

    expected = {
        "dbms_sample.pdf:1",
        "dbms_sample.pdf:4"
    }

    precision, recall, mrr = calculate_metrics(results, expected)

    assert precision == 2 / 3
    assert recall == 1.0
    assert mrr == 1.0


def test_no_results():

    results = []
    expected = {"dbms_sample.pdf:1"}

    precision, recall, mrr = calculate_metrics(results, expected)

    assert precision == 0.0
    assert recall == 0.0
    assert mrr == 0.0

