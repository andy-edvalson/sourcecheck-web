#!/usr/bin/env python3
"""
Test temporal drift case specifically
"""
import json
from pathlib import Path
import requests
import yaml

API_URL = "http://localhost:8000"

# Read files
base_dir = Path("../sourcecheck-py/local")
transcript_path = base_dir / "real_transcript.txt"
output_path = base_dir / "agent_output_temporal_drift.txt"
schema_path = base_dir / "text_schema.yaml"
policies_path = base_dir / "text_policies.yaml"

with open(transcript_path) as f:
    transcript = f.read()

with open(output_path) as f:
    output_text = f.read()

with open(schema_path) as f:
    schema = yaml.safe_load(f)

with open(policies_path) as f:
    policies = yaml.safe_load(f)

print("Transcript excerpt:")
print(transcript[:200] + "...\n")

print("Output text:")
print(output_text)
print()

# Create payload
payload = {
    "source_text": transcript,
    "claims": {"body": output_text},
    "schema": schema,
    "policies": policies
}

print("Sending request...")
response = requests.post(
    f"{API_URL}/api/v1/validate",
    json=payload,
    headers={"Content-Type": "application/json"},
    timeout=120
)

if response.status_code != 200:
    print(f"Error {response.status_code}: {response.text}")
else:
    result = response.json()
    
    # Print raw JSON response
    print("\n" + "="*60)
    print("RAW JSON RESPONSE:")
    print("="*60)
    print(json.dumps(result, indent=2))
    print("="*60 + "\n")
    
    print(f"Overall Score: {result['overall_score']:.3f}")
    print(f"Total Claims: {result['total_claims']}")
    print(f"Supported: {result['supported_count']}")
    print(f"Refuted: {result['refuted_count']}")
    print(f"Insufficient: {result['insufficient_count']}")
    
    if result['total_claims'] == 0:
        print("\n⚠️  WARNING: 0 claims extracted!")
        print("This means the schema/extraction is not working.")
    
    print(f"\nDetailed Results:")
    for i, disp in enumerate(result['dispositions'], 1):
        verdict_emoji = {'supported': '✓', 'refuted': '✗', 'insufficient_evidence': '?'}.get(disp['verdict'], '•')
        print(f"\n{i}. {verdict_emoji} {disp['verdict'].upper()}")
        print(f"   Claim: {disp['claim_text']}")
        print(f"   Validator: {disp['validator']}")
        print(f"   Evidence: {disp['evidence_count']} spans")
        if disp.get('explanation'):
            print(f"   Explanation: {disp['explanation']}")
