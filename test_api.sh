#!/bin/bash

# SourceCheck API - Test Script
# Tests the API with sample data from sourcecheck-py

set -e

API_URL="http://localhost:8000"

echo "========================================="
echo "SourceCheck API - Test Script"
echo "========================================="
echo ""

# Check if API is running
echo "1. Checking API health..."
HEALTH=$(curl -s "${API_URL}/health")
echo "Response: $HEALTH"
echo ""

if echo "$HEALTH" | grep -q "healthy"; then
    echo "✓ API is healthy!"
else
    echo "❌ API is not responding. Make sure it's running with ./run.sh"
    exit 1
fi

echo ""
echo "========================================="
echo "2. Testing validation with sample data"
echo "========================================="
echo ""

# Read sample transcript from sourcecheck-py
TRANSCRIPT_PATH="../sourcecheck-py/examples/sample_transcript.txt"

if [ ! -f "$TRANSCRIPT_PATH" ]; then
    echo "❌ Sample transcript not found at: $TRANSCRIPT_PATH"
    echo "Make sure sourcecheck-py is in the parent directory"
    exit 1
fi

echo "Reading sample transcript from: $TRANSCRIPT_PATH"
TRANSCRIPT=$(cat "$TRANSCRIPT_PATH")

# Create JSON payload
cat > /tmp/test_payload.json <<EOF
{
  "source_text": $(echo "$TRANSCRIPT" | jq -Rs .),
  "claims": {
    "chief_complaint": "Fall",
    "age": "56 years old",
    "gender": "female",
    "medications": "Blood pressure medication"
  }
}
EOF

echo ""
echo "Sending validation request..."
echo ""

# Send request and save response
RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/validate" \
  -H "Content-Type: application/json" \
  -d @/tmp/test_payload.json)

# Pretty print response
echo "$RESPONSE" | jq .

echo ""
echo "========================================="
echo "Summary"
echo "========================================="

# Extract key metrics
OVERALL_SCORE=$(echo "$RESPONSE" | jq -r '.overall_score')
TOTAL_CLAIMS=$(echo "$RESPONSE" | jq -r '.total_claims')
SUPPORTED=$(echo "$RESPONSE" | jq -r '.supported_count')
REFUTED=$(echo "$RESPONSE" | jq -r '.refuted_count')
INSUFFICIENT=$(echo "$RESPONSE" | jq -r '.insufficient_count')

echo "Overall Score: $OVERALL_SCORE"
echo "Total Claims: $TOTAL_CLAIMS"
echo "Supported: $SUPPORTED"
echo "Refuted: $REFUTED"
echo "Insufficient Evidence: $INSUFFICIENT"

echo ""
echo "✓ Test complete!"
echo ""
echo "View detailed results in the JSON output above"
echo "Or visit http://localhost:8000/docs for interactive testing"

# Cleanup
rm /tmp/test_payload.json
