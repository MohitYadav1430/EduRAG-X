import re


class SentenceAwareChunker:

    def __init__(self, chunk_size=800, chunk_overlap=150):

        if chunk_size <= 0:
            raise ValueError("Chunk size must be greater than zero.")

        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError(
                "Chunk overlap must be smaller than chunk size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_sentences(self, text):

        sentences = re.split(
            r'(?<!\d\.)(?<=[.!?])\s+',
            text.strip()
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    def split_text(self, pages):

        chunks = []
        chunk_id = 1

        for page in pages:

            text = page["text"].strip()

            if not text:
                continue

            sentences = self.split_sentences(text)

            current_sentences = []
            current_length = 0

            for sentence in sentences:

                # Handle sentences larger than the chunk size.
                if len(sentence) > self.chunk_size:

                    if current_sentences:

                        chunk_text = " ".join(current_sentences)

                        chunks.append({
                            "chunk_id": chunk_id,
                            "text": chunk_text,
                            "source": page["source"],
                            "page_number": page["page_number"]
                        })

                        chunk_id += 1
                        current_sentences = []
                        current_length = 0

                    for start in range(
                        0,
                        len(sentence),
                        self.chunk_size
                    ):

                        part = sentence[
                            start:start + self.chunk_size
                        ]

                        chunks.append({
                            "chunk_id": chunk_id,
                            "text": part,
                            "source": page["source"],
                            "page_number": page["page_number"]
                        })

                        chunk_id += 1

                    continue

                additional_length = (
                    len(sentence) + 1
                    if current_sentences
                    else len(sentence)
                )

                if current_length + additional_length > self.chunk_size:

                    # Save the current chunk.
                    chunk_text = " ".join(current_sentences)

                    chunks.append({
                        "chunk_id": chunk_id,
                        "text": chunk_text,
                        "source": page["source"],
                        "page_number": page["page_number"]
                    })

                    chunk_id += 1

                    # Prepare sentence-based overlap.
                    overlap_sentences = []
                    overlap_length = 0

                    for previous_sentence in reversed(current_sentences):

                        required_length = (
                            len(previous_sentence)
                            + (1 if overlap_sentences else 0)
                        )

                        if (
                            overlap_length + required_length
                            > self.chunk_overlap
                        ):
                            break

                        overlap_sentences.insert(
                            0,
                            previous_sentence
                        )

                        overlap_length += required_length

                    # Remove oldest overlap sentences if necessary.
                    # This guarantees that the next sentence fits.
                    while overlap_sentences:

                        overlap_length = (
                            sum(len(s) for s in overlap_sentences)
                            + len(overlap_sentences) - 1
                        )

                        required_total = (
                            overlap_length
                            + 1
                            + len(sentence)
                        )

                        if required_total <= self.chunk_size:
                            break

                        overlap_sentences.pop(0)

                    current_sentences = overlap_sentences

                    current_length = (
                        sum(len(s) for s in current_sentences)
                        + max(0, len(current_sentences) - 1)
                    )

                # Add the new sentence.
                current_sentences.append(sentence)

                current_length += (
                    len(sentence)
                    + (1 if len(current_sentences) > 1 else 0)
                )

            # Save remaining sentences.
            if current_sentences:

                chunk_text = " ".join(current_sentences)

                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "source": page["source"],
                    "page_number": page["page_number"]
                })

                chunk_id += 1

        return chunks