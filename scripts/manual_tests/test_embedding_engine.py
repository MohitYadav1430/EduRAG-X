from src.edurag_x.llm.embedding_engine import EmbeddingEngine

engine = EmbeddingEngine()

documents = [
    "Database normalization reduces data redundancy.",
    "Python is a popular programming language.",
    "DBMS helps organize and manage databases."
]

print("\n========== EMBEDDING ENGINE TEST ==========")

document_vectors = engine.embed_documents(documents)

print("Total Documents:", len(document_vectors))
print("Document Vector Dimensions:", len(document_vectors[0]))

query = "How can duplicate data be reduced in a database?"

query_vector = engine.embed_query(query)

print("Query Vector Dimensions:", len(query_vector))

print("Document Embedding: SUCCESS")
print("Query Embedding: SUCCESS")

print("============================================")
