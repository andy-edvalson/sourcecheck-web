"""
Pydantic models for request/response validation
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ValidationRequest(BaseModel):
    """Request model for validation endpoint"""
    source_text: str = Field(
        ...,
        description="The source document text to validate against",
        example="Patient reports chest pain for 2 days..."
    )
    claims: Dict[str, Any] = Field(
        ...,
        description="Dictionary of claims to validate (field_name: claim_text)",
        example={
            "chief_complaint": "Chest pain for 2 days",
            "medications": "Aspirin 81mg daily"
        }
    )
    schema: Dict[str, Any] = Field(
        ...,
        description="Schema configuration as dict (required)",
        example={"version": "1.0", "fields": {}}
    )
    policies: Dict[str, Any] = Field(
        ...,
        description="Policies configuration as dict (required)",
        example={"version": "1.0", "validators": {}}
    )


class QualityIssue(BaseModel):
    """Quality issue detected in a claim"""
    type: str
    severity: str
    detail: str
    suggestion: Optional[str] = None


class EvidenceSpan(BaseModel):
    """Evidence span supporting/refuting a claim"""
    text: str = Field(..., description="Evidence text snippet")
    score: float = Field(..., description="Relevance score (0.0-1.0)")


class ClaimDisposition(BaseModel):
    """Individual claim validation result"""
    field: str
    claim_text: str
    verdict: str  # "supported", "refuted", "insufficient_evidence"
    evidence_count: int
    validator: str
    explanation: Optional[str] = None
    score: Optional[float] = Field(None, description="Semantic/validator confidence score (0.0-1.0)")
    quality_score: Optional[float] = Field(None, description="Quality analysis score (0.0-1.0)")
    quality_issues: List[QualityIssue] = Field(default_factory=list)
    evidence: List[EvidenceSpan] = Field(default_factory=list, description="Top evidence spans (up to 3)")


class ValidationResponse(BaseModel):
    """Response model for validation endpoint"""
    overall_score: float = Field(
        ...,
        description="Overall validation score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    total_claims: int = Field(
        ...,
        description="Total number of claims validated"
    )
    supported_count: int = Field(
        ...,
        description="Number of supported claims"
    )
    refuted_count: int = Field(
        ...,
        description="Number of refuted claims"
    )
    insufficient_count: int = Field(
        ...,
        description="Number of claims with insufficient evidence"
    )
    support_rate: float = Field(
        ...,
        description="Percentage of claims supported",
        ge=0.0,
        le=1.0
    )
    dispositions: List[ClaimDisposition] = Field(
        ...,
        description="Detailed results for each claim"
    )


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., example="healthy")
    version: str = Field(..., example="0.1.0")
    models_loaded: bool = Field(..., example=True)
