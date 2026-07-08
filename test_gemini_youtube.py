import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv("backend/.env")
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=["Please tell me what happens in this video: https://www.youtube.com/shorts/Pn5-EZxajro"]
)

print(response.text)
