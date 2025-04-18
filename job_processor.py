from embedder import get_embedding
from qdrant_service import init_collection, insert_document
from db import fetch_all_jobs
import json

def process_and_upload_jobs():
    """Fetch jobs from MongoDB, create embeddings, and upload to Qdrant"""
    init_collection()
    
    jobs = fetch_all_jobs()
    print(f"Found {len(jobs)} jobs in MongoDB")
    

if __name__ == '__main__':
    process_and_upload_jobs()