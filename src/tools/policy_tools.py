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

class PolicyLookupTool(Tool):
    """Look up policy details from insurance database"""
    
    def __init__(self):
        super().__init__()
        self.mock_data_path = os.getenv("MOCK_POLICY_DB_PATH", "./src/data/mock_policies.json")
    
    def run(self, ctx: ToolRunContext, policy_number: str) -> Optional[PolicyInfo]:
        """Retrieve policy information"""
        try:
            # In production, this would query real insurance database
            # For demo, use mock data
            with open(self.mock_data_path, 'r') as f:
                data = json.load(f)
            
            # Find policy in mock data
            for policy in data.get("policies", []):
                if policy["policy_number"] == policy_number:
                    return PolicyInfo(**policy)
            
            # Policy not found
            logger.warning(f"Policy {policy_number} not found")
            return None
            
        except Exception as e:
            logger.error(f"Error looking up policy {policy_number}: {str(e)}")
            return None