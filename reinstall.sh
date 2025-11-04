#!/bin/bash
# Reinstall sourcecheck package to pick up latest changes

cd "$(dirname "$0")"
source .venv/bin/activate
pip install -e ../sourcecheck-py

# Download SpaCy model if not already installed
echo "Checking for SpaCy model..."
python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null || {
    echo "Downloading SpaCy model 'en_core_web_sm'..."
    python -m spacy download en_core_web_sm
}

echo "✓ sourcecheck package reinstalled"
