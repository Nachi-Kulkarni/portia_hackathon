import asyncio
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.claim_negotiator import ClaimNegotiationAgent

async def test_complete_pipeline():
    """Test the complete claim negotiation pipeline"""
    
    print("🚀 Starting Complete Pipeline Test")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Initialize the complete agent
    agent = ClaimNegotiationAgent("full_pipeline_agent")
    print("✅ Agent initialized with complete tool suite")
    
    # Test scenarios covering different complexity levels
    test_scenarios = [
        {
            "name": "Simple Auto Claim - Calm Customer",
            "audio_data": "Hi, I'd like to file a claim for my car accident",
            "claim_data": {
                "claim_id": "CLM-SIMPLE-001",
                "policy_number": "POL-2024-001",
                "claim_type": "auto_collision",
                "estimated_amount": 8500,
                "customer_id": "CUST-001",
                "incident_date": "2024-01-15",
                "state": "CA"
            }
        },
        {
            "name": "High-Value Claim - Emotional Customer",
            "audio_data": "angry I can't believe this happened my car is totaled",
            "claim_data": {
                "claim_id": "CLM-COMPLEX-001", 
                "policy_number": "POL-2024-002",
                "claim_type": "auto_total_loss",
                "estimated_amount": 75000,
                "customer_id": "CUST-002",
                "incident_date": "2024-01-20",
                "state": "NY"
            }
        },
        {
            "name": "Potential Fraud Case",
            "audio_data": "neutral I need to file a claim",
            "claim_data": {
                "claim_id": "CLM-FRAUD-001",
                "policy_number": "POL-2024-003", 
                "claim_type": "auto_collision",
                "estimated_amount": 45000,
                "customer_id": "CUST-003",
                "incident_date": "2024-01-01",  # Old incident
                "state": "CA",
                "supporting_documents": ["police_report"]  # Minimal docs
            }
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🧪 Test {i}: {scenario['name']}")
        print("-" * 40)
        
        start_time = datetime.now()
        
        try:
            # Run complete pipeline
            result = await agent.negotiate_claim_full_pipeline(
                scenario["audio_data"],
                scenario["claim_data"]
            )
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Display results
            print(f"Status: {result['status']}")
            print(f"Processing Time: {processing_time:.2f} seconds")
            
            if result['status'] == 'negotiation_complete':
                settlement = result.get('settlement_offer', {})
                print(f"Settlement Amount: ${settlement.get('settlement_amount', 0):,.2f}" if isinstance(settlement, dict) else "Settlement details available")
                print(f"Compliance Status: {result.get('compliance_status', 'unknown')}")
                print(f"Emotional Context: {result.get('emotional_analysis', {}).get('primary_emotion', 'unknown')}")
            elif result['status'] == 'requires_clarification':
                print(f"Clarifications Needed: {result['clarifications_needed']}")
                print(f"Pending Approvals: {result['pending_approvals']}")
            else:
                print(f"Error: {result.get('error_message', 'Unknown error')}")
            
            print(f"Plan Run ID: {result.get('plan_run_id', 'N/A')}")
            
            results.append({
                "scenario": scenario["name"],
                "result": result,
                "processing_time": processing_time
            })
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            results.append({
                "scenario": scenario["name"],
                "result": {"status": "test_error", "error": str(e)},
                "processing_time": 0
            })
    
    # Generate summary report
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    
    successful_negotiations = sum(1 for r in results if r["result"]["status"] == "negotiation_complete")
    requiring_clarification = sum(1 for r in results if r["result"]["status"] == "requires_clarification")
    errors = sum(1 for r in results if r["result"]["status"] in ["error", "test_error"])
    
    print(f"✅ Successful Negotiations: {successful_negotiations}/{len(results)}")
    print(f"⚠️  Requiring Clarification: {requiring_clarification}/{len(results)}")
    print(f"❌ Errors: {errors}/{len(results)}")
    
    if results:
        avg_processing_time = sum(r["processing_time"] for r in results) / len(results)
        print(f"⏱️  Average Processing Time: {avg_processing_time:.2f} seconds")
    
    # Save detailed results
    results_file = "pipeline_test_results.json"
    try:
        with open(results_file, "w") as f:
            json.dump({
                "test_timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_tests": len(results),
                    "successful": successful_negotiations,
                    "clarification_needed": requiring_clarification,  
                    "errors": errors,
                    "average_processing_time": avg_processing_time if results else 0
                },
                "detailed_results": results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️  Could not save results: {str(e)}")
    
    return results

# Validation and fallback testing
async def test_error_handling():
    """Test error handling and fallback mechanisms"""
    
    print("\n🛡️  Testing Error Handling & Fallbacks")
    print("=" * 50)
    
    agent = ClaimNegotiationAgent("error_test_agent")
    
    # Test with invalid policy number
    print("Testing invalid policy number...")
    invalid_policy_result = await agent.negotiate_claim_full_pipeline(
        "test audio",
        {
            "claim_id": "CLM-ERROR-001",
            "policy_number": "INVALID-POLICY",
            "claim_type": "auto_collision",
            "estimated_amount": 10000
        }
    )
    
    print(f"Invalid Policy Test: {invalid_policy_result['status']}")
    
    # Test with missing required data
    print("Testing missing data...")
    missing_data_result = await agent.negotiate_claim_full_pipeline(
        "",  # Empty audio
        {
            "claim_id": "CLM-ERROR-002"
            # Missing required fields
        }
    )
    
    print(f"Missing Data Test: {missing_data_result['status']}")
    
    return [invalid_policy_result, missing_data_result]

if __name__ == "__main__":
    # Run comprehensive tests
    print("🏁 Starting Comprehensive Day 1 Testing Suite")
    print("=" * 60)
    
    # Test complete pipeline
    pipeline_results = asyncio.run(test_complete_pipeline())
    
    # Test error handling
    error_results = asyncio.run(test_error_handling())
    
    print("\n🎉 Day 1 Testing Complete!")
    print("Ready for Day 2 advanced features development.")