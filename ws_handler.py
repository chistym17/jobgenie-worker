from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Dict, List, Any
import json
import os
from dotenv import load_dotenv
from qdrant_service import search_similar
from llm_chat import JobRecommendationLLM
from embedder import get_embedding

load_dotenv()

class JobRecommendationWebSocket:
    def __init__(self):
        self.llm = JobRecommendationLLM()
        self.mock_resume = """
        Full Stack Developer with 5+ years of experience
        
        Skills:
        - Python (Flask, FastAPI)
        - JavaScript (React, Node.js)
        - Database (MongoDB, PostgreSQL)
        - Cloud (AWS, Azure)
        - DevOps (Docker, Kubernetes)
        
        Experience:
        - Senior Software Engineer at TechCorp (2020-present)
        - Software Developer at WebDev Solutions (2018-2020)
        
        Education:
        - BSc in Computer Science, University of Tech
        """

    async def handle_connection(self, websocket: WebSocket):
        """Handle WebSocket connection and process job recommendations"""
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                query = json.loads(data).get("query", "")
                
                if not query:
                    await websocket.send_json({
                        "error": "No query provided"
                    })
                    continue

                # Get the embedding for the user query
                query_embedding = get_embedding(self.mock_resume)
                
                # Search for relevant jobs in Qdrant
                job_results = search_similar(query_embedding, top_k=5)
                
                # Extract job descriptions from results
                job_descriptions = []
                for result in job_results:
                    job_descriptions.append(result.payload.get("description", ""))
                
                # Get streaming recommendations
                async for chunk in self.llm.get_recommendation(
                    resume_text=self.mock_resume,
                    job_descriptions=job_descriptions,
                    user_query=query
                ):
                    await websocket.send_json({
                        "recommendation": chunk,
                    })

        except WebSocketDisconnect:
            print("Client disconnected")
        except Exception as e:
            await websocket.send_json({
                "error": f"An error occurred: {str(e)}"
            })

# Initialize WebSocket handler
job_websocket = JobRecommendationWebSocket()

async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for job recommendations"""
    await job_websocket.handle_connection(websocket)