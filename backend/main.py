import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag import ask_question
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI
app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/ask")
def ask(query: Query):
    """Handles chatbot requests from the frontend."""
    try:
        response = ask_question(query.question)
        if not response:
            raise HTTPException(status_code=500, detail="No response from LLM.")
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:5000", "http://127.0.0.1:5000", "*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
