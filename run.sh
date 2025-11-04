#!/bin/bash

# SourceCheck API - Quick Start Script

set -e  # Exit on error

echo "========================================="
echo "SourceCheck API - Starting Server"
echo "========================================="
echo ""

# Check if Python 3.11 is available
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Error: Python 3.11 is required but not found"
    echo "Please install Python 3.11 first"
    exit 1
fi

echo "✓ Python 3.11 found: $(python3.11 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with Python 3.11..."
    python3.11 -m venv .venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies..."
echo "(This may take a few minutes on first run - installing ML models)"
pip install -r requirements.txt

# Check for SpaCy model and download if needed
echo ""
echo "Checking for SpaCy model..."
python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null || {
    echo "Downloading SpaCy model 'en_core_web_sm'..."
    python -m spacy download en_core_web_sm
    echo "✓ SpaCy model installed"
}

echo ""
echo "========================================="
echo "✓ Setup complete!"
echo "========================================="
echo ""
echo "Starting FastAPI server..."
echo ""
echo "API will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn api.main:app --reload --port 8000
