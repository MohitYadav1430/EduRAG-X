import faiss
import json
import numpy as np

from pathlib import Path


class VectorStore:

    def __init__(self):

        self.index = None
        self.documents = []
        self.dimension = None

    def add_documents(self, chunks, embeddings):

        if not chunks or not embeddings:
            raise ValueError("Chunks and embeddings cannot be empty.")

        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match.")

        vectors = np.asarray(embeddings, dtype=np.float32)

        if vectors.ndim != 2:
            raise ValueError("Embeddings must be a 2D array.")

        if not np.isfinite(vectors).all():
            raise ValueError("Embeddings contain invalid numerical values.")

        if self.index is None:

            self.dimension = vectors.shape[1]

            self.index = faiss.IndexFlatIP(self.dimension)

        elif vectors.shape[1] != self.dimension:

            raise ValueError("Embedding dimensions do not match.")

        faiss.normalize_L2(vectors)

        self.index.add(vectors)

        self.documents.extend(chunks)

        return self.index.ntotal

    def search(self, query_embedding, top_k=5):

        if self.index is None or self.index.ntotal == 0:
            raise ValueError("Vector store is empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        query_vector = np.asarray(
            [query_embedding],
            dtype=np.float32
        )

        if query_vector.shape[1] != self.dimension:
            raise ValueError("Query embedding dimension mismatch.")

        if not np.isfinite(query_vector).all():
            raise ValueError("Query embedding contains invalid values.")

        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(
            query_vector,
            min(top_k, self.index.ntotal)
        )

        results = []

        for score, index_position in zip(scores[0], indices[0]):

            if index_position == -1:
                continue

            result = self.documents[index_position].copy()

            result["similarity_score"] = float(score)

            results.append(result)

        return results

    def score_documents(self, query_embedding, documents):

        if self.index is None or self.index.ntotal == 0:
            raise ValueError("Vector store is empty.")

        if not documents:
            return []

        query_vector = np.asarray(
            query_embedding,
            dtype=np.float32
        )

        if query_vector.ndim != 1:
            raise ValueError("Query embedding must be a 1D vector.")

        if len(query_vector) != self.dimension:
            raise ValueError("Query embedding dimension mismatch.")

        if not np.isfinite(query_vector).all():
            raise ValueError("Query embedding contains invalid values.")

        query_vector = query_vector.copy()

        query_norm = np.linalg.norm(query_vector)

        if query_norm == 0:
            raise ValueError("Query embedding cannot be a zero vector.")

        query_vector = query_vector / query_norm

        results = []

        for document in documents:

            document_key = (
                document.get("source"),
                document.get("page_number"),
                document.get("chunk_id"),
                document.get("text", "")
            )

            matching_indices = []

            for index_position, stored_document in enumerate(
                self.documents
            ):

                stored_key = (
                    stored_document.get("source"),
                    stored_document.get("page_number"),
                    stored_document.get("chunk_id"),
                    stored_document.get("text", "")
                )

                if stored_key == document_key:
                    matching_indices.append(index_position)

            if not matching_indices:
                raise ValueError(
                    "Document not found in vector store."
                )

            best_score = None

            for index_position in matching_indices:

                stored_vector = self.index.reconstruct(index_position)

                score = float(
                    np.dot(query_vector, stored_vector)
                )

                if best_score is None or score > best_score:
                    best_score = score

            result = document.copy()

            result["similarity_score"] = best_score

            results.append(result)

        return results

    def save(self, directory):

        if self.index is None or self.index.ntotal == 0:
            raise ValueError("Cannot save an empty vector store.")

        if self.index.ntotal != len(self.documents):
            raise ValueError("Vector and document counts do not match.")

        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        index_path = directory / "index.faiss"
        documents_path = directory / "documents.json"

        faiss.write_index(self.index, str(index_path))

        with open(documents_path, "w", encoding="utf-8") as file:
            json.dump(
                self.documents,
                file,
                ensure_ascii=False,
                indent=4
            )

        return True

    @classmethod
    def load(cls, directory):

        directory = Path(directory)

        index_path = directory / "index.faiss"
        documents_path = directory / "documents.json"

        if not index_path.exists():
            raise FileNotFoundError("FAISS index file not found.")

        if not documents_path.exists():
            raise FileNotFoundError("Documents metadata file not found.")

        index = faiss.read_index(str(index_path))

        with open(documents_path, "r", encoding="utf-8") as file:
            documents = json.load(file)

        if not isinstance(documents, list):
            raise ValueError("Invalid documents metadata format.")

        if index.ntotal != len(documents):
            raise ValueError("Vector and document counts do not match.")

        store = cls()

        store.index = index
        store.documents = documents
        store.dimension = index.d

        return store

    def total_vectors(self):

        if self.index is None:
            return 0

        return self.index.ntotal