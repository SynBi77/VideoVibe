import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

try:
    print("Calling Lyria 3 Clip model...")
    response = client.models.generate_content(
        model='lyria-3-clip-preview',
        contents="Cyberpunk electro house, energetic, futuristic, heavy driving bassline"
    )
    for i, candidate in enumerate(response.candidates):
        for j, part in enumerate(candidate.content.parts):
            print(f"Candidate {i}, Part {j}:")
            if part.inline_data:
                print(f"  Audio found! MIME type: {part.inline_data.mime_type}")
                print(f"  Audio length: {len(part.inline_data.data)} bytes")
                with open(f"test_lyria_output.mp3", "wb") as f:
                    f.write(part.inline_data.data)
                print("  Saved as test_lyria_output.mp3")
            elif part.text:
                print(f"  Text found: {part.text}")
            else:
                print(f"  Other part: {part}")
except Exception as e:
    print(f"Error: {e}")
