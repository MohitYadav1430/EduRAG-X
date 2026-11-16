from src.edurag_x.ingestion.text_chunker import TextChunker

sample_pages = [
    {
        "page_number": 1,
        "source": "sample.pdf",
        "text": "Database Management System (DBMS) is software used to manage databases. " * 30
    },
    {
        "page_number": 2,
        "source": "sample.pdf",
        "text": "Normalization is the process of organizing data to reduce redundancy. " * 20
    }
]

chunker = TextChunker(chunk_size=800, chunk_overlap=150)

chunks = chunker.split_text(sample_pages)

print("\n========== TEXT CHUNKING TEST ==========")

for chunk in chunks:
    print(f"\nChunk ID: {chunk['chunk_id']}")
    print(f"Source: {chunk['source']}")
    print(f"Page: {chunk['page_number']}")
    print(f"Characters: {len(chunk['text'])}")
    print(f"Text Preview: {chunk['text'][:100]}...")

print("\nTotal Chunks:", len(chunks))
print("Maximum Chunk Size:", max(len(c["text"]) for c in chunks))
print("========================================")
