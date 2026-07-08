from backend.main import download_audio
import sys

print("Testing audio dl...")
sys.stdout.flush()
try:
    path, title, dur = download_audio("https://www.youtube.com/shorts/aKWRfbo_q1s", "temp_audio/test_audio_2")
    print(f"Success! {path} {title} {dur}")
except Exception as e:
    print(f"Error: {e}")
