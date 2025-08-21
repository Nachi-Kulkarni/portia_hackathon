import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.base_agent import BaseInsuranceAgent

async def test_basic_agent_functionality():
    """Test basic agent setup and functionality"""
    load_dotenv()
    
    print("🧪 Starting Basic Agent Test")
    print("=" * 40)
    
    try:
        # Initialize agent
        agent = BaseInsuranceAgent("test_agent")
        print("✅ Agent initialized successfully")
        
        # Test claim data
        test_claim = {
            "claim_id": "CLM-TEST-001",
            "policy_number": "POL-2024-001",
            "claim_type": "auto_collision", 
            "estimated_amount": 15000,
            "customer_emotion": "frustrated",
            "customer_id": "CUST-001"
        }
        
        print("📋 Processing test claim...")
        
        # Process test claim
        result = await agent.process_claim(test_claim)
        
        print("\n=== Basic Agent Test Results ===")
        print(f"Processing Status: {result['processing_status']}")
        print(f"Plan Run ID: {result['plan_run_id']}")
        print(f"Clarifications: {result['clarifications_raised']}")
        
        if result["processing_status"] == "completed":
            print("✅ Basic agent functionality working!")
        elif result["processing_status"] == "error":
            print("❌ Agent encountered error:", result.get("error_message", "Unknown error"))
        else:
            print("⚠️  Agent requires clarification or encountered issues")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(test_basic_agent_functionality())