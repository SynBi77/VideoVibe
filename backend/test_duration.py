import os
import replicate
from dotenv import load_dotenv

load_dotenv()
try:
    output = replicate.run(
        "meta/musicgen:b05b1dff1d8c6dc63d14b0cdb405273760fb26ceec95fba7348e351fbde5195e",
        input={
            "prompt": "Test ambient music",
            "model_version": "stereo-large",
            "output_format": "mp3",
            "duration": 35,
            "temperature": 0.85
        }
    )
    print("SUCCESS")
    print(output)
except Exception as e:
    print(f"FAILED: {e}")
