from crewai import Agent
# from agents.llm_provider import get_llm  # Removed because we're creating the LLM directly
from agents.tools import FetchRecommendationsTool

import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

# Define the LLM with CrewAI's LLM class and explicitly set the provider
gemini_llm = LLM(
    model="gemini/gemini-2.0-flash",
    provider="google_ai",  # Or "gemini" - try "google" first, then "gemini" if that doesn't work
    api_key=os.getenv("GOOGLE_API_KEY"),
    verbose=True, # Add verbose here to debug litellm messages too.  Handy!
    model_kwargs={"temperature": 0.5} # Move temperature here
)


fetch_recommendations_tool = FetchRecommendationsTool()

recommender_agent = Agent(
    role="Job Recommendation Engine",
    goal="Find the most relevant jobs for the user based on their resume",
    backstory=(
        "You're an expert job matcher using advanced embeddings and LLM analysis. "
        "You find highly personalized job opportunities based on candidate profiles."
    ),
    tools=[fetch_recommendations_tool],
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)