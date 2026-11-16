class TextChunker:

    def __init__(self, chunk_size=800, chunk_overlap=150):
        if chunk_size <= 0:
            raise ValueError("Chunk size must be greater than zero.")

        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("Chunk overlap must be smaller than chunk size.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, pages):

        chunks = []
        chunk_id = 1

        for page in pages:

            text = page["text"].strip()

            if not text:
                continue

            start = 0

            while start < len(text):

                end = min(start + self.chunk_size, len(text))

                chunk_text = text[start:end].strip()

                if chunk_text:
                    chunks.append({
                        "chunk_id": chunk_id,
                        "text": chunk_text,
                        "source": page["source"],
                        "page_number": page["page_number"]
                    })

                    chunk_id += 1

                if end == len(text):
                    break

                start = end - self.chunk_overlap

        return chunks
