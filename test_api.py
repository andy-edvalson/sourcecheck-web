#!/usr/bin/env python3
"""
SourceCheck API - Python Test Script

Tests the API with sample data from sourcecheck-py
"""
import json
import sys
from pathlib import Path

import requests


API_URL = "http://localhost:8000"


def test_health():
    """Test the health endpoint"""
    print("1. Checking API health...")
    try:
        response = requests.get(f"{API_URL}/health")
        response.raise_for_status()
        health = response.json()
        print(f"Response: {json.dumps(health, indent=2)}")
        print()
        
        if health.get("status") == "healthy":
            print("✓ API is healthy!")
            return True
        else:
            print("❌ API is not healthy")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API is not responding: {e}")
        print("Make sure the API is running with ./run.sh")
        return False


def test_validation():
    """Test the validation endpoint with real data"""
    print()
    print("=" * 50)
    print("2. Testing validation with real data")
    print("=" * 50)
    print()
    
    # Read real transcript from local folder
    transcript_path = Path("../sourcecheck-py/local/real_transcript.txt")
    summary_path = Path("../sourcecheck-py/local/real_summary_hal.json")
    
    if not transcript_path.exists():
        print(f"❌ Transcript not found at: {transcript_path}")
        print("Make sure sourcecheck-py/local has the test files")
        return False
    
    if not summary_path.exists():
        print(f"❌ Summary not found at: {summary_path}")
        print("Make sure sourcecheck-py/local has the test files")
        return False
    
    print(f"Reading transcript from: {transcript_path}")
    with open(transcript_path) as f:
        transcript = f.read()
    
    print(f"Reading summary from: {summary_path}")
    with open(summary_path) as f:
        summary = json.load(f)
    
    # Use the summary as-is (with sections array structure)
    # The schema knows how to extract claims from this structure
    print(f"Summary has {len(summary.get('sections', []))} sections")
    
    # Load schema and policies
    schema_path = Path("../sourcecheck-py/local/sayvant_hpi-schema.yaml")
    policies_path = Path("../sourcecheck-py/local/sayvant_hpi-policy.yaml")
    
    if not schema_path.exists():
        print(f"❌ Schema not found at: {schema_path}")
        return False
    
    if not policies_path.exists():
        print(f"❌ Policies not found at: {policies_path}")
        return False
    
    print(f"Loading schema from: {schema_path}")
    import yaml
    with open(schema_path) as f:
        schema = yaml.safe_load(f)
    
    print(f"Loading policies from: {policies_path}")
    with open(policies_path) as f:
        policies = yaml.safe_load(f)
    
    # Create request payload with schema and policies
    # Send the summary with its sections array structure
    payload = {
        "source_text": transcript,
        "claims": summary,
        "schema": schema,
        "policies": policies
    }
    
    print()
    print("Sending validation request...")
    print()
    
    try:
        response = requests.post(
            f"{API_URL}/api/v1/validate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        
        # Pretty print response
        print(json.dumps(result, indent=2))
        
        # Print summary
        print()
        print("=" * 50)
        print("Summary")
        print("=" * 50)
        print(f"Overall Score: {result['overall_score']:.3f}")
        print(f"Total Claims: {result['total_claims']}")
        print(f"Supported: {result['supported_count']}")
        print(f"Refuted: {result['refuted_count']}")
        print(f"Insufficient Evidence: {result['insufficient_count']}")
        
        # Show per-claim results
        print()
        print("Per-Claim Results:")
        for disp in result['dispositions']:
            verdict_emoji = {
                'supported': '✓',
                'refuted': '✗',
                'insufficient_evidence': '?'
            }.get(disp['verdict'], '•')
            print(f"  {verdict_emoji} {disp['field']}: {disp['verdict']}")
        
        print()
        print("✓ Test complete!")
        print()
        print("View detailed results in the JSON output above")
        print("Or visit http://localhost:8000/docs for interactive testing")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("SourceCheck API - Test Script")
    print("=" * 50)
    print()
    
    # Test health
    if not test_health():
        sys.exit(1)
    
    # Test validation
    if not test_validation():
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
