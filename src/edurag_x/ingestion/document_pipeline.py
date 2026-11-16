from pathlib import Path
import shutil
import tempfile

from src.edurag_x.ingestion.pdf_processor import PDFProcessor
from src.edurag_x.ingestion.text_chunker import TextChunker
from src.edurag_x.llm.embedding_engine import EmbeddingEngine
from src.edurag_x.rag.vector_store import VectorStore


class DocumentIngestionPipeline:

    def __init__(
        self,
        vector_store=None,
        storage_dir="data/vector_store",
        storage_manager=None
    ):

        self.pdf_processor = PDFProcessor()

        self.text_chunker = TextChunker(
            chunk_size=800,
            chunk_overlap=150
        )

        self.embedding_engine = EmbeddingEngine()

        self.storage_dir = Path(storage_dir)
        self.storage_manager = storage_manager

        if vector_store is not None:
            self.vector_store = vector_store

        else:
            self._restore_cloud_store()

            if (
                (self.storage_dir / "index.faiss").exists()
                and (self.storage_dir / "documents.json").exists()
            ):
                self.vector_store = VectorStore.load(self.storage_dir)

            else:
                self.vector_store = VectorStore()

    def _restore_cloud_store(self):

        if self.storage_manager is None:
            return

        try:
            with tempfile.TemporaryDirectory() as temp_dir:

                temp_dir = Path(temp_dir)

                index_path = temp_dir / "index.faiss"
                documents_path = temp_dir / "documents.json"

                self.storage_manager.download_file(
                    "vector_store/index.faiss",
                    index_path
                )

                self.storage_manager.download_file(
                    "vector_store/documents.json",
                    documents_path
                )

                self.storage_dir.mkdir(
                    parents=True,
                    exist_ok=True
                )

                shutil.copy2(
                    index_path,
                    self.storage_dir / "index.faiss"
                )

                shutil.copy2(
                    documents_path,
                    self.storage_dir / "documents.json"
                )

        except Exception as error:
            self.cloud_restore_error = str(error)

    def _sync_cloud_store(self):

        if self.storage_manager is None:
            return

        self.storage_manager.upload_file(
            self.storage_dir / "index.faiss",
            "vector_store/index.faiss"
        )

        self.storage_manager.upload_file(
            self.storage_dir / "documents.json",
            "vector_store/documents.json"
        )

    def ingest_pdf(self, pdf_path):

        pdf_path = Path(pdf_path)

        # Step 1: Extract PDF text
        pages = self.pdf_processor.extract_text(pdf_path)

        # Step 2: Split extracted text into chunks
        chunks = self.text_chunker.split_text(pages)

        if not chunks:
            return {
                "source": pdf_path.name,
                "pages": len(pages),
                "chunks": 0,
                "vectors_stored": 0
            }

        # Step 3: Generate embeddings
        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.embedding_engine.embed_documents(texts)

        # Step 4: Store embeddings and metadata in FAISS
        total_vectors = self.vector_store.add_documents(
            chunks,
            embeddings
        )

        # Step 5: Save local vector database
        self.vector_store.save(self.storage_dir)

        # Step 6: Sync vector database with Supabase
        self._sync_cloud_store()

        return {
            "source": pdf_path.name,
            "pages": len(pages),
            "chunks": len(chunks),
            "vectors_stored": total_vectors
        }