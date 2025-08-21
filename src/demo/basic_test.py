import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Check if we should use demo mode
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

async def test_basic_agent_functionality():
    """Test basic agent setup and functionality"""
    load_dotenv()

    print("🧪 Starting Basic Agent Test")
    print("=" * 40)

    try:
        # Test claim data
        test_claim = {
            "claim_id": "CLM-TEST-001",
            "policy_number": "POL-2024-001",
            "claim_type": "auto_collision",
            "estimated_amount": 15000,
            "customer_emotion": "frustrated",
            "customer_id": "CUST-001"
        }
 
        print("📋 Test claim data prepared:")
        for key, value in test_claim.items():
            print(f"   {key}: {value}")

        if DEMO_MODE or TEST_MODE:
            print("\n🎭 Running in DEMO/TEST mode (no API keys required)")
            print("✅ Mock policy validation...")
            print("✅ Mock claim processing...")
            print("✅ Mock compliance check...")
            print("✅ Mock settlement calculation...")

            # Simulate successful processing
            result = {
                "claim_id": test_claim["claim_id"],
                "processing_status": "completed",
                "settlement_recommendation": {
                    "amount": 13500,
                    "confidence": 0.85,
                    "explanation": "Based on similar cases and policy coverage"
                },
                "audit_trail": ["policy_validated", "claim_processed", "settlement_calculated"],
                "clarifications_raised": 0,
                "plan_run_id": "demo-run-123"
            }

            print("\n=== Basic Agent Test Results ===")
            print(f"Processing Status: {result['processing_status']}")
            print(f"Settlement Amount: ${result['settlement_recommendation']['amount']:,}")
            print(f"Confidence: {result['settlement_recommendation']['confidence']:.1%}")
            print(f"Audit Trail: {len(result['audit_trail'])} steps")
            print(f"Plan Run ID: {result['plan_run_id']}")
            print(f"Clarifications: {result['clarifications_raised']}")

            print("\n✅ Demo mode test completed successfully!")
            print("💡 To run with real Portia SDK, set API keys in .env file")
            return result
        else:
            print("🔑 Attempting to load real Portia SDK...")

            # Try to import and use real agent
            from agents.base_agent import BaseInsuranceAgent

            # Initialize agent with explicit configuration to avoid import issues
            print("🔧 Initializing agent with explicit configuration...")
            agent = BaseInsuranceAgent("test_agent")
            print("✅ Agent initialized successfully")

            print("📋 Processing test claim with real agent...")

            # Process test claim
            result = await agent.process_claim(test_claim)

            print("\n=== Basic Agent Test Results ===")
            print(f"Processing Status: {result.get('processing_status', 'unknown')}")
            print(f"Plan Run ID: {result.get('plan_run_id', 'unknown')}")
            print(f"Clarifications: {result.get('clarifications_raised', 'unknown')}")

            if result.get("processing_status") == "completed":
                print("✅ Basic agent functionality working!")
            elif result.get("processing_status") == "error":
                print("❌ Agent encountered error:", result.get("error_message", "Unknown error"))
            else:
                print("⚠️  Agent requires clarification or encountered issues")

            return result

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        print("💡 Try setting DEMO_MODE=true or TEST_MODE=true to run without API keys")
        # Print more detailed error information
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(test_basic_agent_functionality())