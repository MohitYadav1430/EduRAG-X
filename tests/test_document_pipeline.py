from unittest.mock import Mock, patch

from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline


@patch("src.edurag_x.ingestion.document_pipeline.EmbeddingEngine")
def test_pdf_ingestion_success(mock_embedding_class):
    mock_embedding = Mock()
    mock_embedding_class.return_value = mock_embedding
    mock_embedding.embed_documents.return_value = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6]
    ]

    mock_store = Mock()
    mock_store.add_documents.return_value = 2

    pipeline = DocumentIngestionPipeline(vector_store=mock_store)

    pipeline.pdf_processor.extract_text = Mock(return_value=[
        {"page_number": 1, "text": "Database Management System " * 30, "source": "sample.pdf"}
    ])

    result = pipeline.ingest_pdf("sample.pdf")

    assert result["source"] == "sample.pdf"
    assert result["pages"] == 1
    assert result["chunks"] > 0
    assert result["vectors_stored"] == 2

    mock_embedding.embed_documents.assert_called_once()
    mock_store.add_documents.assert_called_once()
    mock_store.save.assert_called_once_with(pipeline.storage_dir)


@patch("src.edurag_x.ingestion.document_pipeline.EmbeddingEngine")
def test_empty_document_returns_zero_chunks(mock_embedding_class):
    mock_store = Mock()

    pipeline = DocumentIngestionPipeline(vector_store=mock_store)

    pipeline.pdf_processor.extract_text = Mock(return_value=[])

    result = pipeline.ingest_pdf("empty.pdf")

    assert result == {
        "source": "empty.pdf",
        "pages": 0,
        "chunks": 0,
        "vectors_stored": 0
    }

    mock_embedding_class.return_value.embed_documents.assert_not_called()
    mock_store.add_documents.assert_not_called()
    mock_store.save.assert_not_called()


@patch("src.edurag_x.ingestion.document_pipeline.EmbeddingEngine")
def test_pdf_without_extractable_text(mock_embedding_class):
    mock_store = Mock()

    pipeline = DocumentIngestionPipeline(vector_store=mock_store)

    pipeline.pdf_processor.extract_text = Mock(return_value=[
        {"page_number": 1, "text": "   ", "source": "blank.pdf"}
    ])

    result = pipeline.ingest_pdf("blank.pdf")

    assert result["chunks"] == 0
    assert result["vectors_stored"] == 0
    mock_store.add_documents.assert_not_called()
    mock_store.save.assert_not_called()


@patch("src.edurag_x.ingestion.document_pipeline.EmbeddingEngine")
def test_existing_vector_store_is_loaded(mock_embedding_class, tmp_path):
    (tmp_path / "index.faiss").touch()
    (tmp_path / "documents.json").touch()

    loaded_store = Mock()

    with patch(
        "src.edurag_x.ingestion.document_pipeline.VectorStore.load",
        return_value=loaded_store
    ) as mock_load:

        pipeline = DocumentIngestionPipeline(storage_dir=tmp_path)

    mock_load.assert_called_once_with(tmp_path)
    assert pipeline.vector_store is loaded_store


@patch("src.edurag_x.ingestion.document_pipeline.EmbeddingEngine")
def test_new_vector_store_is_created_when_no_database_exists(
    mock_embedding_class, tmp_path
):

    with patch(
        "src.edurag_x.ingestion.document_pipeline.VectorStore"
    ) as mock_vector_store_class:

        new_store = Mock()
        mock_vector_store_class.return_value = new_store

        pipeline = DocumentIngestionPipeline(storage_dir=tmp_path)

    mock_vector_store_class.assert_called_once_with()
    assert pipeline.vector_store is new_store

@patch("src.edurag_x.ingestion.document_pipeline.EmbeddingEngine")
def test_persistence_survives_pipeline_restart(mock_embedding_class, tmp_path):

    mock_embedding = Mock()
    mock_embedding_class.return_value = mock_embedding

    mock_embedding.embed_documents.return_value = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0]
    ]

    storage_dir = tmp_path / "vector_store"

    first_pipeline = DocumentIngestionPipeline(
        storage_dir=storage_dir
    )

    first_pipeline.pdf_processor.extract_text = Mock(return_value=[
        {
            "page_number": 1,
            "text": "Database management system " * 30,
            "source": "sample.pdf"
        }
    ])

    result = first_pipeline.ingest_pdf("sample.pdf")

    assert result["vectors_stored"] == 2
    assert (storage_dir / "index.faiss").exists()
    assert (storage_dir / "documents.json").exists()

    second_pipeline = DocumentIngestionPipeline(
        storage_dir=storage_dir
    )

    assert second_pipeline.vector_store.total_vectors() == 2
    assert second_pipeline.vector_store.documents == (
        first_pipeline.vector_store.documents
    )

    mock_embedding.embed_documents.assert_called_once()
