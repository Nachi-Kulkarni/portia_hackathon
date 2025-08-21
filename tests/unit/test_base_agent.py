import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from src.agents.base_agent import BaseInsuranceAgent

class TestBaseInsuranceAgent:
    
    def test_agent_initialization(self, mock_environment):
        """Test basic agent initialization"""
        agent = BaseInsuranceAgent("test_agent")
        
        assert agent.agent_name == "test_agent"
        assert agent.config is not None
        assert agent.portia is not None
    
    def test_tool_registry_setup(self, mock_environment):
        """Test tool registry is properly configured"""
        agent = BaseInsuranceAgent("test_agent")
        tools = agent._setup_tool_registry()
        
        assert tools is not None
        # Tools should include policy lookup, claim validation, and compliance
        # This is a basic test since we're using mock tools
    
    @pytest.mark.asyncio
    async def test_process_claim_basic(self, mock_environment, sample_claim_data):
        """Test basic claim processing"""
        with patch('src.agents.base_agent.Portia') as mock_portia_class:
            # Setup mock
            mock_portia_instance = Mock()
            mock_plan = Mock()
            mock_plan.id = "test_plan_123"
            
            mock_plan_run = Mock()
            mock_plan_run.id = "test_run_123"
            mock_plan_run.state.name = "COMPLETE"
            mock_plan_run.outputs.final_output.value = {"result": "success"}
            
            mock_portia_instance.plan.return_value = mock_plan
            mock_portia_instance.run_plan.return_value = mock_plan_run
            mock_portia_class.return_value = mock_portia_instance
            
            agent = BaseInsuranceAgent("test_agent")
            result = await agent.process_claim(sample_claim_data)
            
            assert result is not None
            assert result["claim_id"] == "CLM-TEST-001"
            assert result["processing_status"] == "completed"
            assert result["plan_run_id"] == "test_run_123"
    
    @pytest.mark.asyncio
    async def test_process_claim_error_handling(self, mock_environment, sample_claim_data):
        """Test error handling in claim processing"""
        with patch('src.agents.base_agent.Portia') as mock_portia_class:
            # Setup mock to raise exception
            mock_portia_instance = Mock()
            mock_portia_instance.plan.side_effect = Exception("Test error")
            mock_portia_class.return_value = mock_portia_instance
            
            agent = BaseInsuranceAgent("test_agent")
            result = await agent.process_claim(sample_claim_data)
            
            assert result["processing_status"] == "error"
            assert "Test error" in result["error_message"]
            assert result["claim_id"] == "CLM-TEST-001"
    
    def test_before_tool_call_hook_high_value(self, mock_environment):
        """Test escalation hook for high-value settlements"""
        agent = BaseInsuranceAgent("test_agent")
        
        # Mock tool and args for high-value settlement
        mock_tool = Mock()
        mock_tool.name = "create_settlement_offer"
        args = {"amount": 30000}
        
        result = agent._before_tool_call_hook(mock_tool, args, Mock(), 1)
        
        assert result is not None
        assert "25,000 threshold" in result.user_guidance
    
    def test_before_tool_call_hook_emotional_distress(self, mock_environment):
        """Test escalation hook for emotional distress"""
        agent = BaseInsuranceAgent("test_agent")
        
        mock_tool = Mock()
        mock_tool.name = "process_claim"
        args = {"customer_emotion": "extreme_distress"}
        
        result = agent._before_tool_call_hook(mock_tool, args, Mock(), 1)
        
        assert result is not None
        assert "extreme distress" in result.user_guidance
    
    def test_before_tool_call_hook_normal_case(self, mock_environment):
        """Test no escalation for normal cases"""
        agent = BaseInsuranceAgent("test_agent")
        
        mock_tool = Mock()
        mock_tool.name = "process_claim"
        args = {"amount": 5000, "customer_emotion": "neutral"}
        
        result = agent._before_tool_call_hook(mock_tool, args, Mock(), 1)
        
        assert result is None
    
    def test_audit_logging(self, mock_environment):
        """Test audit trail logging"""
        agent = BaseInsuranceAgent("test_agent")
        
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        args = {"test": "value"}
        result = {"test_result": "success"}
        mock_plan_run = Mock()
        mock_plan_run.id = "test_run_123"
        
        # This should not raise an exception
        agent._after_tool_call_hook(mock_tool, args, result, mock_plan_run, 1)
        
        # Audit logging is tested indirectly through no exceptions
        assert True