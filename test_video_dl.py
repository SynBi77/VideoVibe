from backend.main import download_video
import sys
import threading
import traceback
import time

def run():
    print("Testing video dl...")
    sys.stdout.flush()
    try:
        path, title, dur = download_video("https://www.youtube.com/shorts/aKWRfbo_q1s", "temp_audio/test_video")
        print(f"Success! {path} {title} {dur}")
    except Exception as e:
        print(f"Error: {e}")

t = threading.Thread(target=run)
t.start()
t.join(timeout=10)
if t.is_alive():
    print("HUNG!")
