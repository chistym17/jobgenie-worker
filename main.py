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
from agents.Tasks import create_recommendation_task, create_explanation_task, create_resume_advice_task
from agents.initialize_crews import run_crew_for_recommendations, run_crew_for_explanation, run_crew_for_advice
from crewai import Crew
from db import fetch_resume_data
import bson
import datetime

from fetch_recommendations import resume_cache

app = FastAPI()

recommended_jobs_cache = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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

        # Use cache if available
        if recommended_jobs_cache is not None:
            jobs = recommended_jobs_cache
        else:
            jobs = run_crew_for_recommendations(user_email)
            recommended_jobs_cache = jobs

        if not jobs:
            raise HTTPException(status_code=500, detail="Failed to extract job recommendations.")

        return JSONResponse(jobs)

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/recommendations")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        email = json.loads(data).get("email", "demouser17@gmail.com")
        jobs = run_crew_for_recommendations(email)

        if not jobs:
            await websocket.send_text(json.dumps({"error": "Failed to extract job recommendations"}))
            await websocket.close()
            return

        for job in jobs:
            await websocket.send_text(json.dumps(job))
            await asyncio.sleep(0.1)
        while True:
            msg = await websocket.receive_text()
            await websocket.send_text(json.dumps({"echo": msg}))
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)