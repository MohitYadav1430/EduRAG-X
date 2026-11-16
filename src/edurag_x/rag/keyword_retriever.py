import re

from rank_bm25 import BM25Okapi


class KeywordRetriever:

    def __init__(self, vector_store):

        self.vector_store = vector_store
        self.bm25 = None
        self.documents = []
        self._document_signature = None

        self.refresh_index()

    def _tokenize(self, text):

        return re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower()
        )

    def _get_document_signature(self):

        return tuple(
            (
                document.get("chunk_id"),
                document.get("text", ""),
                document.get("source"),
                document.get("page_number")
            )
            for document in self.vector_store.documents
        )

    def refresh_index(self):

        self.documents = [
            document.copy()
            for document in self.vector_store.documents
        ]

        self._document_signature = self._get_document_signature()

        if not self.documents:
            self.bm25 = None
            return

        tokenized_documents = [
            self._tokenize(document["text"])
            for document in self.documents
        ]

        if not any(tokenized_documents):
            self.bm25 = None
            return

        self.bm25 = BM25Okapi(tokenized_documents)

    def _refresh_if_needed(self):

        current_signature = self._get_document_signature()

        if current_signature != self._document_signature:
            self.refresh_index()

    def retrieve(self, query, top_k=5):

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        self._refresh_if_needed()

        if self.bm25 is None:
            return []

        tokenized_query = self._tokenize(query)

        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True
        )

        results = []

        for index in ranked_indices:

            score = float(scores[index])

            if score <= 0:
                break

            result = self.documents[index].copy()

            result["keyword_score"] = score

            results.append(result)

            if len(results) >= top_k:
                break

        return results