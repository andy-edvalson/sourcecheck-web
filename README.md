# SourceCheck API

A FastAPI REST service for validating text claims against source documents using the [sourcecheck-py](https://github.com/andy-edvalson/sourcecheck-py) library.

## Features

- 🚀 **Fast validation** - Models loaded once on startup, kept in memory
- 📊 **Detailed results** - Per-claim verdicts with evidence and explanations
- 📚 **Auto-generated docs** - Interactive API documentation at `/docs`
- 🔄 **Async support** - Handle concurrent validation requests
- 🎯 **Simple API** - Single endpoint for validation

## Requirements

- **Python 3.11** (Required - negspacy does not support Python 3.12+)
- pip

## Quick Start

### 1. Setup

```bash
# Verify Python version
python3.11 --version  # Should show 3.11.x

# Create virtual environment with Python 3.11
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install dependencies (includes sourcecheck-py from GitHub)
pip install -r requirements.txt
```

### 2. Run the API

```bash
# Start the server
uvicorn api.main:app --reload --port 8000

# Or use the run script
chmod +x run.sh
./run.sh
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

## API Endpoints

### POST /api/v1/validate

Validate claims against source text.

**Request:**
```json
{
  "source_text": "Patient reports chest pain for 2 days...",
  "claims": {
    "chief_complaint": "Chest pain for 2 days",
    "medications": "Aspirin 81mg daily"
  }
}
```

**Response:**
```json
{
  "overall_score": 0.92,
  "total_claims": 2,
  "supported_count": 2,
  "refuted_count": 0,
  "insufficient_count": 0,
  "support_rate": 1.0,
  "dispositions": [
    {
      "field": "chief_complaint",
      "claim_text": "Chest pain for 2 days",
      "verdict": "supported",
      "evidence_count": 5,
      "validator": "bm25_validator",
      "explanation": "Found 5 evidence spans..."
    }
  ]
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "models_loaded": true
}
```

## Example Usage

### Using curl

```bash
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "source_text": "Patient reports chest pain for 2 days. No fever or chills.",
    "claims": {
      "chief_complaint": "Chest pain for 2 days",
      "symptoms": "No fever"
    }
  }'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/validate",
    json={
        "source_text": "Patient reports chest pain for 2 days...",
        "claims": {
            "chief_complaint": "Chest pain for 2 days"
        }
    }
)

result = response.json()
print(f"Overall score: {result['overall_score']}")
print(f"Supported: {result['supported_count']}/{result['total_claims']}")
```

## Development

### Project Structure

```
sourcecheck-web/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic models
│   └── routes/
│       ├── health.py        # Health check
│       └── validate.py      # Validation endpoint
├── requirements.txt
├── .gitignore
├── README.md
└── run.sh
```

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when added)
pytest
```

## Deployment

### Docker (Coming Soon)

```bash
docker build -t sourcecheck-api .
docker run -p 8000:8000 sourcecheck-api
```

### EC2 Deployment

See deployment guide for EC2 setup instructions.

## License

Proprietary - All Rights Reserved

## Links

- [sourcecheck-py library](https://github.com/andy-edvalson/sourcecheck-py)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
