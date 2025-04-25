from crewai import Task
from agents.recommender_agent import recommender_agent

def create_recommendation_task(user_email):
    return Task(
        description=(
            f"Process the user email: {user_email}. "
            "Use the `FetchRecommendationsTool` to fetch the recommendations chunks, "
            "and organize them into structured recommendations. "
            "For each job, include: Job Title, Company Name, Location, Job Type, Salary, Posted Date, Application Deadline, Key Requirements, Bonus Skills, Stack, Description, How to Apply, Direct Link, and Match Score as a percentage."
        ),
        expected_output=(
            "A clean, markdown-formatted list of 5 job recommendations. "
            "Each job must include: Job Title, Company Name, Location, Job Type, Salary, Posted Date, Application Deadline, Key Requirements, Bonus Skills, Stack, Description, How to Apply, Direct Link, and Match Score as a percentage."
        ),
        agent=recommender_agent,
        async_execution=False,
        output_file="recommendations.md",
    )