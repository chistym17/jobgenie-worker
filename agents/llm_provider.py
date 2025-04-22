from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

def get_llm(model="gemini-pro"):
    return ChatGoogleGenerativeAI(
        model_name=model,
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7,
    )
    


