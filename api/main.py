"""
SourceCheck API - FastAPI Application

A REST API for validating text claims against source documents.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes import health, validate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable debug logging for sourcecheck modules
logging.getLogger('sourcecheck').setLevel(logging.INFO)

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

# Mount static files
app.mount("/static", StaticFiles(directory="api/static"), name="static")

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(validate.router, prefix="/api/v1", tags=["Validation"])


@app.get("/")
async def root():
    """Root endpoint - serves the web UI"""
    return FileResponse("api/static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
