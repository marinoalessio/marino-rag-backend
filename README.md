# Marino RAG API

A lightweight Retrieval-Augmented Generation (RAG) API built with **FastAPI**, **LlamaIndex**, **Qdrant**, and **Groq**.
This service allows querying information about **Alessio Marino’s career and background** using a vector database and LLM-powered semantic search.

The system ingests documents, stores embeddings in **Qdrant**, and answers questions through a REST API.

---

# Architecture Overview

The system is composed of three main components:

1. **Vector Database**

   * Qdrant stores document embeddings and enables semantic search.

2. **Ingestion Pipeline**

   * Reads documents from `../documents`
   * Splits them into chunks
   * Generates embeddings
   * Stores them in Qdrant.

3. **API Server**

   * FastAPI endpoint that receives questions
   * Retrieves relevant context from Qdrant
   * Sends the context to an LLM (Groq)
   * Returns a generated answer.

---

# Project Structure

```
.
├── main.py          # FastAPI server
├── rag.py           # RAG pipeline and query engine
├── ingest.py        # Document ingestion and indexing
├── requirements.txt
├── Makefile
└── ../documents     # Source documents used for the RAG
```

---

# Requirements

* Python 3.10+
* Docker
* Qdrant
* Groq API key
* HuggingFace token

---

# Environment Variables

Create a `.env` file:

```
HF_TOKEN=your_huggingface_token
GROQ_API_KEY=your_groq_api_key

QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
```

If Qdrant runs locally without authentication, `QDRANT_API_KEY` can remain empty.

---

# Installation

Install dependencies:

```
pip install -r requirements.txt
```

---

# Running Qdrant

Start the vector database using Docker:

```
docker run -p 6333:6333 qdrant/qdrant
```

Qdrant will be available at:

```
http://localhost:6333
```

---

# Document Ingestion

Whenever you add or modify files inside the folder:

```
../documents
```

you must re-run the ingestion pipeline.

Steps:

```
docker run -p 6333:6333 qdrant/qdrant
python ingest.py
```

The ingestion process will:

1. Load documents
2. Split them into semantic chunks
3. Generate embeddings
4. Store them in the `career` collection in Qdrant

Example output:

```
Loaded docs: 5
Collection created
Created chunks: 120
Indexing completed!
Saved points: 120
```

---

# Running the API

## Development

```
make dev
```

or

```
uvicorn main:app --reload --port 8000
```

---

## Production

```
make prod
```

or

```
gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

---

# API Endpoints

## Health Check

```
GET /
```

Response:

```
{
  "status": "online",
  "message": "Alessio Marino RAG API is running"
}
```

---

## Simple Health Endpoint

```
GET /health
```

Response:

```
{
  "status": "online"
}
```

---

## Ask a Question

```
GET /chat?q=your_question
```

Example:

```
/chat?q=What is Alessio Marino's current role?
```

Response:

```
{
  "answer": "Alessio Marino currently works as an Agile Data Engineer..."
}
```

---

# RAG Pipeline Details

## Embedding Model

```
BAAI/bge-small-en-v1.5
```

* Generated via HuggingFace Inference API
* Vector size: **384**

---

## LLM

```
llama-3.3-70b-versatile
```

Served via **Groq** for fast inference.

---

## Vector Database

```
Qdrant
```

Configuration:

* Distance metric: **Cosine similarity**
* Collection: `career`

---

## Retrieval Settings

```
similarity_top_k = 5
response_mode = "compact"
```

The model retrieves the **5 most relevant chunks** and generates a concise answer.

---

# Adding New Documents

1. Place files in:

```
../documents
```

2. Re-run ingestion:

```
python ingest.py
```

This will:

* delete the existing collection
* rebuild the vector index
* store updated embeddings.

---

# Technologies Used

* FastAPI
* Uvicorn
* Gunicorn
* LlamaIndex
* Qdrant
* HuggingFace Embeddings
* Groq LLM
* Python