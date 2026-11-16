import pytest
from pathlib import Path
from src.edurag_x.ingestion.pdf_processor import PDFProcessor


def test_extract_text_from_valid_pdf():
    processor = PDFProcessor()
    pdf_path = Path("data/sample_documents/dbms_sample.pdf")

    result = processor.extract_text(pdf_path)

    assert len(result) > 0
    assert "text" in result[0]
    assert "page_number" in result[0]
    assert "source" in result[0]


def test_page_numbers_are_correct():
    processor = PDFProcessor()
    pdf_path = Path("data/sample_documents/dbms_sample.pdf")

    result = processor.extract_text(pdf_path)

    assert result[0]["page_number"] == 1
    assert result[0]["source"] == "dbms_sample.pdf"


def test_nonexistent_pdf_raises_error():
    processor = PDFProcessor()

    with pytest.raises(FileNotFoundError):
        processor.extract_text("data/sample_documents/not_found.pdf")


def test_non_pdf_file_is_rejected():
    processor = PDFProcessor()

    with pytest.raises(ValueError):
        processor.extract_text("test.txt")
