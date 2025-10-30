"""
Health check endpoint
"""
from fastapi import APIRouter
from api.models import HealthResponse

router = APIRouter()

# Global flag to track if models are loaded
_models_loaded = False


def set_models_loaded(loaded: bool):
    """Set the models loaded status"""
    global _models_loaded
    _models_loaded = loaded


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns the API status and whether models are loaded.
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        models_loaded=_models_loaded
    )
