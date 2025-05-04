import requests
import os
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

def get_embedding(text: str) -> list[float]:
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2",
            headers={"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"},
            json={"inputs": text},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Embedding error:", e)
        return []
