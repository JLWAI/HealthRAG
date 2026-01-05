import os

# RAG Configuration
DATA_PATH = "data/pdfs"
VECTORSTORE_PATH = "data/vectorstore"

# Text Splitting Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval Configuration
RETRIEVAL_K = 5

# Local Model Configuration
# Can be overridden with OLLAMA_BASE_URL environment variable (for homelab deployment)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = "llama3.1:8b"

# Embedding Model Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DEVICE = "cpu"