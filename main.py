import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag import ask_question

app = FastAPI()

origins = [
    "https://marino-ai.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# @app.get("/")
# def health_check():
#     return {"status": "online", "message": "Alessio Marino RAG API is running"}

@app.get("/")
def health_check():
    try:
        freeze_output = subprocess.check_output(["pip", "freeze"]).decode("utf-8")
        packages = freeze_output.split('\n')
    except Exception as e:
        packages = [f"Errore nel recupero pacchetti: {str(e)}"]

    return {
        "status": "online", 
        "message": "Alessio Marino RAG API is running",
        "render_environment_freeze": packages
    }

@app.get("/chat")
def chat(q: str):
    return {"answer": ask_question(q)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)