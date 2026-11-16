class HybridRetriever:

    def __init__(
        self,
        semantic_retriever,
        keyword_retriever,
        rrf_k=60
    ):

        if (
            not isinstance(rrf_k, int)
            or isinstance(rrf_k, bool)
            or rrf_k <= 0
        ):
            raise ValueError(
                "rrf_k must be a positive integer."
            )

        self.semantic_retriever = semantic_retriever
        self.keyword_retriever = keyword_retriever
        self.rrf_k = rrf_k

    def embed_query(self, query):

        return self.semantic_retriever.embed_query(query)

    def _get_document_key(self, document):

        return (
            document.get("source"),
            document.get("page_number"),
            document.get("chunk_id"),
            document.get("text", "")
        )

    def _reciprocal_rank_fusion(
        self,
        semantic_results,
        keyword_results,
        top_k
    ):

        fused_results = {}

        retrieval_lists = [
            ("semantic", semantic_results),
            ("keyword", keyword_results)
        ]

        for retrieval_type, results in retrieval_lists:

            for rank, document in enumerate(results, start=1):

                document_key = self._get_document_key(document)

                if document_key not in fused_results:

                    fused_results[document_key] = document.copy()

                    fused_results[document_key]["rrf_score"] = 0.0
                    fused_results[document_key]["retrieval_sources"] = []

                    fused_results[document_key]["semantic_rank"] = None
                    fused_results[document_key]["keyword_rank"] = None

                    fused_results[document_key]["similarity_score"] = None
                    fused_results[document_key]["keyword_score"] = None

                fused_document = fused_results[document_key]

                fused_document["rrf_score"] += (
                    1.0 / (self.rrf_k + rank)
                )

                fused_document["retrieval_sources"].append(
                    retrieval_type
                )

                if retrieval_type == "semantic":

                    fused_document["semantic_rank"] = rank

                    fused_document["similarity_score"] = (
                        document.get("similarity_score")
                    )

                elif retrieval_type == "keyword":

                    fused_document["keyword_rank"] = rank

                    fused_document["keyword_score"] = (
                        document.get("keyword_score")
                    )

        ranked_results = sorted(
            fused_results.values(),
            key=lambda document: document["rrf_score"],
            reverse=True
        )

        return ranked_results[:top_k]

    def retrieve(
        self,
        query,
        top_k=5,
        min_similarity=None,
        query_embedding=None
    ):

        if not query or not query.strip():
            raise ValueError(
                "Search query cannot be empty."
            )

        if (
            not isinstance(top_k, int)
            or isinstance(top_k, bool)
            or top_k <= 0
        ):
            raise ValueError(
                "top_k must be greater than zero."
            )

        if query_embedding is None:

            embed_method = getattr(
                type(self.semantic_retriever),
                "embed_query",
                None
            )

            if callable(embed_method):
                query_embedding = self.embed_query(query)

        if query_embedding is not None:

            semantic_results = self.semantic_retriever.retrieve(
                query,
                top_k=top_k,
                min_similarity=min_similarity,
                query_embedding=query_embedding
            )

        else:

            semantic_results = self.semantic_retriever.retrieve(
                query,
                top_k=top_k,
                min_similarity=min_similarity
            )
        keyword_results = self.keyword_retriever.retrieve(
            query,
            top_k=top_k
        )

        return self._reciprocal_rank_fusion(
            semantic_results,
            keyword_results,
            top_k
        )