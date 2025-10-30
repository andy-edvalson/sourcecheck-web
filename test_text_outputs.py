#!/usr/bin/env python3
"""
SourceCheck API - Text Output Test Script

Tests the API with text output files from sourcecheck-py/local
"""
import json
import sys
from pathlib import Path

import requests
import yaml


API_URL = "http://localhost:8000"


def test_text_output(output_file: Path, transcript_path: Path, schema_path: Path, policies_path: Path):
    """Test validation with a single text output file"""
    
    output_name = output_file.stem
    print(f"\n{'='*60}")
    print(f"Testing: {output_name}")
    print(f"{'='*60}\n")
    
    # Read transcript
    with open(transcript_path) as f:
        transcript = f.read()
    
    # Read output text
    with open(output_file) as f:
        output_text = f.read()
    
    # Load schema and policies
    with open(schema_path) as f:
        schema = yaml.safe_load(f)
    
    with open(policies_path) as f:
        policies = yaml.safe_load(f)
    
    # Wrap the text in a dict with "body" key
    # This keeps the API consistent - always expecting JSON/dict
    claims = {"body": output_text}
    
    # Create request payload
    payload = {
        "source_text": transcript,
        "claims": claims,
        "schema": schema,
        "policies": policies
    }
    
    print(f"Transcript length: {len(transcript)} chars")
    print(f"Output length: {len(output_text)} chars")
    print()
    
    try:
        response = requests.post(
            f"{API_URL}/api/v1/validate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # Longer timeout for processing
        )
        response.raise_for_status()
        result = response.json()
        
        # Print summary
        print(f"Overall Score: {result['overall_score']:.3f}")
        print(f"Total Claims: {result['total_claims']}")
        print(f"Supported: {result['supported_count']}")
        print(f"Refuted: {result['refuted_count']}")
        print(f"Insufficient Evidence: {result['insufficient_count']}")
        print(f"Support Rate: {result['support_rate']:.1%}")
        
        # Show per-claim results
        if result['dispositions']:
            print(f"\nClaim Results:")
            for disp in result['dispositions']:
                verdict_emoji = {
                    'supported': '✓',
                    'refuted': '✗',
                    'insufficient_evidence': '?'
                }.get(disp['verdict'], '•')
                
                claim_preview = disp['claim_text'][:80] + "..." if len(disp['claim_text']) > 80 else disp['claim_text']
                print(f"  {verdict_emoji} {disp['field']}: {disp['verdict']}")
                print(f"     \"{claim_preview}\"")
                print(f"     Validator: {disp['validator']}, Evidence: {disp['evidence_count']} spans")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def main():
    """Run all text output tests"""
    print("=" * 60)
    print("SourceCheck API - Text Output Tests")
    print("=" * 60)
    
    # Check API health
    print("\n1. Checking API health...")
    try:
        response = requests.get(f"{API_URL}/health")
        response.raise_for_status()
        health = response.json()
        if health.get("status") == "healthy":
            print("✓ API is healthy!")
        else:
            print("❌ API is not healthy")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ API is not responding: {e}")
        print("Make sure the API is running with ./run.sh")
        sys.exit(1)
    
    # Setup paths
    base_dir = Path("../sourcecheck-py/local")
    transcript_path = base_dir / "real_transcript.txt"
    schema_path = base_dir / "text_schema.yaml"
    policies_path = base_dir / "text_policies.yaml"
    
    # Check files exist
    if not transcript_path.exists():
        print(f"❌ Transcript not found: {transcript_path}")
        sys.exit(1)
    if not schema_path.exists():
        print(f"❌ Schema not found: {schema_path}")
        sys.exit(1)
    if not policies_path.exists():
        print(f"❌ Policies not found: {policies_path}")
        sys.exit(1)
    
    # Find all agent_output*.txt files
    output_files = sorted(base_dir.glob("agent_output*.txt"))
    
    if not output_files:
        print(f"❌ No agent_output*.txt files found in {base_dir}")
        sys.exit(1)
    
    print(f"\nFound {len(output_files)} output files to test")
    
    # Test each output file
    results = {}
    for output_file in output_files:
        result = test_text_output(output_file, transcript_path, schema_path, policies_path)
        if result:
            results[output_file.name] = result
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}\n")
    
    for filename, result in results.items():
        score = result['overall_score']
        supported = result['supported_count']
        total = result['total_claims']
        
        status = "✓" if score >= 0.8 else "⚠" if score >= 0.6 else "✗"
        print(f"{status} {filename:40s} Score: {score:.3f} ({supported}/{total} supported)")
    
    print(f"\n✓ All tests complete!")
    sys.exit(0)


if __name__ == "__main__":
    main()
