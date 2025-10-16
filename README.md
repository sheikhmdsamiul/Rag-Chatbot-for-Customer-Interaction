# RAG Chatbot for Customer Interaction

A simple Retrieval-Augmented Generation (RAG) chatbot that fetches product data from an external API, converts products into retrievable documents, and answers user queries by combining retrieved product context with a chat history-aware LLM.

## Project overview

This repository implements a lightweight product information assistant built with FastAPI and LangChain. The service fetches product data (from a sample API), converts each product into a LangChain Document, indexes them into a FAISS vector store, and answers user questions using a RAG pipeline with a history-aware retriever.

Core goals:
- Demonstrate a minimal RAG pipeline using LangChain primitives.
- Keep initialization lazy to avoid heavy imports at module import time.
- Provide a simple HTTP API for fetching product data and running chat queries.

## Technical implementation details

- Framework: FastAPI provides HTTP endpoints.
- Retrieval: FAISS (via `langchain_community.vectorstores.FAISS`) is used to index and search product documents.
- Embeddings: `langchain_huggingface.HuggingFaceEmbeddings` is used for embeddings (model controlled by `EMBEDDING_MODEL`).
- LLM: Groq Chat (via `langchain_groq.ChatGroq`) is used as the generative model when `GROQ_API_KEY` is present.
- RAG flow:
  1. Fetch products from the configured `DUMMYJSON_API_URL`.
  2. Convert each product to a LangChain `Document` containing a human-readable summary and raw JSON snapshot.
  3. Create a FAISS vectorstore from documents and expose a retriever.
  4. Use a history-aware retriever to contextualize the latest question, then run a QA chain over retrieved documents.

Key code locations:
- `server/app/main.py` — FastAPI app, endpoints `/api/products` and `/api/chat`.
- `server/app/services/product_service.py` — Product -> Document conversion.
- `server/app/services/chatbot_service.py` — RAG pipeline, model and embeddings initialization, vectorstore creation.
- `server/app/utils/groq_client.py` — Wrapper to initialize Groq Chat LLM.
- `server/app/core/config.py` — Environment-based settings (`GROQ_API_KEY`, `EMBEDDING_MODEL`, etc.).
- `server/app/models/schemas.py` — Pydantic models for API request/response and Product schema.
- `server/app/core/chat_state.py` — In-memory chat state storing chat history and current documents.

## Setup & Installation

1. Clone the repository and open a PowerShell terminal.

2. (Recommended) Create and activate a virtual environment. From the repo root in PowerShell:

```powershell
# Create (if you don't have one already)
python -m venv chatbotenv

# Activate
. .\chatbotenv\Scripts\Activate.ps1
```

3. Install dependencies:


```powershell
pip install -r requirements.txt
```



4. Configure environment variables. Create a `.env` file in the repository root:

```text
# Get Your Free Groq API Key

# Visit https://console.groq.com
# Sign up for free
# Create an API key
# Add it to your .env file
```

## Project structure

Top-level relevant files/folders:

- `server/app/main.py` — API endpoints and entrypoint.
- `server/app/services/` — Business logic for product->document and RAG pipeline.
- `server/app/models/` — Pydantic models.
- `server/app/core/` — Configuration and in-memory chat state.
- `server/app/utils/` — LLM client helpers.
- `requirements_fixed.txt` — Cleaned dependency list (use this to install).

## Usage

Start the FastAPI app with uvicorn from the repository root (after activating venv):

```powershell or cmd
uvicorn server.app.main:app --reload 
```

Endpoints:
- GET `/api/products` — Fetches product data from the configured `DUMMYJSON_API_URL`, converts them to documents, and stores them in memory for retrieval.
- POST `/api/chat` — Send a JSON body matching `ChatRequest` (see `server/app/models/schemas.py`). Example:

```json
{ "query": "Tell me about the Kiwi product" }
```

Response shape matches `ChatResponse` with `chat_history` and `response` fields.

Notes:
- The service uses an in-memory store (`server/app/core/chat_state.py`). For production, replace this with a persistent store (Redis, DB) and a persisted vectorstore.
- Model/embeddings initialization is lazy to avoid import-time heavy initialization. Ensure your environment has the required packages before calling `/api/chat`.





