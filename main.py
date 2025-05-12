from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
from typing import List, Dict, Any
from agents.recommender_agent import recommender_agent
from agents.explainer_agent import explainer_agent
from agents.resume_advisor_agent import resume_advisor_agent
from agents.initialize_crews import run_crew_for_explanation, run_crew_for_advice
from crewai import Crew
from db import fetch_resume_data
import bson
import datetime
from db import check_mongodb_connection
from utils.qdrant_service import check_qdrant_connection
from fetch_recommendations import resume_cache
from celery_tasks.recommendation_task import generate_recommendations_task
from celery.result import AsyncResult
from celery_app import celery_app

app = FastAPI()

recommended_jobs_cache = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    mongodb_connection = check_mongodb_connection()
    qdrant_connection = check_qdrant_connection()
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "JobGenie Worker",
        "mongodb_connection": mongodb_connection,
        "qdrant_connection": qdrant_connection
    }



def find_job_by_title_and_company(job_title: str, company_name: str):
    """
    Search the recommended_jobs_cache for a job matching the given title and company name.
    Returns the matched job object or None if not found.
    """
    global recommended_jobs_cache
    if not recommended_jobs_cache:
        return None
    for job in recommended_jobs_cache:
        title = job.get("Job Title", "").strip().lower()
        company = job.get("Company Name", "").strip().lower()
        if title == job_title.strip().lower() and company == company_name.strip().lower():
            return job
    return None

@app.post("/recommendations")
async def get_recommendations(request: Request):
    """
    Endpoint to get job recommendations.
    """
    global recommended_jobs_cache
    try:
        data = await request.json()
        user_email = data.get("email", "demouser17@gmail.com")

        if recommended_jobs_cache is not None:
            jobs = recommended_jobs_cache
            return {"jobs": jobs, "message": "Recommendation task completed"}
        else:
            task = generate_recommendations_task.delay(user_email)
            recommended_jobs_cache = task

        return {"task_id": task.id, "message": "Recommendation task submitted"}

    
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recommendations/{task_id}")
def get_task_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if result.ready():
        return {"status": "completed", "data": result.result}
    return {"status": "pending"}


@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                print(payload)
                msg_type = payload.get("type", "general")
                message = payload.get("message", "")
                job = payload.get("job", None)
                if msg_type == "explain":
                    email = job.get("email") if job else None
                    if not email:
                        reply = "[ERROR] No email provided in job payload."
                    else:
                        user_resume = fetch_resume_data(email)
                        job_obj = find_job_by_title_and_company(job.get("title"), job.get("company"))

                        if not user_resume:
                            reply = f"[ERROR] Resume not found for {email}."
                        else:
                            explanation = run_crew_for_explanation(job_obj, user_resume)
                            reply = explanation
                elif msg_type == "suggest":
                    email = job.get("email") if job else None
                    if not email:
                        reply = "[ERROR] No email provided in job payload."
                    else:
                        user_resume = fetch_resume_data(email)
                        job_obj = find_job_by_title_and_company(job.get("title"), job.get("company"))
                        if not user_resume:
                            reply = f"[ERROR] Resume not found for {email}."
                        else:
                            advice = run_crew_for_advice(job_obj, user_resume)
                            reply = advice
                else:
                    reply = f"[MOCK] You said: {message}"
            except Exception as e:
                reply = f"[MOCK] Sorry, I could not process your message. ({e})"
            await websocket.send_json({"reply": reply})
    except Exception as e:
        print(f"WebSocket error (chat): {e}")
        await websocket.close()


# @app.post("/compute-embeddings")
# async def compute_embeddings(request: Request):
#     """
#     Endpoint to trigger resume embedding computation
#     """
#     try:
#         data = await request.json()
#         user_email = data.get("email")
        
#         if not user_email:
#             raise HTTPException(status_code=400, detail="Email is required")
            
#         # Check if resume exists
#         resume = fetch_resume_data(user_email)
#         if not resume:
#             raise HTTPException(status_code=404, detail="Resume not found")
            
#         # Trigger the background task
#         task = compute_resume_embedding_task.delay(user_email)
        
#         return {
#             "task_id": task.id,
#             "message": "Embedding computation task submitted"
#         }
        
#     except Exception as e:
#         print(f"Error triggering embedding computation: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)