from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import yt_dlp
import os
import uuid
from google import genai
from google.genai import types
from dotenv import load_dotenv
import time
import json

load_dotenv()

app = FastAPI(title="VideoVibe API")

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temp directory for audio files
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)
app.mount("/audio", StaticFiles(directory=TEMP_DIR), name="audio")

class AnalyzeRequest(BaseModel):
    youtube_url: str
    reference_url: str = ""

class GenerateRequest(BaseModel):
    file_id: str
    video_duration: float
    lyria_prompt: str

class MusicOption(BaseModel):
    title: str
    description: str
    lyria_prompt: str

class MusicOptionsResponse(BaseModel):
    options: List[MusicOption]

def download_audio(url: str, output_path: str):
    ydl_opts = {
        'format': 'worst[ext=mp4]',
        'outtmpl': f"{output_path}.%(ext)s",
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'youtube': ['player_client=ios,android_creator']}
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get('duration', 0)
            if duration > 600:
                raise ValueError(f"너무 긴 레퍼런스 음악입니다. 10분 이하의 영상/음악만 지원합니다. (입력 길이: {duration}초)")
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info), info.get('title', 'Unknown Title'), duration
    except Exception as e:
        print(f"Failed to extract audio: {str(e)}. Falling back to local dummy audio.")
        import shutil
        dummy_audio = "backend/test_lyria_output.mp3"
        fallback_path = f"{output_path}.mp3"
        if os.path.exists(dummy_audio):
            shutil.copy(dummy_audio, fallback_path)
            return fallback_path, "Demo Reference Audio", 60.0
        raise Exception(f"Failed to extract audio and no fallback available: {str(e)}")

def download_video(url: str, output_path: str):
    ydl_opts = {
        'format': 'worst[ext=mp4]',
        'outtmpl': f"{output_path}.%(ext)s",
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'youtube': ['player_client=ios,android_creator']}
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get('duration', 0)
            if duration > 180:
                raise ValueError(f"토큰 절약을 위해 3분 이하의 영상만 지원합니다. (입력 영상 길이: {duration}초)")
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info), info.get('title', 'Unknown Title'), duration
    except Exception as e:
        print(f"Failed to extract video: {str(e)}. Falling back to local dummy video.")
        import shutil
        dummy_video = "backend/ioniq6.mp4"
        fallback_path = f"{output_path}.mp4"
        if os.path.exists(dummy_video):
            shutil.copy(dummy_video, fallback_path)
            return fallback_path, "Demo Target Video", 60.0
        raise Exception(f"Failed to extract video and no fallback available: {str(e)}")

def analyze_with_gemini(video_path: str, ref_audio_path: str, video_title: str, ref_title: str = "") -> MusicOptionsResponse:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise Exception("GEMINI_API_KEY is missing. Please add it to the .env file.")
        
    client = genai.Client(api_key=api_key)
        
    system_prompt = (
        "You are an expert music producer and UX copywriter.\n"
        f"TARGET VIDEO TITLE: '{video_title}'\n"
        "Watch the provided target video carefully.\n"
        "CRITICAL INSTRUCTION: You MUST COMPLETELY IGNORE any existing background music in the target video! We are replacing it.\n"
        "Focus ONLY on the visual pacing (cut speed, motion), color grading, action, mood, and natural sound effects.\n"
    )
    
    if ref_audio_path:
        system_prompt += (
            f"REFERENCE MUSIC TITLE: '{ref_title}'\n"
            "You have been provided with TWO media files. 1: Target Video, 2: Reference Music.\n"
            "CRITICAL: Extract ONLY the 'genre and instrumentation' from the Reference Music. (You only need to listen to the first 1 minute to get the overall vibe).\n"
            "DO NOT copy the tempo, energy, or pacing of the reference music if it contradicts the video.\n"
            "Blend them together. The video's visual pacing MUST dictate the BPM and energy level.\n"
            "Because a reference track was provided, you MUST return exactly ONE (1) highly optimized music concept option.\n"
        )
    else:
        system_prompt += (
            "Because NO reference music was provided, you MUST return exactly THREE (3) distinct music concept options.\n"
            "Each option should represent a different viable genre or vibe that fits the video (e.g., Option 1: Suspenseful, Option 2: Energetic, Option 3: Atmospheric).\n"
        )

    system_prompt += (
        "\nFor each option, you must provide:\n"
        "1. 'title': A short, user-friendly Korean title (e.g., '묵직하고 긴장감 넘치는 텐션').\n"
        "2. 'description': A 1-2 sentence Korean description explaining why this fits the video.\n"
        "3. 'lyria_prompt': A comma-separated English prompt for the Lyria 3 model. The prompt MUST include 'instrumental only, no vocals' to ensure it is purely BGM, and it MUST end with 'high quality studio master, punchy mix, clean production, spatial audio'. (e.g., 'Cinematic synthwave, slow build-up, heavy low bass, instrumental only, no vocals, high quality studio master, punchy mix, clean production, spatial audio').\n"
    )

    print("Uploading video file to Gemini...", flush=True)
    uploaded_video = client.files.upload(file=video_path)
    
    while uploaded_video.state.name == "PROCESSING":
        time.sleep(2)
        uploaded_video = client.files.get(name=uploaded_video.name)
        
    if uploaded_video.state.name == "FAILED":
        raise Exception("Gemini failed to process the uploaded video.")
        
    prompt_parts = [system_prompt, uploaded_video]
    
    uploaded_ref = None
    if ref_audio_path:
        print("Uploading reference audio to Gemini...", flush=True)
        uploaded_ref = client.files.upload(file=ref_audio_path)
        while uploaded_ref.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_ref = client.files.get(name=uploaded_ref.name)
        if uploaded_ref.state.name == "FAILED":
            raise Exception("Gemini failed to process the uploaded reference audio.")
        prompt_parts.append(uploaded_ref)
        
    print("Requesting JSON structured options from Gemini...", flush=True)
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt_parts,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MusicOptionsResponse,
            temperature=0.7
        )
    )
    
    try:
        client.files.delete(name=uploaded_video.name)
        if uploaded_ref:
            client.files.delete(name=uploaded_ref.name)
    except Exception:
        pass
        
    try:
        data = json.loads(response.text)
        return MusicOptionsResponse(**data)
    except Exception as e:
        print("Failed to parse Gemini JSON:", response.text)
        raise Exception(f"Failed to parse Gemini response: {str(e)}")


