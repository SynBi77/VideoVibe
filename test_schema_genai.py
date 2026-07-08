import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv("backend/.env")
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

schema_dict = {
    "type": "OBJECT",
    "properties": {
        "options": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING"},
                    "description": {"type": "STRING"},
                    "lyria_prompt": {"type": "STRING"}
                },
                "required": ["title", "description", "lyria_prompt"]
            }
        }
    },
    "required": ["options"]
}

try:
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents="Hello",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=types.Schema(**schema_dict),
            temperature=0.7
        )
    )
    print("Success!")
except Exception as e:
    import traceback
    traceback.print_exc()
