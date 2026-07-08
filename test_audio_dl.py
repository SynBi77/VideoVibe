from backend.main import download_audio
import sys

print("Testing audio dl...")
sys.stdout.flush()
try:
    path, title, dur = download_audio("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "temp_audio/test_audio")
    print(f"Success! {path} {title} {dur}")
except Exception as e:
    print(f"Error: {e}")
