import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv("backend/.env")
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

response_schema = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "options": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "title": types.Schema(type=types.Type.STRING),
                    "description": types.Schema(type=types.Type.STRING),
                    "lyria_prompt": types.Schema(type=types.Type.STRING)
                },
                required=["title", "description", "lyria_prompt"]
            )
        )
    },
    required=["options"]
)

try:
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents="Hello",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.7
        )
    )
    print("Success!")
except Exception as e:
    import traceback
    traceback.print_exc()
