from crewai import Task
from agents.recommender_agent import recommender_agent
from agents.tools import FetchRecommendationsTool

def create_recommendation_task(user_email):
    return Task(
        description=(
            f"Process the user email: {user_email}. "
            "Use the `FetchRecommendationsTool` to fetch the recommendations chunks, "
            "and organize them into structured recommendations. "
            "Each result should include the job title, short description, and why it fits the user's profile."
        ),
        expected_output=(
            "A clean, markdown-formatted list of 5 job recommendations, with id,company_name,title, summaries, and personalized reasoning."
        ),
        agent=recommender_agent,
        async_execution=False,
        output_file="recommendations.md",
    )
