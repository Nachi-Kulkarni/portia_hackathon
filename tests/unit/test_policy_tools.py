import pytest
from unittest.mock import Mock, mock_open, patch
from src.tools.policy_tools import PolicyLookupTool, PolicyInfo

class TestPolicyLookupTool:
    
    def test_policy_lookup_success(self, mock_environment):
        """Test successful policy lookup"""
        # Mock the file content
        mock_data = {
            "policies": [{
                "policy_number": "POL-2024-001",
                "customer_id": "CUST-001",
                "policy_type": "auto",
                "coverage_amount": 250000,
                "deductible": 1000,
                "premium_amount": 1200,
                "status": "active",
                "effective_date": "2024-01-01",
                "expiration_date": "2025-01-01",
                "exclusions": ["racing"],
                "additional_coverages": {"auto_collision": True}
            }]
        }
        
        with patch("builtins.open", mock_open(read_data='{"policies": [{"policy_number": "POL-2024-001", "customer_id": "CUST-001", "policy_type": "auto", "coverage_amount": 250000, "deductible": 1000, "premium_amount": 1200, "status": "active", "effective_date": "2024-01-01", "expiration_date": "2025-01-01", "exclusions": ["racing"], "additional_coverages": {"auto_collision": true}}]}')):
            with patch("json.load", return_value=mock_data):
                tool = PolicyLookupTool()
                mock_ctx = Mock()
                
                result = tool.run(mock_ctx, "POL-2024-001")
                
                assert result is not None
                assert isinstance(result, PolicyInfo)
                assert result.policy_number == "POL-2024-001"
                assert result.coverage_amount == 250000
    
    def test_policy_lookup_not_found(self, mock_environment):
        """Test policy not found scenario"""
        mock_data = {"policies": []}
        
        with patch("builtins.open", mock_open()):
            with patch("json.load", return_value=mock_data):
                tool = PolicyLookupTool()
                mock_ctx = Mock()
                
                result = tool.run(mock_ctx, "NONEXISTENT-POLICY")
                
                assert result is None
    
    def test_policy_lookup_file_error(self, mock_environment):
        """Test file reading error handling"""
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            tool = PolicyLookupTool()
            mock_ctx = Mock()
            
            result = tool.run(mock_ctx, "POL-2024-001")
            
            assert result is None
    
    def test_policy_info_model(self):
        """Test PolicyInfo model validation"""
        policy_data = {
            "policy_number": "POL-2024-001",
            "customer_id": "CUST-001",
            "policy_type": "auto",
            "coverage_amount": 250000,
            "deductible": 1000,
            "premium_amount": 1200,
            "status": "active",
            "effective_date": "2024-01-01",
            "expiration_date": "2025-01-01",
            "exclusions": ["racing"],
            "additional_coverages": {"auto_collision": True}
        }
        
        policy = PolicyInfo(**policy_data)
        
        assert policy.policy_number == "POL-2024-001"
        assert policy.coverage_amount == 250000
        assert policy.additional_coverages["auto_collision"] is True