from google import genai
from google.genai import types

from src.edurag_x.config.settings import GEMINI_API_KEY


class EmbeddingEngine:

    def __init__(self):

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = "gemini-embedding-2"

    def embed_documents(self, texts):

        if not texts:
            return []

        document_vectors = []

        for text in texts:

            if not text or not text.strip():
                raise ValueError("Document text cannot be empty.")

            response = self.client.models.embed_content(
                model=self.model,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT"
                )
            )

            document_vectors.append(
                response.embeddings[0].values
            )

        return document_vectors

    def embed_query(self, query):

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        response = self.client.models.embed_content(
            model=self.model,
            contents=query,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY"
            )
        )

        return response.embeddings[0].values
