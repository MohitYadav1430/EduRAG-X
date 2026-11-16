from src.edurag_x.rag.vector_store import VectorStore

store = VectorStore()

documents = [
    {
        "chunk_id": 1,
        "text": "Database normalization reduces duplicate data.",
        "source": "dbms.pdf",
        "page_number": 1
    },
    {
        "chunk_id": 2,
        "text": "Python is a popular programming language.",
        "source": "python.pdf",
        "page_number": 5
    },
    {
        "chunk_id": 3,
        "text": "Normalization improves database consistency.",
        "source": "dbms.pdf",
        "page_number": 2
    }
]

# Controlled vectors for testing FAISS independently
embeddings = [
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.9, 0.1, 0.0]
]

total = store.add_documents(documents, embeddings)

query_embedding = [1.0, 0.0, 0.0]

results = store.search(query_embedding, top_k=2)

print("\n========== VECTOR STORE TEST ==========")

print("Total Stored Vectors:", store.total_vectors())

for result in results:
    print("\nChunk ID:", result["chunk_id"])
    print("Text:", result["text"])
    print("Source:", result["source"])
    print("Page:", result["page_number"])
    print("Similarity:", round(result["similarity_score"], 4))

print("\nRetrieved Documents:", len(results))
print("Vector Store Test: SUCCESS")
print("=======================================")
