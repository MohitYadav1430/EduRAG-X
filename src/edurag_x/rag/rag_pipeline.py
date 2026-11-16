from src.edurag_x.rag.answer_generator import GroundedAnswerGenerator
from src.edurag_x.rag.citation_validator import CitationValidator
from src.edurag_x.rag.evidence_verifier import EvidenceVerifier


class RAGPipeline:

    def __init__(
        self,
        retriever,
        answer_generator=None,
        citation_validator=None,
        evidence_verifier=None,
        evidence_relevance_filter=None
    ):

        self.retriever = retriever

        self.answer_generator = (
            answer_generator or GroundedAnswerGenerator()
        )

        self.citation_validator = (
            citation_validator or CitationValidator()
        )

        self.evidence_verifier = (
            evidence_verifier or EvidenceVerifier()
        )

        self.evidence_relevance_filter = evidence_relevance_filter

    def answer_question(
        self,
        question,
        top_k=5,
        min_similarity=None
    ):

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        retrieval_options = {
            "top_k": top_k
        }

        if min_similarity is not None:
            retrieval_options["min_similarity"] = min_similarity

        query_embedding = None

        # Generate query embedding once when relevance filtering is enabled.
        if self.evidence_relevance_filter is not None:

            query_embedding = self.retriever.embed_query(question)

            retrieval_options["query_embedding"] = query_embedding

        retrieved_chunks = self.retriever.retrieve(
            question,
            **retrieval_options
        )

        # Keep original retrieved candidates separate from filtered evidence.
        evidence_chunks = retrieved_chunks

        if self.evidence_relevance_filter is not None:

            evidence_chunks = self.evidence_relevance_filter.filter(
                query_embedding,
                retrieved_chunks
            )

            # Abstain when no sufficiently relevant evidence is available.
            if not evidence_chunks:

                return {
                    "question": question,
                    "status": "INSUFFICIENT_EVIDENCE",
                    "answer": (
                        "I could not find sufficiently relevant "
                        "evidence in the uploaded documents "
                        "to answer this question."
                    ),
                    "error": None,
                    "retrieved_chunks": retrieved_chunks,
                    "filtered_chunks": [],
                    "citation_validation": None,
                    "evidence_verification": None
                }

        try:

            answer = self.answer_generator.generate_answer(
                question,
                evidence_chunks
            )

        except RuntimeError as error:

            result = {
                "question": question,
                "status": "ANSWER_GENERATION_FAILED",
                "answer": None,
                "error": str(error),
                "retrieved_chunks": retrieved_chunks,
                "citation_validation": None,
                "evidence_verification": None
            }

            if self.evidence_relevance_filter is not None:
                result["filtered_chunks"] = evidence_chunks

            return result

        citation_validation = self.citation_validator.validate(
            answer,
            evidence_chunks
        )

        evidence_verification = self.evidence_verifier.verify(
            answer,
            evidence_chunks
        )

        result = {
            "question": question,
            "status": "COMPLETED",
            "answer": answer,
            "error": None,
            "retrieved_chunks": retrieved_chunks,
            "citation_validation": citation_validation,
            "evidence_verification": evidence_verification
        }

        if self.evidence_relevance_filter is not None:
            result["filtered_chunks"] = evidence_chunks

        return result