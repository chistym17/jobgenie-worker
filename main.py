from agents.recommender_agent import recommender_agent
from agents.Tasks import create_recommendation_task
from crewai import Crew

email_input = "demouser17@gmail.com"
recommendation_task = create_recommendation_task(email_input)

recommender_crew = Crew(
    agents=[recommender_agent],
    tasks=[recommendation_task],
    verbose=True
)

if __name__ == "__main__":
    recommender_crew.kickoff(inputs={"email": email_input})
