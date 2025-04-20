from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from dotenv import load_dotenv
load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION")

def init_collection():
    if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=384,  
                distance=models.Distance.COSINE
            )
        )

def insert_document(id: int, embedding: list[float], payload: dict):
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=id,
                vector=embedding,
                payload=payload
            )
        ]
    )

def search_similar(text_embedding: list[float], top_k: int = 5):
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=text_embedding,
        limit=top_k
    )
    return results
