import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from rag import ask_question
import start_ollama  # This ensures the local Ollama instance is started
from fastapi.middleware.cors import CORSMiddleware

# Ensure the API uses only the repo-stored models
os.environ["OLLAMA_MODELS"] = os.path.join(os.path.dirname(__file__), "ollama", "models")

# Initialize FastAPI
app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/ask")
def ask(query: Query):
    """Handles chatbot requests from the frontend."""
    response = ask_question(query.question)
    return {"response": response}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:5000", "http://127.0.0.1:5000", "*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
