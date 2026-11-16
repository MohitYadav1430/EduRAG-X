from pathlib import Path

from src.edurag_x.ingestion.pdf_processor import PDFProcessor
from src.edurag_x.ingestion.text_chunker import TextChunker
from src.edurag_x.llm.embedding_engine import EmbeddingEngine
from src.edurag_x.rag.vector_store import VectorStore


class DocumentIngestionPipeline:

    def __init__(
        self,
        vector_store=None,
        storage_dir="data/vector_store"
    ):

        self.pdf_processor = PDFProcessor()

        self.text_chunker = TextChunker(
            chunk_size=800,
            chunk_overlap=150
        )

        self.embedding_engine = EmbeddingEngine()

        self.storage_dir = Path(storage_dir)

        if vector_store is not None:
            self.vector_store = vector_store

        elif (
            (self.storage_dir / "index.faiss").exists()
            and (self.storage_dir / "documents.json").exists()
        ):
            self.vector_store = VectorStore.load(self.storage_dir)

        else:
            self.vector_store = VectorStore()

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

        # Step 5: Automatically save vector database
        self.vector_store.save(self.storage_dir)

        return {
            "source": pdf_path.name,
            "pages": len(pages),
            "chunks": len(chunks),
            "vectors_stored": total_vectors
        }
