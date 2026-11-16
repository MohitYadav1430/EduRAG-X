from src.edurag_x.rag.citation_validator import CitationValidator


def sample_chunks():
    return [
        {"source": "dbms.pdf", "page_number": 1, "text": "DBMS introduction"},
        {"source": "dbms.pdf", "page_number": 2, "text": "Normalization"},
        {"source": "dbms.pdf", "page_number": 3, "text": "Primary keys"}
    ]


def test_valid_citation():
    validator = CitationValidator()

    answer = "DBMS manages databases. [Source: dbms.pdf, Page: 1]"

    result = validator.validate(answer, sample_chunks())

    assert result["total_citations"] == 1
    assert result["valid_citations"] == 1
    assert result["all_valid"] is True


def test_fake_source_is_rejected():
    validator = CitationValidator()

    answer = "Some information. [Source: fake.pdf, Page: 1]"

    result = validator.validate(answer, sample_chunks())

    assert result["invalid_citations"] == 1
    assert result["all_valid"] is False


def test_invalid_page_is_rejected():
    validator = CitationValidator()

    answer = "Some information. [Source: dbms.pdf, Page: 5]"

    result = validator.validate(answer, sample_chunks())

    assert result["invalid_citations"] == 1


def test_missing_citation_is_detected():
    validator = CitationValidator()

    answer = "DBMS is used to manage databases."

    result = validator.validate(answer, sample_chunks())

    assert result["missing_citations"] is True
    assert result["total_citations"] == 0
    assert result["all_valid"] is False


def test_multiple_page_citations():
    validator = CitationValidator()

    answer = "Normalization is important. [Source: dbms.pdf, Page: 1, Page: 2]"

    result = validator.validate(answer, sample_chunks())

    assert result["valid_citations"] == 1
    assert result["citations"][0]["pages"] == [1, 2]


def test_page_range_citation():
    validator = CitationValidator()

    answer = "DBMS concepts. [Source: dbms.pdf, Pages: 1-3]"

    result = validator.validate(answer, sample_chunks())

    assert result["valid_citations"] == 1
    assert result["citations"][0]["pages"] == [1, 2, 3]

def test_multiple_sources_in_one_bracket():
    validator = CitationValidator()

    answer = (
        "Combined information "
        "[Source: dbms.pdf, Page: 1; "
        "Source: transactions.pdf, Page: 2]"
    )

    chunks = [
        {"source": "dbms.pdf", "page_number": 1},
        {"source": "transactions.pdf", "page_number": 2}
    ]

    result = validator.validate(answer, chunks)

    assert result["total_citations"] == 2
    assert result["valid_citations"] == 2
    assert result["all_valid"] is True


def test_comma_separated_page_numbers():
    validator = CitationValidator()

    answer = "Information [Source: dbms.pdf, Page: 1, 2]"

    result = validator.validate(answer, sample_chunks())

    assert result["valid_citations"] == 1
    assert result["citations"][0]["pages"] == [1, 2]


def test_multiple_sources_and_pages():
    validator = CitationValidator()

    answer = (
        "Combined information "
        "[Source: dbms.pdf, Page: 1, 2; "
        "Source: transactions.pdf, Pages: 1-2]"
    )

    chunks = [
        {"source": "dbms.pdf", "page_number": 1},
        {"source": "dbms.pdf", "page_number": 2},
        {"source": "transactions.pdf", "page_number": 1},
        {"source": "transactions.pdf", "page_number": 2}
    ]

    result = validator.validate(answer, chunks)

    assert result["total_citations"] == 2
    assert result["valid_citations"] == 2
    assert result["all_valid"] is True


def test_invalid_page_range_is_rejected():
    validator = CitationValidator()

    answer = "Information [Source: dbms.pdf, Pages: 1-5]"

    result = validator.validate(answer, sample_chunks())

    assert result["invalid_citations"] == 1
    assert result["all_valid"] is False

