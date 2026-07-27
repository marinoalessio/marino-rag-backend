import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from llama_index.core import SimpleDirectoryReader

load_dotenv()

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
docs_path = os.path.join(BASE_DIR, "../documents")

documents = SimpleDirectoryReader(docs_path).load_data()
print(f"Loaded docs: {len(documents)}")

client = QdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    api_key=os.getenv("QDRANT_API_KEY")
)

if client.collection_exists("career"):
    client.delete_collection("career")

client.create_collection(
    collection_name="career",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
print("Collection created")

vector_store = QdrantVectorStore(client=client, collection_name="career")
storage_context = StorageContext.from_defaults(vector_store=vector_store)
splitter = SentenceSplitter(chunk_size=128, chunk_overlap=30)
nodes = splitter.get_nodes_from_documents(documents)
print(f"Created chunks: {len(nodes)}")

index = VectorStoreIndex(nodes, storage_context=storage_context, show_progress=True)
print("Indexing completed!")

collection_info = client.get_collection("career")
print(f"Saved points: {collection_info.points_count}")