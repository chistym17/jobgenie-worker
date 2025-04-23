from langchain.tools import Tool
from db import fetch_resume_data
from fetch_recommendations import fetch_recommendations

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# Step 1: Define input schema
class RecommendationInput(BaseModel):
    """Input schema for the recommendation tool."""
    email: str = Field(..., description="User's email to fetch job recommendations for")

# Step 2: Create the tool subclassing BaseTool
class FetchRecommendationsTool(BaseTool):
    name: str = "fetch_recommendations"
    description: str = "Fetches job recommendations for a given email"
    args_schema: Type[BaseModel] = RecommendationInput

    def _run(self, email: str) -> str:
        # Your recommendation logic here
        return fetch_recommendations(email)
