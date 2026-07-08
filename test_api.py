import requests
import sys

print("Testing API...")
sys.stdout.flush()
try:
    resp = requests.post('http://127.0.0.1:8000/api/analyze', json={
        "youtube_url": "https://www.youtube.com/shorts/aKWRfbo_q1s",
        "reference_url": "https://www.youtube.com/shorts/aKWRfbo_q1s"
    })
    print("Status code:", resp.status_code)
    print("Response:", resp.json())
except Exception as e:
    print(f"Error: {e}")
