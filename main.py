from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
from typing import List, Dict, Any
from agents.recommender_agent import recommender_agent
from agents.Tasks import create_recommendation_task
from crewai import Crew

app = FastAPI()

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

@app.post("/recommendations")
async def get_recommendations(request: Request):
    """
    Endpoint to get job recommendations.
    """
    try:
        data = await request.json()
        user_email = data.get("email", "demouser17@gmail.com")
        jobs = run_crew_for_email(user_email)

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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)