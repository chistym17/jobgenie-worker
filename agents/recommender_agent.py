from crewai import Agent
from llm_provider import get_llm

llm = get_llm()

recommender_agent = Agent(
    role="Job Recommender",
    goal="Recommend the best fitting jobs using resume and vector matches.",
    backstory="You're an experienced recommender that finds the most relevant job listings.",
    verbose=True,
    allow_delegation=True,
    llm=llm
)