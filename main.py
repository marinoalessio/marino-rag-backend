from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag import ask_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/chat")
def chat(q: str):
    return {"answer": ask_question(q)}