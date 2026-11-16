import json

from src.edurag_x.ingestion.processing_history import ProcessingHistory


def test_add_record(tmp_path):
    history_file = tmp_path / "processing_history.json"
    history = ProcessingHistory(history_file)

    record = history.add_record(
        filename="dbms_sample.pdf",
        status="SUCCESS",
        pages=2,
        chunks=4,
        vectors=4
    )

    assert record["filename"] == "dbms_sample.pdf"
    assert record["status"] == "SUCCESS"
    assert record["pages"] == 2
    assert record["chunks"] == 4
    assert record["vectors"] == 4
    assert record["timestamp"] is not None


def test_get_history(tmp_path):
    history_file = tmp_path / "processing_history.json"
    history = ProcessingHistory(history_file)

    history.add_record(
        filename="test.pdf",
        status="SUCCESS",
        pages=2,
        chunks=4
    )

    records = history.get_history()

    assert len(records) == 1
    assert records[0]["filename"] == "test.pdf"


def test_multiple_records(tmp_path):
    history_file = tmp_path / "processing_history.json"
    history = ProcessingHistory(history_file)

    history.add_record(
        filename="first.pdf",
        status="SUCCESS"
    )

    history.add_record(
        filename="second.pdf",
        status="FAILED",
        error="Invalid PDF"
    )

    records = history.get_history()

    assert len(records) == 2
    assert records[0]["status"] == "SUCCESS"
    assert records[1]["status"] == "FAILED"


def test_clear_history(tmp_path):
    history_file = tmp_path / "processing_history.json"
    history = ProcessingHistory(history_file)

    history.add_record(
        filename="test.pdf",
        status="SUCCESS"
    )

    history.clear_history()

    assert history.get_history() == []


def test_history_is_saved_as_valid_json(tmp_path):
    history_file = tmp_path / "processing_history.json"
    history = ProcessingHistory(history_file)

    history.add_record(
        filename="sample.pdf",
        status="SUCCESS"
    )

    with open(history_file, "r", encoding="utf-8") as file:
        records = json.load(file)

    assert isinstance(records, list)
    assert len(records) == 1