import os
from datetime import date
from typing import Any, Dict, List
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Settings, PromptTemplate
from llama_index.core.embeddings import BaseEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.llms.groq import Groq
from qdrant_client import QdrantClient
from huggingface_hub import InferenceClient

load_dotenv()

class LightHFEmbedding(BaseEmbedding):
    def __init__(self, model_name: str, token: str, **kwargs: Any):
        super().__init__(**kwargs)
        self._client = InferenceClient(model=model_name, token=token)

    def _get_query_embedding(self, query: str) -> List[float]:
        return self._client.feature_extraction(query).flatten().tolist()

    def _get_text_embedding(self, text: str) -> List[float]:
        return self._client.feature_extraction(text).flatten().tolist()

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self._get_text_embedding(t) for t in texts]

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

def build_prompt() -> PromptTemplate:
    today = date.today().strftime("%B %d, %Y")
    return PromptTemplate(
        f"You are an assistant that ONLY answers questions about Alessio Marino's career and background.\n"
        f"Today's date is {today}. Use it to calculate ages or durations when needed.\n"
        "Use ONLY the context below.\n"
        "Provide a concise but complete answer (4–6 sentences maximum).\n"
        "Focus on the key facts: role, company, main responsibilities, and technologies.\n"
        "Write in clear, professionally and avoid unnecessary explanations.\n"
        "If the answer is present in the context, summarize it clearly.\n\n"
        "Context:\n{context_str}\n\n"
        "Question: {query_str}\n"
        "Answer:"
    )

_query_engine = None

def get_query_engine():
    global _query_engine
    if _query_engine is None:
        Settings.embed_model = LightHFEmbedding(
            model_name="BAAI/bge-base-en-v1.5",
            token=os.getenv("HF_TOKEN")
        )
        
        Settings.llm = Groq(
            model="qwen/qwen3.8-27b",
            api_key=os.getenv("GROQ_API_KEY"),
            max_tokens=512
        )
        
        client = QdrantClient(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "qdrant_storage"))
        
        vector_store = QdrantVectorStore(client=client, collection_name="career")
        index = VectorStoreIndex.from_vector_store(vector_store)
        
        _query_engine = index.as_query_engine(
            text_qa_template=build_prompt(),
            similarity_top_k=5,
            response_mode="compact"
        )
    return _query_engine

def _format_history(history: List[Dict]) -> str:
    lines = []
    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)

def ask_question(question: str, history: List[Dict] = []) -> str:
    try:
        if history:
            history_str = _format_history(history)
            augmented = f"Conversation so far:\n{history_str}\n\nCurrent question: {question}"
        else:
            augmented = question
        return str(get_query_engine().query(augmented))
    except Exception as e:
        return f"Error: {str(e)}"