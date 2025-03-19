import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag import ask_question
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

# Initialize FastAPI
app = FastAPI()

class Query(BaseModel):
    question: str

# ✅ Streaming Response in FastAPI
@app.post("/ask")
async def ask(query: Query):
    """Handles chatbot requests with a streaming response."""
    print(f"\nReceived Query: {query.question}")  # ✅ Log input
    return StreamingResponse(ask_question(query.question), media_type="text/plain")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:5000", "http://127.0.0.1:5000", "*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="debug")
