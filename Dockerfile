# Multi-stage build for sourcecheck API
# Stage 1: Build stage with all dependencies
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy sourcecheck library first (changes less frequently)
COPY ../sourcecheck-py /app/sourcecheck-py

# Install sourcecheck library
RUN pip install --no-cache-dir -e /app/sourcecheck-py

# Copy API requirements
COPY requirements.txt .

# Install API dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spacy models (do this in builder to cache)
RUN python -m spacy download en_core_web_sm

# Stage 2: Runtime stage (smaller image)
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 apiuser

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy sourcecheck library (for editable install)
COPY --from=builder /app/sourcecheck-py /app/sourcecheck-py

# Copy API code
COPY api /app/api
COPY run.sh /app/

# Change ownership to non-root user
RUN chown -R apiuser:apiuser /app

# Switch to non-root user
USER apiuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

# Run the API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
