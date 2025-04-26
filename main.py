from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
from typing import List, Dict, Any
from agents.recommender_agent import recommender_agent
from agents.explainer_agent import explainer_agent
from agents.Tasks import create_recommendation_task, create_explanation_task
from crewai import Crew
from db import fetch_resume_data
import bson
import datetime

from fetch_recommendations import resume_cache

app = FastAPI()


job_obj = {
    "Job Title": "Senior Full-Stack MERN Developer (React / Node / JavaScript)",
    "Company Name": "Orbital Installation Technologies, LLC.",
    "Location": "Remote",
    "Job Type": "Contract or Full-Time",
    "Salary": "$50,000 - $74,999 USD",
    "Posted Date": "9 days ago",
    "Application Deadline": "May 9th, 2025",
    "Key Requirements": [
        "Strong experience with React, Node.js, MongoDB",
        "You’ve shipped production MERN apps before — full cycle, not just small pieces",
        "Comfortable designing API routes, data models, and component structure",
        "Clean, maintainable code and good git hygiene",
        "You’re opinionated about architecture but not religious — you know trade-offs",
        "Comfortable working async and remote — you don’t need hand-holding"
    ],
    "Bonus Skills": [
        "Experience with AWS (Lambda, CloudFront, S3, etc.)",
        "React Native or mobile-first development experience",
        "Integration with third-party APIs (auth, maps, OCR, image validation, etc.)"
    ],
    "Stack": [
        "React (Context API, moving toward modularization)",
        "Node.js + Express",
        "MongoDB",
        "REST APIs",
        "AWS (Lambda, S3, etc.)"
    ],
    "Description": "We’re looking for a senior-level full-stack dev who knows the MERN stack inside out and is still very much in the code.\nThis isn’t a management role. You’ll be contributing directly — writing code, shaping architecture, and helping us build out real product features. You’ll work closely with our IT technical team. You’ll have a voice in decisions, but we expect you to ship and stay hands-on.\nWhat You’ll Be Working On:\nWe’re building a modern workforce management platform for field service teams — real-world use cases like install tracking, dispatch, mobile work orders, photo verification, etc. It’s not a toy app or another dashboard overlay — we’re solving actual ops problems with a lean team and strong stack.",
    "How to Apply": [
        "A link to your GitHub or portfolio (real work, not tutorial clones)",
        "What you're best at, and what kind of problems you like solving",
        "Your availability and rate (hourly or monthly)",
        "Optional: something in JavaScript that drives you nuts and how you deal with it"
    ],
    "Direct Link": None,
    "Match Score": 52
}

recommended_jobs_cache = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_crew_output(raw):
    s = raw.strip()
    if s.startswith('```json'):
        s = s[len('```json'):].strip()
    if s.startswith('```'):
        s = s[len('```'):].strip()
    if s.endswith('```'):
        s = s[:-3].strip()
    return s

def run_crew_for_email(email: str):
    recommendation_task = create_recommendation_task(email)
    recommender_crew = Crew(
        agents=[recommender_agent],
        tasks=[recommendation_task],
        verbose=True
    )
    result = recommender_crew.kickoff(inputs={"email": email})
    jobs_str = result.final_answer if hasattr(result, "final_answer") else str(result.raw)
    jobs_str = clean_crew_output(jobs_str)
    try:
        jobs = json.loads(jobs_str)
    except Exception:
        jobs = []
    return jobs

def sanitize_resume(resume):
    if isinstance(resume, dict):
        return {k: sanitize_resume(v) for k, v in resume.items()}
    elif isinstance(resume, list):
        return [sanitize_resume(i) for i in resume]
    elif hasattr(resume, 'binary') or 'bson' in str(type(resume)):
        return str(resume)
    elif isinstance(resume, (datetime.datetime, datetime.date)):
        return resume.isoformat()
    else:
        return resume

def run_crew_for_explanation(job_object, user_resume):
    user_resume = sanitize_resume(user_resume)
    explanation_task = create_explanation_task(job_object, user_resume)
    explainer_crew = Crew(
        agents=[explainer_agent],
        tasks=[explanation_task],
        verbose=True
    )
    result = explainer_crew.kickoff(inputs={"job_object": job_object, "user_resume": user_resume})
    explanation = result.final_answer if hasattr(result, "final_answer") else str(result.raw)
    return explanation

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
            jobs = run_crew_for_email(user_email)
            recommended_jobs_cache = jobs

        if not jobs:
            raise HTTPException(status_code=500, detail="Failed to extract job recommendations.")

        return JSONResponse(jobs)

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain-job-fit")
async def explain_job_fit(request: Request):
    """
    API to run the explainer agent for a given job title and company.
    Expects JSON: {"job_title": ..., "company_name": ..., "user_email": ...}
    """
    data = await request.json()
    job_title = data.get("job_title")
    company_name = data.get("company_name")
    user_email = data.get("user_email")

    if not job_title or not company_name or not user_email:
        raise HTTPException(status_code=400, detail="Missing job_title, company_name, or user_email.")

    # job_obj = find_job_by_title_and_company(job_title, company_name)
    # if not job_obj:
    #     raise HTTPException(status_code=404, detail="Job not found in recommendations cache.")

    user_resume = fetch_resume_data(user_email)
    if not user_resume:
        raise HTTPException(status_code=404, detail="Resume not found in cache.")

    explanation = run_crew_for_explanation(job_obj, user_resume)
    return JSONResponse({"explanation": explanation})

@app.websocket("/ws/recommendations")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        email = json.loads(data).get("email", "demouser17@gmail.com")
        jobs = run_crew_for_email(email)

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
                    # Get email from payload.job
                    email = job.get("email") if job else None
                    if not email:
                        reply = "[ERROR] No email provided in job payload."
                    else:
                        user_resume = fetch_resume_data(email)
                        job_obj = find_job_by_title_and_company(job.get("title"), job.get("company"))

                        print(job_obj)
                        
                        if not user_resume:
                            reply = f"[ERROR] Resume not found for {email}."
                        else:
                            # Run explainer crew agent
                            explanation = run_crew_for_explanation(job_obj, user_resume)
                            reply = explanation
                elif msg_type == "suggest":
                    reply = f"[MOCK] To improve your application for {job.get('title', 'this job')}, consider tailoring your resume and highlighting relevant skills."
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