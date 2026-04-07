"""
RAG Service for HealthRAG Backend API.

Lazy singleton wrapping ChromaDB + Ollama for AI coaching queries.
Reads from the shared vectorstore populated by the Streamlit container.
"""

import os
import time
import requests
from typing import Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

VECTORSTORE_PATH = os.getenv("VECTORSTORE_PATH", "/app/data/vectorstore")

PROMPT_TEMPLATE = """
You are a health and fitness advisor. IMPORTANT: Only use information from the provided context to answer questions. Do NOT make up information.

Context from documents:
{context}

Question: {question}

Rules:
1. ONLY use information explicitly stated in the context above
2. If the context doesn't contain the answer, say "I don't have information about that in the provided documents"
3. Quote or reference specific parts of the context when possible
4. Do NOT generate information not in the context
5. Be clear when recommending to consult healthcare professionals

Answer based only on the context:
"""

_rag_instance: Optional["RAGService"] = None


class RAGService:
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )
        self.vectorstore = Chroma(
            persist_directory=VECTORSTORE_PATH,
            embedding_function=self.embeddings,
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})

    def query(self, question: str) -> dict:
        """Query the RAG system. Returns response, timing, and source filenames."""
        start = time.time()

        docs = self.retriever.get_relevant_documents(question)
        context = "\n\n".join(doc.page_content for doc in docs)
        prompt = PROMPT_TEMPLATE.format(context=context, question=question)

        resp = requests.post(
            f"{self.ollama_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=300,
        )
        resp.raise_for_status()
        answer = resp.json()["response"]

        # Deduplicate and strip to just filenames for cleaner output
        sources = list({
            os.path.basename(doc.metadata.get("source", ""))
            for doc in docs
            if doc.metadata.get("source")
        })

        return {
            "response": answer,
            "response_time": round(time.time() - start, 2),
            "sources": sources,
        }

    @property
    def document_count(self) -> int:
        return self.vectorstore._collection.count()


def get_rag() -> RAGService:
    """Return the lazy singleton RAGService. Initializes on first call."""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGService()
    return _rag_instance
