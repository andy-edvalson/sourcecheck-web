# Docker Deployment Guide

## Quick Start

```bash
# Build the image
./docker-build.sh

# Run the API
docker-compose up

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

## What's Included

### Multi-Stage Build
- **Stage 1 (builder)**: Installs all dependencies, downloads models
- **Stage 2 (runtime)**: Copies only what's needed, runs as non-root user
- **Result**: Smaller, more secure image

### Features
- ✅ Non-root user (security)
- ✅ Health checks (monitoring)
- ✅ Resource limits (stability)
- ✅ Volume mounts (development)
- ✅ Auto-restart (reliability)

## Development Workflow

### Hot Reload (with volumes)
The docker-compose.yml mounts your code as volumes:
```yaml
volumes:
  - ../sourcecheck-py:/app/sourcecheck-py:ro
  - ./api:/app/api:ro
```

**When you update sourcecheck-py:**
1. Changes are immediately available in container
2. Restart container: `docker-compose restart api`

**When you update API code:**
1. Changes are immediately available
2. Restart container: `docker-compose restart api`

### Rebuild (after dependency changes)
```bash
# Rebuild image
docker-compose build

# Restart with new image
docker-compose up -d
```

## Production Deployment

### Build for Production
```bash
# Build without cache (fresh build)
docker-compose build --no-cache

# Tag for registry
docker tag sourcecheck-web-api:latest your-registry/sourcecheck-api:v1.0.0

# Push to registry
docker push your-registry/sourcecheck-api:v1.0.0
```

### Run on EC2/Server
```bash
# Pull image
docker pull your-registry/sourcecheck-api:v1.0.0

# Run container
docker run -d \
  --name sourcecheck-api \
  -p 8000:8000 \
  --restart unless-stopped \
  --memory 4g \
  --cpus 2 \
  your-registry/sourcecheck-api:v1.0.0
```

### Environment Variables
```bash
# Set log level
docker run -e LOG_LEVEL=debug ...

# Set custom port
docker run -p 9000:8000 ...
```

## Monitoring

### Health Check
```bash
# Check container health
docker ps

# Manual health check
curl http://localhost:8000/health
```

### Logs
```bash
# Follow logs
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api

# Logs since 1 hour ago
docker-compose logs --since 1h api
```

### Resource Usage
```bash
# Container stats
docker stats sourcecheck-web-api-1

# Detailed info
docker inspect sourcecheck-web-api-1
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs api

# Check if port is in use
lsof -i :8000

# Remove old containers
docker-compose down
docker-compose up
```

### Out of memory
```bash
# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G  # Increase this
```

### Slow build
```bash
# Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker-compose build

# Or set in environment
export DOCKER_BUILDKIT=1
```

### Library updates not reflecting
```bash
# Rebuild without cache
docker-compose build --no-cache

# Or just rebuild the builder stage
docker-compose build --no-cache --build-arg BUILDKIT_INLINE_CACHE=1
```

## Image Size Optimization

Current setup uses multi-stage build:
- Builder stage: ~3GB (with all build tools)
- Runtime stage: ~1.5GB (only runtime dependencies)

To further optimize:
1. Use `python:3.11-slim` (already done)
2. Clean apt cache (already done)
3. Use `--no-cache-dir` for pip (already done)
4. Consider distroless base image for production

## Security

### Non-Root User
Container runs as `apiuser` (UID 1000), not root.

### Read-Only Volumes
Development volumes are mounted read-only (`:ro`).

### Resource Limits
CPU and memory limits prevent resource exhaustion.

### Health Checks
Automatic health monitoring and restart on failure.

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Build Docker image
  run: |
    cd sourcecheck-web
    docker-compose build

- name: Run tests
  run: |
    docker-compose up -d
    sleep 10
    python test_api.py
    docker-compose down
```

### Automated Deployment
```yaml
- name: Deploy to production
  run: |
    docker tag sourcecheck-web-api:latest $REGISTRY/sourcecheck-api:$VERSION
    docker push $REGISTRY/sourcecheck-api:$VERSION
    ssh $SERVER "docker pull $REGISTRY/sourcecheck-api:$VERSION && docker-compose up -d"
