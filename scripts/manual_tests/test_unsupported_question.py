from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline
from src.edurag_x.rag.retriever import Retriever
from src.edurag_x.rag.answer_generator import GroundedAnswerGenerator

pipeline = DocumentIngestionPipeline()

pdf_path = "data/sample_documents/dbms_sample.pdf"

pipeline.ingest_pdf(pdf_path)

retriever = Retriever(
    vector_store=pipeline.vector_store,
    embedding_engine=pipeline.embedding_engine
)

question = "Explain ACID properties in DBMS."

print("\n========== UNSUPPORTED QUESTION TEST ==========")
print("Student Question:", question)

results = retriever.retrieve(
    query=question,
    top_k=3
)

print("\nRetrieved Chunks:", len(results))

for result in results:
    print(
        "Page:", result["page_number"],
        "| Similarity:", round(result["similarity_score"], 4)
    )

generator = GroundedAnswerGenerator()

answer = generator.generate_answer(
    question=question,
    retrieved_chunks=results
)

print("\n========== AI RESPONSE ==========")
print(answer)

print("\n========== TEST COMPLETE ==========")
