import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

def main():
    client = genai.Client()
    print("Uploading video...")
    video_file = client.files.upload(file='ioniq6.mp4')
    
    while True:
        file_info = client.files.get(name=video_file.name)
        if file_info.state.name == 'ACTIVE':
            break
        elif file_info.state.name == 'FAILED':
            raise Exception("Video processing failed.")
        time.sleep(2)
        
    prompt = "describe the visual contents, action, pacing, color grading, and overall mood of this video in extreme detail."
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=[video_file, prompt]
    )
    
    print(response.text)

if __name__ == "__main__":
    main()
