"""
Chat / RAG API endpoints.

Exposes the HealthRAG vector-search + Ollama AI coaching system via REST.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from api.auth import get_current_user
from models.schemas import ChatQuery, ChatResponse, TokenData
from services.rag_service import get_rag

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def query_rag(
    request: ChatQuery,
    current_user: TokenData = Depends(get_current_user),
) -> ChatResponse:
    """
    Query the HealthRAG AI coaching system.

    Retrieves relevant chunks from the fitness/nutrition PDF knowledge base
    (28 expert PDFs: Renaissance Periodization, Jeff Nippard, etc.) and
    generates a grounded response via Ollama.

    Args:
        request.question: Natural language health or fitness question

    Returns:
        response: AI-generated answer grounded in PDF sources
        response_time: Seconds taken to generate
        sources: PDF filenames that informed the answer
    """
    try:
        rag = get_rag()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"RAG system unavailable: {str(e)}",
        )

    try:
        result = rag.query(request.question)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}",
        )


@router.get("/status")
async def rag_status(current_user: TokenData = Depends(get_current_user)) -> dict:
    """
    Check RAG system status and document count.

    Returns initialization state and number of indexed document chunks.
    """
    try:
        rag = get_rag()
        return {
            "status": "ready",
            "document_chunks": rag.document_count,
            "ollama_url": rag.ollama_url,
            "model": rag.model,
        }
    except Exception as e:
        return {"status": "unavailable", "error": str(e)}
