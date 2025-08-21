from portia.tool import Tool, ToolRunContext
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import json
import logging
import os
from datetime import datetime, date

logger = logging.getLogger(__name__)

class PolicyInfo(BaseModel):
    """Policy information model"""
    policy_number: str
    customer_id: str
    policy_type: str  # auto, home, life, etc.
    coverage_amount: float
    deductible: float
    premium_amount: float
    status: str  # active, expired, suspended
    effective_date: str
    expiration_date: str
    exclusions: List[str]
    additional_coverages: Dict[str, Any]

class PolicyLookupArgs(BaseModel):
    """Arguments for policy lookup"""
    policy_number: str = Field(description="The policy number to look up")

class PolicyLookupTool(Tool):
    """Look up policy details from insurance database"""
    
    def __init__(self):
        # Initialize the Tool with required parameters
        super().__init__(
            id="policy_lookup",
            name="Policy Lookup",
            description="Look up policy details from insurance database",
            args_schema=PolicyLookupArgs,
            output_schema=("json", "Policy information including coverage details"),
            structured_output_schema=PolicyInfo
        )
    
    def run(self, ctx: ToolRunContext, policy_number: str) -> Optional[PolicyInfo]:
        """Retrieve policy information"""
        try:
            # In a real implementation, this would query a database or external API
            # For now, we'll use the mock data as a starting point for actual implementation
            mock_data_path = os.getenv("MOCK_POLICY_DB_PATH", "./src/data/mock_policies.json")
            
            with open(mock_data_path, 'r') as f:
                data = json.load(f)
            
            # Find policy in mock data
            for policy in data.get("policies", []):
                if policy["policy_number"] == policy_number:
                    # Convert the mock data to match our PolicyInfo model
                    converted_policy = {
                        "policy_number": policy["policy_number"],
                        "customer_id": policy["customer_id"],
                        "policy_type": policy["policy_type"],
                        "coverage_amount": policy["coverage_amount"],
                        "deductible": policy["deductible"],
                        "premium_amount": policy.get("premium", 0),  # Handle missing premium field
                        "status": policy["status"],
                        "effective_date": policy["effective_date"],
                        "expiration_date": policy["expiration_date"],
                        "exclusions": policy["exclusions"],
                        "additional_coverages": policy["additional_coverages"]
                    }
                    return PolicyInfo(**converted_policy)
            
            # Policy not found
            logger.warning(f"Policy {policy_number} not found")
            return None
            
        except Exception as e:
            logger.error(f"Error looking up policy {policy_number}: {str(e)}")
            return None