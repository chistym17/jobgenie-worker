from db import fetch_all_jobs, fetch_resume_data
from fastapi import APIRouter
from qdrant_service import search_similar
from embedder import get_embedding
import numpy as np
import re

router = APIRouter()

def chunk_text(text, max_length=500):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += " " + sentence
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    return chunks

def extract_relevant_resume_text(resume):
    # Extract main fields for embedding
    parts = []
    # Skills
    skills = resume.get('skills', [])
    if skills:
        parts.append('Skills: ' + ', '.join(skills))
    # Experience
    for exp in resume.get('experience', []):
        exp_str = f"{exp.get('position', '')} at {exp.get('company', '')}. {exp.get('description', '')} ({exp.get('duration', '')})"
        parts.append('Experience: ' + exp_str)
    # Projects
    for proj in resume.get('projects', []):
        proj_str = f"{proj.get('title', '')} ({proj.get('tech_stack', '')}): {proj.get('description', '')}"
        parts.append('Project: ' + proj_str)
    # Education (if present)
    for edu in resume.get('education', []):
        edu_str = f"{edu.get('degree', '')} at {edu.get('institution', '')} ({edu.get('year', '')})"
        parts.append('Education: ' + edu_str)
    # Certifications (if present)
    for cert in resume.get('certifications', []):
        cert_str = cert.get('title', '')
        if cert_str:
            parts.append('Certification: ' + cert_str)
    return '\n'.join(parts)

@router.get("/fetch_recommendations")

def fetch_recommendations(user_email: str):
    print("Fetching recommendations for user:", user_email)
    resume = fetch_resume_data(user_email)
    if not resume:
        return []
        
    relevant_text = extract_relevant_resume_text(resume)
    chunks = chunk_text(relevant_text, max_length=500)
    embeddings = []
    for chunk in chunks:
        if chunk.strip():
            emb = get_embedding(chunk)
            embeddings.append(emb)
    if embeddings:
        embedding = np.mean(embeddings, axis=0).tolist()
    else:
        embedding = []
    fetched_chunks = search_similar(embedding)

    print(fetched_chunks)

    return fetched_chunks



if __name__ == "__main__":
    fetch_recommendations("demouser17@gmail.com")
