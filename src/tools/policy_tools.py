from portia import Tool, ToolRunContext
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import json
import logging
import os
from datetime import datetime, date
from src.utils.exceptions import PolicyNotFoundError, ConfigurationError

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
        """Retrieve policy information with proper error handling"""
        logger.info(f"Looking up policy: {policy_number}")
        
        try:
            # In a real implementation, this would query a database or external API
            mock_data_path = os.getenv("MOCK_POLICY_DB_PATH", "./src/data/mock_policies.json")
            
            if not os.path.exists(mock_data_path):
                raise ConfigurationError("MOCK_POLICY_DB_PATH", f"Policy database file not found: {mock_data_path}")
            
            try:
                with open(mock_data_path, 'r') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in policy database: {e}")
                raise ConfigurationError("MOCK_POLICY_DB_PATH", f"Invalid JSON format in policy database: {e}")
            except IOError as e:
                logger.error(f"Could not read policy database: {e}")
                raise ConfigurationError("MOCK_POLICY_DB_PATH", f"Could not read policy database: {e}")
            
            # Find policy in mock data
            policies = data.get("policies", [])
            if not isinstance(policies, list):
                raise ConfigurationError("MOCK_POLICY_DB_PATH", "Policy database must contain 'policies' array")
            
            for policy in policies:
                if policy.get("policy_number") == policy_number:
                    try:
                        # Convert the mock data to match our PolicyInfo model
                        converted_policy = {
                            "policy_number": policy["policy_number"],
                            "customer_id": policy["customer_id"],
                            "policy_type": policy["policy_type"],
                            "coverage_amount": policy["coverage_amount"],
                            "deductible": policy["deductible"],
                            "premium_amount": policy.get("premium", policy.get("premium_amount", 0)),
                            "status": policy["status"],
                            "effective_date": policy["effective_date"],
                            "expiration_date": policy["expiration_date"],
                            "exclusions": policy.get("exclusions", []),
                            "additional_coverages": policy.get("additional_coverages", {})
                        }
                        
                        policy_info = PolicyInfo(**converted_policy)
                        logger.info(f"Found policy {policy_number}: {policy_info.policy_type}, ${policy_info.coverage_amount:,.2f} coverage")
                        return policy_info
                        
                    except KeyError as e:
                        logger.error(f"Missing required field in policy {policy_number}: {e}")
                        raise ConfigurationError("MOCK_POLICY_DB_PATH", f"Policy {policy_number} missing required field: {e}")
                    except (TypeError, ValueError) as e:
                        logger.error(f"Invalid data type in policy {policy_number}: {e}")
                        raise ConfigurationError("MOCK_POLICY_DB_PATH", f"Invalid data in policy {policy_number}: {e}")
            
            # Policy not found - this is a business logic issue, not a system error
            logger.warning(f"Policy {policy_number} not found in database with {len(policies)} policies")
            raise PolicyNotFoundError(policy_number)
            
        except (PolicyNotFoundError, ConfigurationError):
            # Re-raise business logic and configuration errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error looking up policy {policy_number}: {str(e)}")
            raise ConfigurationError("POLICY_LOOKUP", f"Unexpected error: {str(e)}")