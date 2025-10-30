#!/bin/bash
# Reinstall sourcecheck package to pick up latest changes

cd "$(dirname "$0")"
source .venv/bin/activate
pip install -e ../sourcecheck-py
echo "✓ sourcecheck package reinstalled"
