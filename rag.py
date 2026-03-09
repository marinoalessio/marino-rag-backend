import os
from typing import Any, List
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

qa_prompt = PromptTemplate(
    "You are an assistant that answers questions about Alessio Marino's career and background.\n"
    "Use ONLY the context below to answer accurately and in detail.\n"
    "If the context contains the answer, provide it fully. Do not say 'Empty Response'.\n\n"
    "Context:\n{context_str}\n\n"
    "Question: {query_str}\n"
    "Answer:"
)

_query_engine = None

def get_query_engine():
    global _query_engine
    if _query_engine is None:
        Settings.embed_model = LightHFEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            token=os.getenv("HF_TOKEN")
        )
        
        Settings.llm = Groq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        
        vector_store = QdrantVectorStore(client=client, collection_name="career")
        index = VectorStoreIndex.from_vector_store(vector_store)
        
        _query_engine = index.as_query_engine(
            text_qa_template=qa_prompt,
            similarity_top_k=5,
            response_mode="compact"
        )
    return _query_engine

def ask_question(question: str) -> str:
    try:
        return str(get_query_engine().query(question))
    except Exception as e:
        return f"Error: {str(e)}"