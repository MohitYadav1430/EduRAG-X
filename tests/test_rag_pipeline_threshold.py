from unittest.mock import Mock

from src.edurag_x.rag.rag_pipeline import RAGPipeline


def test_similarity_threshold_is_passed_to_retriever():

    question = "Explain ACID properties."

    retriever = Mock()
    retriever.retrieve.return_value = []

    answer_generator = Mock()
    answer_generator.generate_answer.return_value = (
        "No relevant evidence found."
    )

    citation_validator = Mock()
    citation_validator.validate.return_value = {}

    evidence_verifier = Mock()
    evidence_verifier.verify.return_value = {}

    pipeline = RAGPipeline(
        retriever=retriever,
        answer_generator=answer_generator,
        citation_validator=citation_validator,
        evidence_verifier=evidence_verifier
    )

    pipeline.answer_question(
        question,
        top_k=5,
        min_similarity=0.60
    )

    retriever.retrieve.assert_called_once_with(
        question,
        top_k=5,
        min_similarity=0.60
    )