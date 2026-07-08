from backend.main import download_audio
try:
    download_audio("https://www.youtube.com/watch?v=_GXbXU4g_CA", "temp_audio/test_dl2")
    print("Success")
except Exception as e:
    print(f"Error: {e}")
