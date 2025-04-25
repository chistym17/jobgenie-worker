from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
import json
from agents.recommender_agent import recommender_agent
from agents.Tasks import create_recommendation_task
from crewai import Crew

app = FastAPI()

def get_job_recommendations(email):
    return [
        {
            "title": "Senior Full-Stack MERN Developer (React / Node / JavaScript)",
            "company": "Orbital Installation Technologies, LLC.",
            "location": "Remote",
            "job_type": "Contract or Full-Time",
            "salary": "$50,000 - $74,999 USD",
            "posted_date": "9 days ago",
            "application_deadline": "May 9th, 2025",
            "key_requirements": "Strong experience with React, Node.js, MongoDB; Shipped production MERN apps before; Comfortable designing API routes, data models, and component structure; Clean code and good git hygiene; Opinionated about architecture; Comfortable working async and remote.",
            "bonus_skills": "Experience with AWS, React Native, Integration with third-party APIs.",
            "stack": "React, Node.js, Express, MongoDB, REST APIs, AWS",
            "description": "Looking for a senior-level full-stack dev who knows the MERN stack inside out and is still very much in the code. Building a modern workforce management platform for field service teams.",
            "how_to_apply": "Send a quick note with a link to your GitHub or portfolio, your best skills, your availability and rate, and optionally, something in JavaScript that drives you nuts.",
            "direct_link": None,
            "match_score": "52.30%"
        }
    ]

@app.websocket("/ws/recommendations")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        email = json.loads(data).get("email", "demouser17@gmail.com")
        jobs = get_job_recommendations(email)
        for job in jobs:
            await websocket.send_text(json.dumps(job))
            await asyncio.sleep(0.1) 
        while True:
            msg = await websocket.receive_text()
            await websocket.send_text(json.dumps({"echo": msg}))
    except Exception as e:
        await websocket.close()

email_input = "demouser17@gmail.com"
recommendation_task = create_recommendation_task(email_input)

recommender_crew = Crew(
    agents=[recommender_agent],
    tasks=[recommendation_task],
    verbose=True
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
