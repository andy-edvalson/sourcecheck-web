"""
SourceCheck API - FastAPI Application

A REST API for validating text claims against source documents.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import health, validate

# Create FastAPI app
app = FastAPI(
    title="SourceCheck API",
    description="Verify text claims against source documents using NLI and retrieval methods",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(validate.router, prefix="/api/v1", tags=["Validation"])


@app.get("/")
async def root():
    """Root endpoint - redirects to docs"""
    return {
        "message": "SourceCheck API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
