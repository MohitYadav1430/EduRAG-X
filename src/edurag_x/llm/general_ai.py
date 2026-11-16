import time

from google import genai
from google.genai import errors
from src.edurag_x.config.settings import GEMINI_API_KEY


class GeneralAIEngine:

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = "gemini-3.6-flash"

    def generate_answer(self, question, learning_mode="Beginner"):

        instructions = {
            "Beginner": "Explain in simple language with examples.",
            "Intermediate": "Give a balanced technical explanation.",
            "Advanced": "Provide a detailed technical explanation.",
            "Exam": "Give a structured, exam-oriented answer.",
            "Interview": "Give an interview-oriented answer."
        }

        teaching_instruction = instructions.get(
            learning_mode,
            instructions["Beginner"]
        )

        prompt = f"""
        You are EduRAG-X, an intelligent AI teaching assistant.

        Explain concepts accurately and clearly.
        Use practical examples where useful.
        Never invent facts or references.
        Admit uncertainty when necessary.

        Learning Mode: {learning_mode}
        Instructions: {teaching_instruction}

        Student Question:
        {question}
        """

        for attempt in range(3):

            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )

                return response.text

            except errors.ServerError:
                if attempt == 2:
                    return "Gemini server is currently busy. Please try again later."

                time.sleep(2 ** attempt)

            except errors.APIError as error:
                return f"Gemini API error: {error}"

            except Exception as error:
                return f"Unexpected connection error: {error}"


