"""
Module: schemas.py
System: Multi-Agent Insurance Claims Resolution Framework
Component: Step 1 - Centralized State & Data Validation Boundary (Pydantic V2 Native)

Description:
    This module establishes the data contract layer for the multi-agent system.
    Upgraded natively to Pydantic V2, it enforces type-safety boundaries, 
    string-to-float coercion, and runtime domain invariants without legacy warnings.

References:
    - Pydantic V2 Field & Migration Guide: https://errors.pydantic.dev/2.13/migration/
    - Core Ingest Architecture: WhiteboxHub Assignment Specifications
"""

from pydantic import BaseModel, Field, field_validator  # Updated import for V2
from typing import List, Optional


class ClaimSubmission(BaseModel):
    """
    Data Transfer Object (DTO).
    Parses, coerces, and sanitizes incoming raw JSON claim payloads.
    """
    claim_id: str = Field(..., description="Unique code identifying the specific claim.")
    customer_id: str = Field(..., description="Unique key linking to the customer's profile.")
    policy_type: str = Field(..., description="Liability category, e.g., Auto or Health.")
    incident_description: str = Field(..., description="Natural language details explaining the accident event.")
    estimated_damage: float = Field(..., description="Preliminary financial cost estimation of the damage.")
    documents: List[str] = Field(default=[], description="List of uploaded tracking filenames or invoices.")

    # Modern Pydantic V2 Field Validator Syntax
    @field_validator('estimated_damage')
    @classmethod  # Pydantic V2 field_validators must be written as class methods
    def verify_positive_damage_value(cls, valuation: float) -> float:
        """
        Defensive programming validation step. Ensures that monetary numbers 
        are strictly positive before allowing downstream agents to execute math.
        """
        if valuation <= 0:
            raise ValueError(
                f"Data Integrity Violation: Estimated damage must be a positive number greater than $0.00. "
                f"Provided valuation: {valuation}"
            )
        return valuation


class SystemState(BaseModel):
    """
    Global Shared Memory Tracker.
    Preserves application context, multi-agent outputs, and retry loops.
    """
    claim: Optional[ClaimSubmission] = None
    missing_fields: List[str] = Field(default=[])
    
    # Document Verification Agent Outputs
    is_policy_active: Optional[bool] = None
    coverage_limit: float = Field(default=0.0)
    deductible: float = Field(default=0.0)
    ocr_extracted_text: Optional[str] = None
    document_authenticity_score: float = Field(default=1.0)
    verification_report: dict = Field(default={})
    
    # Fraud Detection Agent Outputs
    fraud_score: float = Field(default=0.0)
    fraud_signals: List[str] = Field(default=[])
    fraud_explanation: Optional[str] = None
    
    # Payout Estimation Agent Outputs
    estimated_payout: float = Field(default=0.0)
    adjustment_notes: Optional[str] = None
    
    # Decision Agent Matrix
    final_decision: Optional[str] = None  # Constraints: "approve" | "reject" | "escalate"
    decision_reasoning: Optional[str] = None
    
    # Communication Agent Outputs
    customer_email: Optional[str] = None
    adjuster_summary: Optional[str] = None
    
    # Resilience & Fault Tolerance Trackers (Fulfills Loop/Retry Requirements)
    # Using V2 'default_factory' pattern to safely handle mutable dictionary states
    retry_counts: dict = Field(
        default_factory=lambda: {"ocr": 0, "fraud_api": 0}, 
        description="Tracks graph iterations to prevent infinite execution loops."
    )


# =====================================================================
# INTERACTIVE DATA PROCESSING ENGINE DEMO
# =====================================================================
if __name__ == "__main__":
    print("==========================================================")
    print("⚙️ RUNNING STEP 1: DATA INGESTION & COERCION LIFECYCLE  ⚙️")
    print("==========================================================\n")

    # TEST A: Demonstrating Native String-to-Float Data Coercion
    print("[Ingest Test A] Receiving raw network transmission string formatting...")
    raw_payload = {
        "claim_id": "CLM-9942",
        "customer_id": "CUS-921",
        "policy_type": "Auto",
        "incident_description": "Frontal collision on Highway 101 involving minor property impact.",
        "estimated_damage": "4800.50",
        "documents": ["invoice_01.pdf", "scene_photo.jpg"]
    }
    
    validated_data = ClaimSubmission(**raw_payload)
    print("✅ Ingest Success: Pydantic compiled data into structured Memory.")
    print(f"   -> Original Incoming Type: 'str' (\"4800.50\")")
    print(f"   -> Sanitized Clean Value: {validated_data.estimated_damage}")
    print(f"   -> Coerced Internal Type: {type(validated_data.estimated_damage)}\n")
    # TEST B: Forcing Custom Constraint Error Handling
    print("[Ingest Test B] Simulating a malformed negative financial asset input...")
    malicious_payload = {
        "claim_id": "CLM-ERROR-TEST",
        "customer_id": "CUS-921",
        "policy_type": "Auto",
        "incident_description": "Testing edge case constraints.",
        "estimated_damage": -250.00,
        "documents": []
    }
    
    try:
        invalid_data = ClaimSubmission(**malicious_payload)
    except ValueError as context_error:
        print("❌ Blocked: Pydantic safely caught and threw a ValidationError.")
        print(f"⚠️ Generated Error Stack Trace Logs:\n{context_error}")