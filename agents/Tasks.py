from crewai import Task
from agents.recommender_agent import recommender_agent
from agents.explainer_agent import explainer_agent

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
        output_file="recommendations.md", 
    )

def create_explanation_task(job_object, user_resume):
    return Task(
        description=(
            f"""
            You are an expert job match explainer.
            You will receive a job object and a user's resume as input.
            Analyze the job requirements, responsibilities, and desired skills from the job object: {job_object}, and compare them carefully with the user's experience, skills, and background from the resume: {user_resume}.
            Write a clear, concise explanation that *directly compares* the job posting with the user's profile: for each major requirement, explain how the user meets it, referencing specific experiences, skills, or achievements.
            Your explanation should follow this pattern: "The job requires [requirement], and you have [matching skill/experience]."
            Always address the user directly as "you" — do not use their name, and do not refer to them as "the candidate" or "he/she."
            If the user lacks any skills, explain how their transferable skills can help cover the gap.
            Your final output MUST be a single, well-structured paragraph (no bullet points, no markdown, no extraneous text).
            Only return the explanation text, and nothing else.
            """
        ),
        expected_output=(
            "A single, well-structured paragraph that directly compares the job requirements and the user's skills and experience, highlighting matches and addressing any gaps."
        ),
        agent=explainer_agent,
        async_execution=False
    )

