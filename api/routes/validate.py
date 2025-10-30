"""
Validation endpoint
"""
from fastapi import APIRouter, HTTPException
from api.models import ValidationRequest, ValidationResponse, ClaimDisposition

# Import sourcecheck library
try:
    from sourcecheck import Checker
    SOURCECHECK_AVAILABLE = True
except ImportError:
    SOURCECHECK_AVAILABLE = False
    Checker = None

router = APIRouter()

# Cache the checker instance (loaded once on startup)
_checker = None


@router.post("/validate", response_model=ValidationResponse)
async def validate_claims(request: ValidationRequest):
    """
    Validate claims against source text
    
    Takes a source document, claims, schema, and policies, then validates 
    each claim using the sourcecheck library.
    
    Returns detailed validation results including:
    - Overall score
    - Per-claim verdicts (supported/refuted/insufficient_evidence)
    - Evidence spans
    - Validator explanations
    """
    if not SOURCECHECK_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="sourcecheck library not available"
        )
    
    try:
        # Create checker with configs from request
        checker = Checker(
            schema=request.schema,
            policies=request.policies
        )
        
        # Run validation
        report = checker.verify_summary(
            transcript=request.source_text,
            summary=request.claims
        )
        
        # Convert dispositions to response format
        dispositions = [
            ClaimDisposition(
                field=d.claim.field,
                claim_text=d.claim.text,
                verdict=d.verdict,
                evidence_count=d.evidence_count,
                validator=d.validator,
                explanation=d.explanation,
                score=d.confidence,  # Semantic/validator confidence score
                quality_score=d.quality_score,
                quality_issues=[
                    {
                        "type": issue.type,
                        "severity": issue.severity,
                        "detail": issue.detail,
                        "suggestion": issue.suggestion
                    }
                    for issue in d.quality_issues
                ]
            )
            for d in report.dispositions
        ]
        
        return ValidationResponse(
            overall_score=report.overall_score,
            total_claims=report.total_claims,
            supported_count=report.supported_count,
            refuted_count=report.refuted_count,
            insufficient_count=report.insufficient_count,
            support_rate=report.support_rate,
            dispositions=dispositions
        )
        
    except Exception as e:
        # Log the full stack trace
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR: Validation failed")
        print(error_trace)
        
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}\n\nStack trace:\n{error_trace}"
        )
