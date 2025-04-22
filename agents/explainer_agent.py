from crewai import Agent
from llm_provider import get_llm

llm = get_llm()

explainer_agent = Agent(
    role="Job Explanation Expert",
    goal="Explain the rationale behind each job recommendation clearly and thoroughly.",
    backstory="You're an expert AI with deep knowledge in career strategy. You break down recommendations for users so they can understand the fit.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)
