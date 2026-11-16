from src.edurag_x.ingestion.document_pipeline import DocumentIngestionPipeline
from src.edurag_x.rag.retriever import Retriever
from src.edurag_x.rag.answer_generator import GroundedAnswerGenerator


# Initialize the document pipeline
pipeline = DocumentIngestionPipeline()

pdf_path = "data/sample_documents/dbms_sample.pdf"

print("\n========== STEP 1: DOCUMENT INGESTION ==========")

ingestion_result = pipeline.ingest_pdf(pdf_path)

print("Document:", ingestion_result["source"])
print("Pages:", ingestion_result["pages"])
print("Chunks:", ingestion_result["chunks"])
print("Vectors:", ingestion_result["vectors_stored"])


# Initialize the retriever
retriever = Retriever(
    vector_store=pipeline.vector_store,
    embedding_engine=pipeline.embedding_engine
)

question = "How can duplicate data in a database be reduced?"

print("\n========== STEP 2: SEMANTIC RETRIEVAL ==========")
print("Student Question:", question)

retrieved_chunks = retriever.retrieve(
    query=question,
    top_k=3
)

print("Retrieved Chunks:", len(retrieved_chunks))


# Generate an evidence-grounded answer
answer_generator = GroundedAnswerGenerator()

print("\n========== STEP 3: GROUNDED AI ANSWER ==========")

answer = answer_generator.generate_answer(
    question=question,
    retrieved_chunks=retrieved_chunks
)

print("\nEduRAG-X Answer:\n")
print(answer)

print("\n========== RAG PIPELINE COMPLETE ==========")
