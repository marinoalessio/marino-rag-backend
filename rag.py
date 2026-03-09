import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Settings, PromptTemplate
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from qdrant_client import QdrantClient

load_dotenv()

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
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        llm = Groq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        
        vector_store = QdrantVectorStore(client=client, collection_name="career")
        index = VectorStoreIndex.from_vector_store(vector_store)
        
        _query_engine = index.as_query_engine(
            llm=llm,
            text_qa_template=qa_prompt,
            similarity_top_k=5,
            response_mode="compact"
        )
    return _query_engine

def ask_question(question: str) -> str:
    return str(get_query_engine().query(question))