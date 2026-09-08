import os
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from rag import ask_question

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: List[Message] = []

@app.get("/")
def health_check():
    return {"status": "online", "message": "Alessio Marino RAG API is running"}

@app.head("/health")
async def health_head():
    return Response(status_code=200)

@app.post("/chat")
@limiter.limit("30/day")
def chat(request: Request, body: ChatRequest):
    history = [{"role": m.role, "content": m.content} for m in body.history]
    return {"answer": ask_question(body.question, history)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)