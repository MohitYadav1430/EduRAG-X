from google import genai

from src.edurag_x.config.settings import GEMINI_API_KEY


class GroundedAnswerGenerator:

    def __init__(self):

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = "gemini-3.6-flash"

    def generate_answer(self, question, retrieved_chunks):

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        if not retrieved_chunks:
            return (
                "I could not find relevant information "
                "in the uploaded documents."
            )

        context_parts = []

        for chunk in retrieved_chunks:

            context_parts.append(
                f"""
SOURCE: {chunk['source']}
PAGE: {chunk['page_number']}

DOCUMENT CONTENT:
{chunk['text']}
"""
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are EduRAG-X, an evidence-aware AI teaching assistant.

Your task is to answer the student's question using
the retrieved document evidence.

STRICT EVIDENCE RULES:

1. Use only the information explicitly supported
   by the provided document context.

2. Every factual claim must have a citation.

3. Use this exact citation format:
   [Source: filename, Page: number]

4. Never invent filenames or page numbers.

5. Do not treat a citation as proof unless the
   cited document content actually supports the claim.

6. Do not introduce outside knowledge as if it
   came from the uploaded documents.

7. Do not make unsupported conclusions or assumptions.

8. If the document does not explicitly establish
   a conclusion, do not present that conclusion as
   a documented fact.

9. If you provide an inference, clearly label it
   as "Inference" and explain that it is not
   explicitly stated in the document.

10. If sufficient evidence is unavailable, clearly say:
    "The uploaded documents do not provide sufficient
    evidence to answer this question."

11. Do not force an answer when evidence is insufficient.

ANSWER STRUCTURE:

- Direct Answer
- Supporting Evidence
- Important Limitations (if applicable)

STUDENT QUESTION:
{question}

RETRIEVED DOCUMENT CONTEXT:
{context}

Now generate a clear, student-friendly,
evidence-grounded answer.
"""

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response.")

            return response.text

        except Exception as error:

            raise RuntimeError(
                f"Answer generation failed: {error}"
            ) from error
