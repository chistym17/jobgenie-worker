from agents.recommender_agent import recommender_agent
from agents.Tasks import recommendation_task
from crewai import Crew

recommender_crew = Crew(
    agents=[recommender_agent],
    tasks=[recommendation_task],
    verbose=True
)
    



user_email = "demouser17@gmail.com"

result = recommender_crew.kickoff(inputs={"email": user_email})

if __name__ == "__main__":
    recommender_crew.kickoff(inputs={"email": user_email})
    print(result)