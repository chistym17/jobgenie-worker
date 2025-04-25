from crewai import Task
from agents.recommender_agent import recommender_agent

def create_recommendation_task(user_email):
    return Task(
        description=(
            f"Process the user email: {user_email}. "
            "Use the `FetchRecommendationsTool` to fetch job recommendation information. "
            "Transform the fetched data into a structured JSON format. "
            "Each job in the JSON should include the following fields: "
            "Job Title, Company Name, Location, Job Type, Salary, Posted Date, Application Deadline, "
            "Key Requirements, Bonus Skills, Stack, Description, How to Apply, Direct Link, and Match Score (as a percentage). "
            "Ensure that the Match Score is represented as a number (e.g., 55 for 55%). "
            "The final output *MUST* be a valid JSON array where each element is a JSON object representing a job. "
            "**IMPORTANT: Your FINAL ANSWER must *ONLY* contain valid JSON and *NO* other text or markdown. Do not add any surrounding text, explanations, or conversational elements. JUST the JSON.**"
        ),
        expected_output=(
            "A clean, json formatted list of 5 job recommendations. "
            "Each job includes: Job Title, Company Name, Location, Job Type, Salary, Posted Date, "
            "Application Deadline, Key Requirements, Bonus Skills, Stack, Description, How to Apply, "
            "Direct Link, and Match Score (as a percentage). It MUST be a json array."
        ),
        agent=recommender_agent,
        async_execution=False,
        output_file="recommendations.md", # Removed - not needed for the API
    )