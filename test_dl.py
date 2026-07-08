from backend.main import download_video
try:
    download_video("https://www.youtube.com/watch?v=_GXbXU4g_CA", "temp_video/test_dl")
    print("Success")
except Exception as e:
    print(f"Error: {e}")
