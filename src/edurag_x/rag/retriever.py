import math

from src.edurag_x.llm.embedding_engine import EmbeddingEngine


class Retriever:

    def __init__(self, vector_store, embedding_engine=None):

        self.vector_store = vector_store

        self.embedding_engine = (
            embedding_engine or EmbeddingEngine()
        )

    def embed_query(self, query):

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        return self.embedding_engine.embed_query(query)

    def retrieve(
        self,
        query,
        top_k=5,
        min_similarity=None,
        query_embedding=None
    ):

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if (
            not isinstance(top_k, int)
            or isinstance(top_k, bool)
            or top_k <= 0
        ):
            raise ValueError("top_k must be greater than zero.")

        if min_similarity is not None:

            if not isinstance(min_similarity, (int, float)):
                raise ValueError("min_similarity must be a number.")

            if not math.isfinite(min_similarity):
                raise ValueError("min_similarity must be finite.")

            if not -1.0 <= min_similarity <= 1.0:
                raise ValueError(
                    "min_similarity must be between -1 and 1."
                )

        if query_embedding is None:
            query_embedding = self.embed_query(query)

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k
        )

        if min_similarity is not None:

            results = [
                result
                for result in results
                if result.get("similarity_score") is not None
                and result["similarity_score"] >= min_similarity
            ]

        return results