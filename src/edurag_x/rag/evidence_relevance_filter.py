import math


class EvidenceRelevanceFilter:

    def __init__(self, vector_store, min_relevance=0.60):

        if (
            not isinstance(min_relevance, (int, float))
            or isinstance(min_relevance, bool)
            or not math.isfinite(min_relevance)
            or not -1.0 <= min_relevance <= 1.0
        ):
            raise ValueError(
                "min_relevance must be a finite number between -1 and 1."
            )

        self.vector_store = vector_store
        self.min_relevance = float(min_relevance)

    def filter(self, query_embedding, retrieved_chunks):

        if not retrieved_chunks:
            return []

        scored_chunks = self.vector_store.score_documents(
            query_embedding=query_embedding,
            documents=retrieved_chunks
        )

        relevant_chunks = []

        for chunk in scored_chunks:

            score = chunk.get("similarity_score")

            if score is None:
                continue

            if score >= self.min_relevance:

                relevant_chunks.append(chunk)

        return relevant_chunks