from portia.tool import Tool, ToolRunContext
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime
from src.tools.policy_tools import PolicyInfo

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
        
        # High-value settlement rules
        if settlement_amount > 100000:
            required_approvals.extend(["senior_manager", "legal_department"])
            additional_docs.append("detailed_justification_report")
            risk_level = "high"
            
        if settlement_amount > 250000:
            required_approvals.append("executive_approval")
            additional_docs.append("external_legal_review")
            risk_level = "critical"
        
        # State-specific regulations (simplified example)
        state_rules = {
            "CA": {
                "max_auto_settlement": 50000,
                "required_disclosure": "california_consumer_privacy_notice"
            },
            "NY": {
                "max_auto_settlement": 45000,
                "required_disclosure": "new_york_insurance_disclosure"
            }
        }
        
        if state in state_rules:
            state_rule = state_rules[state]
            if claim_type == "auto" and settlement_amount > state_rule["max_auto_settlement"]:
                violations.append(f"Settlement exceeds {state} maximum for auto claims")
            
            additional_docs.append(state_rule["required_disclosure"])
        
        # Time-based regulations
        if datetime.now().weekday() >= 5:  # Weekend
            warnings.append("Settlement processed on weekend - verify business day requirements")
        
        # Determine overall compliance
        compliant = len(violations) == 0
        
        return ComplianceReport(
            compliant=compliant,
            violations=violations,
            warnings=warnings,
            required_approvals=required_approvals,
            additional_documentation=additional_docs,
            regulatory_notes=f"Compliance check completed for {state} jurisdiction",
            risk_level=risk_level
        )