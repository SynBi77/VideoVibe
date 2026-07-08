import os
from google import genai
import dotenv

dotenv.load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Explain how AI works in a few words"
    )
    print("SUCCESS")
    print(response.text)
except Exception as e:
    print(f"FAILED: {e}")
