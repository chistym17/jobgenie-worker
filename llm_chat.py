from typing import List, Dict, Any, AsyncGenerator, Optional
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class JobRecommendationLLM:
    def __init__(self):
        # Initialize Gemini model
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GOOGLE_API_KEY in environment variables.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash') 


        self.system_prompt = """

        You are a professional career advisor that specializes in providing tailored job recommendations.

🎯 Your Objective:
Help the user discover the best-matching job opportunities based on their resume and dynamically matched job descriptions.

✅ You Will Receive:
- The user's resume context
- A list of job descriptions, curated based on that resume

🧠 Your Task:
Analyze both the resume and the job descriptions. Based on that, perform the following steps:

---

🔍 First Response Structure:

1. Top 2 Job Recommendations from the provided job descriptions:
   - Job Title
   - Company Name
   - Location
   - Required Skills
   - Matching Factors (e.g., user has 2+ years with React, used AWS in past job)
   - Salary Range (if provided)
   - Next Steps (e.g., tailor resume to focus on backend skills, prepare for system design interview)

2. Smart Follow-Up Questions to narrow down the perfect match. Examples:
   - What type of company culture or size do you prefer (startup vs enterprise)?
   - Are you open to relocation or remote roles?
   - What's your expected salary range?
   - Would you prefer backend-heavy or full-stack roles?

3. Helpful & Friendly Tone: Be supportive and focused. Only ask relevant questions. Don't answer off-topic or unrelated queries. Help the user feel like you're on their side.

---

🚫 Don't:
- Don't suggest jobs not in the provided list.
- Don't answer unrelated questions.
- Don't offer generic advice without tying it to the context.

---

✅ Example Output Format (First Response):

{
  "recommendations": [
    {
      "job_title": "Full Stack Developer",
      "company": "HealthTech AI",
      "location": "Remote (US-based)",
      "required_skills": ["React", "Node.js", "MongoDB", "AWS"],
      "matching_factors": [
        "2+ years experience with React and Node.js",
        "Used MongoDB in academic project",
        "Knowledge of AWS deployment"
      ],
      "salary_range": "$90k - $110k",
      "next_steps": [
        "Highlight AWS deployment in resume",
        "Review common system design patterns for interviews"
      ]
    },
    {
      "job_title": "Backend Engineer",
      "company": "FinEdge",
      "location": "New York, NY (Hybrid)",
      "required_skills": ["Python", "Django", "PostgreSQL", "Docker"],
      "matching_factors": [
        "Strong Python & Django experience",
        "Familiar with Docker and PostgreSQL",
        "Good fit for financial tech domain"
      ],
      "salary_range": "$105k - $130k",
      "next_steps": [
        "Emphasize backend experience with Django",
        "Prepare for backend coding interview using LeetCode"
      ]
    }
  ],
  "follow_up_questions": [
    "Are you open to hybrid or only looking for remote roles?",
    "Do you have a preferred domain (e.g., health tech, fintech)?",
    "Would you prefer to focus on frontend-heavy, backend-heavy, or balanced full-stack roles?"
  ]
}
    
"""

    async def create_context(self, resume_text: str, job_descriptions: List[str]) -> str:
        """Create context string for the LLM"""
        return f"""
Resume Content:
{resume_text}

Job Descriptions:
{'\n\n'.join(job_descriptions)}
"""

    async def get_recommendation(self, resume_text: str, job_descriptions: List[str], user_query: str) -> AsyncGenerator[str, None]:
        """Get streaming job recommendations based on user query"""
        # Create context
        context = await self.create_context(resume_text, job_descriptions)

        # Combine system prompt with context
        combined_prompt = f"""
        {self.system_prompt}

Current jobs matched:
{context}

User Query:
{user_query}
"""

        messages = [
            {"role": "user", "parts": [{"text": combined_prompt}]}
        ]

        # Get streaming response
        try:
            response = self.model.generate_content(messages, stream=True)

            print(response)
            
            # Process streaming response
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                elif chunk.candidates:
                    yield chunk.candidates[0].content
                
        except Exception as e:
            print(f"Error during streaming: {e}")
            yield f"An error occurred during generation: {e}"


        except Exception as e:
            print(f"Error during streaming: {e}")
            yield f"An error occurred during generation: {e}" 

    async def get_single_recommendation(self, resume_text: str, job_descriptions: List[str], user_query: str) -> str:
        """Get a single complete recommendation"""
        full_response = []
        async for chunk in self.get_recommendation(resume_text, job_descriptions, user_query):
            full_response.append(chunk)
        return ''.join(full_response)

async def main():
    llm = JobRecommendationLLM()
    resume_text = "Experienced Python developer with expertise in machine learning and data analysis."
    job_descriptions = ["Software Engineer (Python, ML), Senior Data Scientist"]
    user_query = "What job recommendations do you have for me?"

    recommendation = await llm.get_single_recommendation(resume_text, job_descriptions, user_query)
    print(recommendation)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())