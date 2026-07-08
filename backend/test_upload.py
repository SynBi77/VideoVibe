import os
from google import genai
import dotenv

dotenv.load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

with open("dummy.txt", "w") as f:
    f.write("hello")
    
f = client.files.upload(file="dummy.txt")
print(f"File uploaded: {f.name}")
client.files.delete(name=f.name)
print("Deleted.")
