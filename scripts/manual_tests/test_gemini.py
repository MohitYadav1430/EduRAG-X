from google import genai
from src.edurag_x.config.settings import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Explain Artificial Intelligence in three simple sentences."
)

print("\nEduRAG-X Gemini Connection Test")
print("--------------------------------")
print(response.text)
