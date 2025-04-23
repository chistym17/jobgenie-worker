from crewai import Task
from agents.recommender_agent import recommender_agent
from agents.tools import FetchRecommendationsTool

recommendation_task = Task(
    description=(
        "Use the `FetchRecommendationsTool` to fetch the recommendations chunks, "
        "and organize them into structured recommendations. "
        "Each result should include the job title, short description, and why it fits the user's profile."
    ),
    expected_output=(
        "A clean, markdown-formatted list of 5 job recommendations, with titles, summaries, and personalized reasoning."
    ),
    agent=recommender_agent,
    async_execution=False,
    output_file="recommendations.md",
    input={"email": "demouser17@gmail.com"}  # You'll pass the real email when running
)
