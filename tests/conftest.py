import pytest
from portia import Portia, Config
from unittest.mock import Mock, MagicMock
import os
import sys
import asyncio

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def test_config():
    """Test Portia configuration"""
    return Config.from_default()

@pytest.fixture  
def mock_portia():
    """Mock Portia instance for testing"""
    mock = Mock(spec=Portia)
    mock.plan = MagicMock()
    mock.run_plan = MagicMock()
    return mock

@pytest.fixture
def sample_claim_data():
    """Sample claim data for testing"""
    return {
        "claim_id": "CLM-TEST-001",
        "policy_number": "POL-2024-001", 
        "claim_type": "auto_collision",
        "estimated_amount": 12000,
        "customer_emotion": "frustrated",
        "customer_id": "CUST-001",
        "incident_date": "2024-01-15",
        "state": "CA"
    }

@pytest.fixture
def sample_policy_data():
    """Sample policy data for testing"""
    return {
        "policy_number": "POL-2024-001",
        "customer_id": "CUST-001",
        "policy_type": "auto",
        "coverage_amount": 250000,
        "deductible": 1000,
        "premium_amount": 1200,
        "status": "active",
        "effective_date": "2024-01-01",
        "expiration_date": "2025-01-01",
        "exclusions": ["racing", "commercial use"],
        "additional_coverages": {
            "auto_collision": True,
            "auto_comprehensive": True,
            "auto_total_loss": True
        }
    }

@pytest.fixture
def mock_plan_run():
    """Mock plan run result"""
    mock = MagicMock()
    mock.id = "plan_run_test_123"
    mock.state.name = "COMPLETE"
    mock.outputs.final_output.value = {"settlement_amount": 11000}
    mock.outputs.clarifications = []
    return mock

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_environment(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("MOCK_POLICY_DB_PATH", "./src/data/mock_policies.json")
    monkeypatch.setenv("ENABLE_AUDIT_LOGGING", "false")
    monkeypatch.setenv("HUME_API_KEY", "test_key")
    monkeypatch.setenv("HUME_SECRET_KEY", "test_secret")