from src.edurag_x.llm.general_ai import GeneralAIEngine

assistant = GeneralAIEngine()

question = "Explain DBMS normalization with an example."

answer = assistant.generate_answer(
    question=question,
    learning_mode="Beginner"
)

print("\n========== EduRAG-X ==========")
print(answer)
print("==============================")
