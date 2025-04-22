from crewai import Agent
from llm_provider import get_llm

llm = get_llm()

general_agent = Agent(
    role="Conversational Assistant",
    goal="Engage users in friendly conversation, answer general queries, and help route them to the right assistance.",
    backstory="You're a friendly chatbot with a casual tone, responsible for general greetings, follow-ups, and support for non-technical queries.",
    verbose=True,
    allow_delegation=True,
    llm=llm
)
