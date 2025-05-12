from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from dotenv import load_dotenv
import uuid
import hashlib
load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION")


def check_qdrant_connection():
    try:
        client.get_collections()
        return True
    except Exception as e:
        print(f"Qdrant connection failed: {e}")
        return False

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



def generate_consistent_id(email: str) -> int:
    """
    Generate a consistent ID for an email using SHA-256 hash.
    Returns a positive integer that's deterministic for the same email.
    """
    # Create a SHA-256 hash of the email
    hash_object = hashlib.sha256(email.encode())
    # Convert to integer and take modulo to ensure it's within Qdrant's range
    return int(hash_object.hexdigest(), 16) % (2**63 - 1)

def insert_resume_embedding(embedding: list[float], payload: dict):
    # Generate a deterministic ID using SHA-256
    resume_id = generate_consistent_id(payload["email"])
  
    try:
        result = client.upsert(
            collection_name="resume_embeddings",
            points=[
                models.PointStruct(
                    id=resume_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )
        return result
    except Exception as e:
        print(f"[INSERT] Error inserting embedding: {e}")
        return None

def search_similar(text_embedding: list[float], top_k: int = 5):
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=text_embedding,
        limit=top_k
    )
    return results

def list_collections():
    """
    List all available collections in the Qdrant database.
    Returns a list of collection names.
    """
    try:
        collections = client.get_collections()
        print("Available collections:")
        for collection in collections.collections:
            print(f"- {collection.name}")
        return [c.name for c in collections.collections]
    except Exception as e:
        print(f"Error listing collections: {e}")
        return []

def delete_collection(collection_name: str):
    """
    Delete a collection from Qdrant database.
    Args:
        collection_name (str): Name of the collection to delete
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        # First check if collection exists
        collections = [c.name for c in client.get_collections().collections]
        if collection_name not in collections:
            print(f"Collection '{collection_name}' does not exist")
            return False
            
        # Delete the collection
        client.delete_collection(collection_name=collection_name)
        print(f"Successfully deleted collection: {collection_name}")
        return True
    except Exception as e:
        print(f"Error deleting collection '{collection_name}': {e}")
        return False

def create_collection(collection_name: str):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=384,  
            distance=models.Distance.COSINE
        )
    )

def get_resume_embedding_by_email(user_email: str):
    resume_id = generate_consistent_id(user_email)
    try:
        result = client.retrieve(
            collection_name="resume_embeddings",
            ids=[resume_id],  
            with_vectors=True, 
        )
        if result and result[0] and result[0].vector:
            print(f"[GET] Found vector of length: {len(result[0].vector)}")
            return result[0].vector  
        return None
    except Exception as e:
        print(f"[GET] Error retrieving embedding: {e}")
        return None

if __name__ == "__main__":
    # Test the connection and list collections
    if check_qdrant_connection():
        print("Successfully connected to Qdrant!")
        print("\nAvailable collections:")
        list_collections()

        result = get_resume_embedding_by_email("demouser17@gmail.com")
        print(result)

     
       
    else:
        print("Failed to connect to Qdrant")
      
