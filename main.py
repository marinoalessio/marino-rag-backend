from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from rag import get_query_engine, ask_question

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Init query engine...")
    get_query_engine()
    print("Ready!")
    yield

app = FastAPI(lifespan=lifespan)

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