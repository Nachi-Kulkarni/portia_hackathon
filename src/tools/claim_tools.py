from portia import Tool, ToolRunContext
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import json
import logging
import os
from datetime import datetime, date
from src.tools.policy_tools import PolicyInfo
from src.config import CLAIM_VALIDATION_CONFIG
from src.utils.exceptions import ClaimValidationError, InvalidDateFormatError

logger = logging.getLogger(__name__)

class ClaimInfo(BaseModel):
    """Claim information model"""
    claim_id: Optional[str] = Field(default="unknown")
    policy_number: Optional[str] = Field(default="unknown")
    claim_type: str
    incident_date: Optional[str] = Field(default="unknown")
    reported_date: Optional[str] = Field(default="unknown")
    estimated_amount: Optional[float] = Field(default=0.0)
    description: Optional[str] = Field(default="")
    supporting_documents: List[str] = Field(default_factory=list)
    customer_statement: str = ""

class ClaimValidationArgs(BaseModel):
    """Arguments for claim validation"""
    claim_info: Dict[str, Any] = Field(description="The claim information to validate")
    policy_info: Optional[Dict[str, Any]] = Field(default=None, description="The policy information for validation")

class ValidationResult(BaseModel):
    """Claim validation result"""
    is_valid: bool
    fraud_risk_score: float = Field(description="0-1 fraud risk score")
    validation_issues: List[str]
    requires_investigation: bool
    recommended_action: str

class ClaimValidationTool(Tool):
    """Validate insurance claim for authenticity and coverage"""
    
    def __init__(self):
        # Initialize the Tool with required parameters
        super().__init__(
            id="claim_validation",
            name="Claim Validation",
            description="Validate insurance claim for authenticity and coverage",
            args_schema=ClaimValidationArgs,
            output_schema=("json", "Validation result including fraud risk score and recommendations"),
            structured_output_schema=ValidationResult
        )
    
    def run(self, ctx: ToolRunContext, claim_info: Dict[str, Any], policy_info: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Comprehensive claim validation"""
        issues = []
        fraud_score = 0.0
        
        # Convert dict inputs to models for easier processing
        if isinstance(claim_info, dict):
            # Handle incomplete claim data by filling missing fields with defaults
            processed_claim_info = {
                'claim_id': claim_info.get('claim_id', 'unknown'),
                'policy_number': claim_info.get('policy_number', 'unknown'),
                'claim_type': claim_info.get('claim_type', 'unknown'),
                'incident_date': claim_info.get('incident_date', 'unknown'),
                'reported_date': claim_info.get('reported_date', 'unknown'),
                'estimated_amount': claim_info.get('estimated_amount', claim_info.get('claim_amount', 0.0)),
                'description': claim_info.get('description', f"{claim_info.get('claim_type', 'Unknown')} claim for ${claim_info.get('claim_amount', 0)}.")
            }
            claim = ClaimInfo(**processed_claim_info)
        else:
            claim = claim_info
            
        if policy_info and isinstance(policy_info, dict):
            policy = PolicyInfo(**policy_info)
        else:
            policy = policy_info
        
        # Check policy coverage if policy info provided
        if policy:
            if claim.claim_type not in policy.additional_coverages:
                issues.append(f"Claim type '{claim.claim_type}' not covered under policy")
            
            # Check claim amount against policy limits
            if claim.estimated_amount > policy.coverage_amount:
                issues.append(f"Claim amount ${claim.estimated_amount} exceeds policy limit ${policy.coverage_amount}")
        
        # Fraud risk indicators using configurable thresholds
        if claim.estimated_amount > CLAIM_VALIDATION_CONFIG.HIGH_VALUE_CLAIM_THRESHOLD:
            fraud_score += CLAIM_VALIDATION_CONFIG.HIGH_VALUE_FRAUD_SCORE_INCREASE
        
        # Check for late reporting with proper exception handling
        if hasattr(claim, 'incident_date') and claim.incident_date:
            try:
                # Handle various date formats
                date_str = claim.incident_date.replace('Z', '+00:00')
                incident_date = datetime.fromisoformat(date_str)
                days_since_incident = (datetime.now() - incident_date).days
                
                if days_since_incident > CLAIM_VALIDATION_CONFIG.LATE_REPORTING_DAYS_THRESHOLD:
                    fraud_score += CLAIM_VALIDATION_CONFIG.LATE_REPORTING_FRAUD_SCORE_INCREASE
                    logger.info(f"Late reporting detected: {days_since_incident} days since incident")
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not parse incident date '{claim.incident_date}': {e}")
                # Don't fail validation, but log the issue
                issues.append(f"Invalid incident date format: {claim.incident_date}")
            
        if len(claim.supporting_documents) < CLAIM_VALIDATION_CONFIG.MIN_SUPPORTING_DOCUMENTS:
            fraud_score += CLAIM_VALIDATION_CONFIG.INSUFFICIENT_DOCS_FRAUD_SCORE_INCREASE
            issues.append(f"Insufficient supporting documentation (need at least {CLAIM_VALIDATION_CONFIG.MIN_SUPPORTING_DOCUMENTS})")
        
        # Determine overall validity using configurable thresholds
        is_valid = len(issues) == 0 and fraud_score < CLAIM_VALIDATION_CONFIG.FRAUD_SCORE_THRESHOLD
        requires_investigation = fraud_score > CLAIM_VALIDATION_CONFIG.INVESTIGATION_THRESHOLD
        
        if is_valid:
            recommended_action = "approve_for_settlement"
        elif requires_investigation:
            recommended_action = "refer_to_investigation"
        else:
            recommended_action = "request_additional_information"
        
        return ValidationResult(
            is_valid=is_valid,
            fraud_risk_score=fraud_score,
            validation_issues=issues,
            requires_investigation=requires_investigation,
            recommended_action=recommended_action
        )