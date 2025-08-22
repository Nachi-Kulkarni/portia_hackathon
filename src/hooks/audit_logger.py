# Apply compatibility fix for Python < 3.12 BEFORE importing anything that uses Portia
try:
    import src.compatibility_fix  # This patches typing.override
except ImportError:
    pass  # Continue without compatibility fix

from portia import Tool, ToolRunContext
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import logging
import uuid

logger = logging.getLogger(__name__)

class AuditEntry(BaseModel):
    """Individual audit trail entry"""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str
    tool_name: Optional[str]
    arguments: Dict[str, Any]
    result: Any
    user_id: Optional[str]
    plan_run_id: Optional[str]
    step_index: Optional[int]
    compliance_flags: List[str] = []
    risk_indicators: List[str] = []
    justification: Optional[str]

class ComplianceReport(BaseModel):
    """Comprehensive compliance report"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    plan_run_id: str
    total_actions: int
    compliance_violations: List[str]
    high_risk_actions: List[str]
    regulatory_notes: List[str]
    summary: str

class AuditTrailManager:
    """Manages comprehensive audit trails for regulatory compliance"""
    
    def __init__(self):
        self.audit_entries: List[AuditEntry] = []
        self.compliance_rules = self._load_compliance_rules()
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules and regulations"""
        # In a real implementation, this would load from a regulatory database
        return {
            "high_value_threshold": 50000,
            "approval_required_threshold": 25000,
            "documentation_requirements": {
                "high_value": ["supervisor_approval", "compliance_review"],
                "complex_claims": ["detailed_justification", "legal_review"]
            }
        }
    
    def log_action(self, entry: AuditEntry) -> None:
        """Log an action to the audit trail"""
        self.audit_entries.append(entry)
        logger.info(f"Audit entry logged: {entry.action_type} - {entry.tool_name}")
    
    def check_compliance(self, entry: AuditEntry) -> List[str]:
        """Check if an action complies with regulations"""
        violations = []
        
        # Check for high-value transactions requiring approval
        if entry.action_type == "settlement_offer":
            amount = entry.arguments.get("amount", 0)
            if amount > self.compliance_rules["approval_required_threshold"]:
                # Check if required approvals are present
                approvals = entry.arguments.get("approvals", [])
                required_approvals = self.compliance_rules["documentation_requirements"]["high_value"]
                missing_approvals = [req for req in required_approvals if req not in approvals]
                
                if missing_approvals:
                    violations.append(f"Missing required approvals: {missing_approvals}")
        
        # Check for complex claim handling
        if entry.action_type == "claim_validation" and entry.arguments.get("complexity") == "high":
            required_docs = self.compliance_rules["documentation_requirements"]["complex_claims"]
            provided_docs = entry.arguments.get("documentation", [])
            missing_docs = [doc for doc in required_docs if doc not in provided_docs]
            
            if missing_docs:
                violations.append(f"Missing required documentation for complex claim: {missing_docs}")
        
        # Add any existing compliance flags
        violations.extend(entry.compliance_flags)
        
        return violations
    
    def generate_compliance_report(self, plan_run_id: str) -> ComplianceReport:
        """Generate a comprehensive compliance report for a plan run"""
        # Filter entries for this plan run
        plan_entries = [entry for entry in self.audit_entries if entry.plan_run_id == plan_run_id]
        
        # Identify violations and high-risk actions
        all_violations = []
        high_risk_actions = []
        regulatory_notes = []
        
        for entry in plan_entries:
            violations = self.check_compliance(entry)
            all_violations.extend(violations)
            
            # Identify high-risk actions
            if entry.risk_indicators or violations:
                high_risk_actions.append(f"{entry.action_type} - {entry.tool_name}")
            
            # Add regulatory notes
            if entry.justification:
                regulatory_notes.append(f"{entry.action_type}: {entry.justification}")
        
        # Generate summary
        total_actions = len(plan_entries)
        if all_violations:
            summary = f"Compliance issues detected in {len(all_violations)} out of {total_actions} actions."
        else:
            summary = f"All {total_actions} actions compliant with regulations."
        
        return ComplianceReport(
            plan_run_id=plan_run_id,
            total_actions=total_actions,
            compliance_violations=all_violations,
            high_risk_actions=high_risk_actions,
            regulatory_notes=regulatory_notes,
            summary=summary
        )
    
    def get_full_audit_trail(self, plan_run_id: Optional[str] = None) -> List[AuditEntry]:
        """Retrieve the complete audit trail, optionally filtered by plan run"""
        if plan_run_id:
            return [entry for entry in self.audit_entries if entry.plan_run_id == plan_run_id]
        return self.audit_entries.copy()
    
    def export_audit_trail(self, plan_run_id: Optional[str] = None, format: str = "json") -> str:
        """Export audit trail in specified format"""
        entries = self.get_full_audit_trail(plan_run_id)
        
        if format.lower() == "json":
            return json.dumps([entry.dict() for entry in entries], indent=2)
        else:
            # Default to JSON even if format not recognized
            return json.dumps([entry.dict() for entry in entries], indent=2)

class AuditLoggerTool:
    """Audit logging utility for regulatory compliance"""
    
    def __init__(self):
        self.audit_manager = AuditTrailManager()
    
    def log_action(self, action_type: str, arguments: Dict[str, Any], 
                  result: Any, compliance_flags: List[str] = None, 
                  risk_indicators: List[str] = None, justification: str = None) -> Dict[str, Any]:
        """Log an action to the audit trail"""
        
        # Create audit entry
        entry = AuditEntry(
            action_type=action_type,
            tool_name="audit_logger",
            arguments=arguments,
            result=result,
            user_id="system",
            plan_run_id="audit-log",
            step_index=0,
            compliance_flags=compliance_flags or [],
            risk_indicators=risk_indicators or [],
            justification=justification
        )
        
        # Log the entry
        self.audit_manager.log_action(entry)
        
        # Check compliance
        violations = self.audit_manager.check_compliance(entry)
        
        return {
            "entry_id": entry.entry_id,
            "logged_at": entry.timestamp,
            "compliance_violations": violations,
            "requires_review": len(violations) > 0
        }

class ComplianceReportTool(Tool):
    """Portia tool for generating compliance reports"""
    
    def __init__(self):
        super().__init__()
        self.audit_manager = AuditTrailManager()
    
    def run(self, ctx: ToolRunContext, plan_run_id: str) -> ComplianceReport:
        """Generate compliance report for a plan run"""
        return self.audit_manager.generate_compliance_report(plan_run_id)