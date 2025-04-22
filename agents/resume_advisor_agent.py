from crewai import Agent
from llm_provider import get_llm

llm = get_llm()

resume_advisor_agent = Agent(
    role="Resume Improvement Advisor",
    goal="Give clear suggestions to improve a candidate's resume for better alignment with job matches.",
    backstory="You're a professional resume consultant who tailors resumes for better ATS and recruiter visibility.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)
