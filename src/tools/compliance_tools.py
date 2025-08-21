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

class ComplianceCheckTool(Tool):
    """Ensure regulatory compliance for settlements"""
    
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

class SettlementOfferTool(Tool):
    """Generate final settlement offer with compliance"""
    
    def run(self, ctx: ToolRunContext, 
            recommended_amount: float, 
            policy_info: Optional[Dict[str, Any]],
            compliance_report: Optional[Dict[str, Any]],
            customer_emotion: str = "neutral") -> Dict[str, Any]:
        """Generate compliant settlement offer"""
        
        # Convert dict inputs to models if needed
        if compliance_report and isinstance(compliance_report, dict):
            compliance = ComplianceReport(**compliance_report)
        else:
            compliance = compliance_report
            
        if policy_info and isinstance(policy_info, dict):
            policy = PolicyInfo(**policy_info)
        else:
            policy = policy_info
        
        # Adjust offer based on compliance requirements
        final_amount = recommended_amount
        
        if compliance and not compliance.compliant:
            # Reduce offer if compliance issues exist
            final_amount *= 0.9
        
        # Apply deductible if policy info available
        if policy:
            final_amount = max(0, final_amount - policy.deductible)
        
        # Emotional adjustment (within compliance bounds)
        if customer_emotion == "extreme_distress" and final_amount < 100000:
            final_amount *= 1.05  # Small goodwill adjustment
        
        # Generate offer structure
        offer = {
            "settlement_amount": final_amount,
            "breakdown": {
                "gross_settlement": recommended_amount,
                "deductible": policy.deductible if policy else 0,
                "net_settlement": final_amount
            },
            "conditions": [
                "Final and complete settlement",
                "Release of all claims",
                f"Payment within {7 if not compliance or compliance.risk_level == 'low' else 14} business days"
            ],
            "required_approvals": compliance.required_approvals if compliance else [],
            "compliance_notes": compliance.regulatory_notes if compliance else "Standard compliance check passed",
            "expires_in_days": 30
        }
        
        return offer