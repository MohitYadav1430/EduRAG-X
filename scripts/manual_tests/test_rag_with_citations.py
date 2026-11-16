from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline
from src.edurag_x.rag.retriever import Retriever
from src.edurag_x.rag.answer_generator import GroundedAnswerGenerator
from src.edurag_x.rag.citation_validator import CitationValidator


pipeline = DocumentIngestionPipeline()

pdf_path = "data/sample_documents/dbms_sample.pdf"

print("\n========== DOCUMENT INGESTION ==========")

result = pipeline.ingest_pdf(pdf_path)

print("Document:", result["source"])
print("Pages:", result["pages"])
print("Chunks:", result["chunks"])


retriever = Retriever(
    vector_store=pipeline.vector_store,
    embedding_engine=pipeline.embedding_engine
)

question = "How can duplicate data in a database be reduced?"

print("\n========== RETRIEVAL ==========")

retrieved_chunks = retriever.retrieve(
    query=question,
    top_k=3
)

print("Retrieved Chunks:", len(retrieved_chunks))


generator = GroundedAnswerGenerator()

print("\n========== GENERATED ANSWER ==========")

answer = generator.generate_answer(
    question=question,
    retrieved_chunks=retrieved_chunks
)

print(answer)


validator = CitationValidator()

print("\n========== CITATION VALIDATION ==========")

validation = validator.validate(
    answer=answer,
    retrieved_chunks=retrieved_chunks
)

print("Total Citations:", validation["total_citations"])
print("Valid Citations:", validation["valid_citations"])
print("Invalid Citations:", validation["invalid_citations"])

for citation in validation["citations"]:
    print(
        citation["source"],
        "| Pages:", citation["pages"],
        "| Valid:", citation["valid"]
    )

print("\nAll Citations Valid:", validation["all_valid"])

print("\n========== INTEGRATION TEST COMPLETE ==========")
