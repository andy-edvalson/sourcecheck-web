#!/bin/bash
# Build and run sourcecheck API with Docker

set -e

echo "🐳 Building sourcecheck API Docker image..."
docker-compose build

echo "✓ Build complete!"
echo ""
echo "To run the API:"
echo "  docker-compose up"
echo ""
echo "To run in background:"
echo "  docker-compose up -d"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop:"
echo "  docker-compose down"