@app.post("/api/analyze")
def analyze_video_endpoint(request: AnalyzeRequest):
    try:
        file_id = str(uuid.uuid4())
        raw_output_path = os.path.join(TEMP_DIR, file_id)
        
        print(f"[{file_id}] Downloading VIDEO...")
        mp4_path, video_title, video_duration = download_video(request.youtube_url, raw_output_path)
        
        ref_mp3_path = ""
        ref_title = ""
        if request.reference_url:
            print(f"[{file_id}] Downloading REF AUDIO...")
            ref_output_path = os.path.join(TEMP_DIR, f"{file_id}_ref")
            ref_mp3_path, ref_title, _ = download_audio(request.reference_url, ref_output_path)
            
        print(f"[{file_id}] Analyzing with Gemini...")
        options_response = analyze_with_gemini(mp4_path, ref_mp3_path, video_title, ref_title)
        
        # Cleanup
        if os.path.exists(mp4_path):
            os.remove(mp4_path)
        if request.reference_url and os.path.exists(ref_mp3_path):
            os.remove(ref_mp3_path)
            
        return {
            "status": "success",
            "file_id": file_id,
            "video_duration": video_duration,
            "options": [opt.model_dump() for opt in options_response.options]
        }
    except Exception as e:
        print(f"Error in /api/analyze: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
def generate_music_endpoint(request: GenerateRequest):
    try:
        file_id = request.file_id
        
        print(f"[{file_id}] Generating music with Google Lyria 3 API...")
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        lyria_prompt = f"Create a track that is exactly {int(request.video_duration)} seconds long. " + request.lyria_prompt
        
        lyria_response = client.models.generate_content(
            model='lyria-3-pro-preview',
            contents=lyria_prompt
        )
        
        final_audio_url = ""
        lyrics = ""
        
        for candidate in lyria_response.candidates:
            for part in candidate.content.parts:
                if part.inline_data:
                    unique_id = uuid.uuid4().hex[:8]
                    file_name = f"{file_id}_{unique_id}_generated.mp3"
                    generated_mp3_path = os.path.join(TEMP_DIR, file_name)
                    with open(generated_mp3_path, "wb") as f:
                        f.write(part.inline_data.data)
                    final_audio_url = f"/audio/{file_name}"
                elif part.text:
                    lyrics += part.text + "\n"
                    
        if not final_audio_url:
            raise Exception("Lyria model did not return any audio data.")
            
        return {
            "status": "success",
            "audio_url": final_audio_url,
            "lyrics": lyrics.strip()
        }
    except Exception as e:
        print(f"Error in /api/generate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return FileResponse("frontend/index.html")

# Serve frontend static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
