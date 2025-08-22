from portia import Tool, ToolRunContext
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime
from src.tools.policy_tools import PolicyInfo
from src.config import COMPLIANCE_CONFIG
from src.utils.exceptions import ComplianceViolationError

logger = logging.getLogger(__name__)

class ComplianceRule(BaseModel):
    """Regulatory compliance rule"""
    rule_id: str
    rule_type: str  # state, federal, internal
    description: str
    threshold_amount: Optional[float]
    required_approvals: List[str]
    documentation_required: List[str]

class ComplianceReport(BaseModel):
    """Compliance assessment report"""
    compliant: bool
    violations: List[str]
    warnings: List[str]
    required_approvals: List[str]
    additional_documentation: List[str]
    regulatory_notes: str
    risk_level: str  # low, medium, high, critical

class ComplianceCheckArgs(BaseModel):
    """Arguments for compliance check"""
    settlement_amount: float = Field(description="The settlement amount to check")
    claim_type: str = Field(description="The type of claim")
    state: str = Field(default="CA", description="The state for regulatory compliance")

class ComplianceCheckTool(Tool):
    """Ensure regulatory compliance for settlements"""
    
    def __init__(self):
        # Initialize the Tool with required parameters
        super().__init__(
            id="compliance_check",
            name="Compliance Check",
            description="Ensure regulatory compliance for settlements",
            args_schema=ComplianceCheckArgs,
            output_schema=("json", "Compliance report including violations and required approvals"),
            structured_output_schema=ComplianceReport
        )
    
    def run(self, ctx: ToolRunContext, settlement_amount: float, claim_type: str, state: str = "CA") -> ComplianceReport:
        """Comprehensive compliance check"""
        
        violations = []
        warnings = []
        required_approvals = []
        additional_docs = []
        risk_level = "low"
        
        # High-value settlement rules using configurable thresholds
        if settlement_amount > COMPLIANCE_CONFIG.SENIOR_MANAGER_APPROVAL_THRESHOLD:
            required_approvals.extend(["senior_manager", "legal_department"])
            additional_docs.append("detailed_justification_report")
            risk_level = "high"
            logger.info(f"High-value settlement detected: ${settlement_amount:,.2f}")
            
        if settlement_amount > COMPLIANCE_CONFIG.EXECUTIVE_APPROVAL_THRESHOLD:
            required_approvals.append("executive_approval")
            additional_docs.append("external_legal_review")
            risk_level = "critical"
            logger.warning(f"Critical-value settlement detected: ${settlement_amount:,.2f}")
        
        # State-specific regulations using configuration
        if state in COMPLIANCE_CONFIG.STATE_REGULATIONS:
            state_rule = COMPLIANCE_CONFIG.STATE_REGULATIONS[state]
            max_auto_settlement = state_rule["max_auto_settlement"]
            
            # Check auto claim limits
            if claim_type in ["auto", "auto_collision", "auto_comprehensive", "auto_total_loss"]:
                if settlement_amount > max_auto_settlement:
                    violation_msg = f"Settlement ${settlement_amount:,.2f} exceeds {state} maximum of ${max_auto_settlement:,.2f} for auto claims"
                    violations.append(violation_msg)
                    logger.error(f"Compliance violation: {violation_msg}")
            
            # Add required state disclosure
            required_disclosure = state_rule["required_disclosure"]
            additional_docs.append(required_disclosure)
            logger.debug(f"Added {state} required disclosure: {required_disclosure}")
        else:
            logger.warning(f"No specific regulations configured for state: {state}")
        
        # Time-based regulations
        current_time = datetime.now()
        if current_time.weekday() >= 5:  # Weekend (Saturday=5, Sunday=6)
            warning_msg = f"Settlement processed on weekend ({current_time.strftime('%A')}) - verify business day requirements"
            warnings.append(warning_msg)
            logger.info(f"Weekend processing detected: {warning_msg}")
        
        # Determine overall compliance and log results
        compliant = len(violations) == 0
        
        if not compliant:
            logger.error(f"Compliance check failed with {len(violations)} violations for ${settlement_amount:,.2f} settlement")
        else:
            logger.info(f"Compliance check passed for ${settlement_amount:,.2f} settlement in {state}")
        
        report = ComplianceReport(
            compliant=compliant,
            violations=violations,
            warnings=warnings,
            required_approvals=required_approvals,
            additional_documentation=additional_docs,
            regulatory_notes=f"Compliance check completed for {state} jurisdiction at {current_time.isoformat()}",
            risk_level=risk_level
        )
        
        # Log summary
        logger.info(f"Compliance report generated: {len(violations)} violations, {len(warnings)} warnings, {len(required_approvals)} approvals needed")
        
        return report