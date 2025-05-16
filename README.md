# ⚙️ Worker Service - JobGenie

The **Worker Service** handles heavy processing and AI-related logic in JobGenie. It works alongside the Primary Backend to embed data, generate job recommendations, and manage AI interactions—ensuring scalability and responsiveness.

---

### 🧠 Core Responsibilities

- **Asynchronous Processing**: Uses **Celery** with **Redis** as a message broker to offload intensive tasks like:
  - Embedding resumes and job descriptions via **Google Gemini API**
  - Generating personalized job recommendations
- **AI Interactions**: Manages real-time communication with the frontend using WebSocket for AI-driven chat, resume suggestions, and job-fit explanations.
- **Semantic Search**: Stores and retrieves embedded vectors using **Qdrant** to match resumes with jobs effectively.
- **AI Agent Orchestration**: Uses **CrewAI** to coordinate multi-agent logic for handling complex user queries.

---

### 🛠️ Tech Stack (Worker)

- **Task Queue**: Celery + Redis
- **Embedding & NLP**: Google Generative AI (Gemini API)
- **Semantic DB**: Qdrant
- **WebSocket Server**: FastAPI WebSocket
- **AI Agents**: CrewAI
- **Language**: Python

---

> Note: The Worker Service operates independently but listens for tasks dispatched by the Primary Backend. Real-time features rely on its uptime and proper WebSocket connectivity.
