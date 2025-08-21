import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables first
load_dotenv()

async def test_emotion_awareness(audio_data):
    """Test emotion-aware claim processing"""
    
    print("🔑 Using real Portia SDK...")
    
    try:
        # Try to import and use real agent
        from src.agents.claim_negotiator import ClaimNegotiationAgent

        # Initialize agent with explicit configuration to avoid import issues
        print("🔧 Initializing emotion-aware agent with explicit configuration...")
        agent = ClaimNegotiationAgent("emotion_test_agent")
        print("✅ Agent initialized successfully")

        # Test scenarios with different emotional states
        test_scenarios = [
            {
                "audio_data": audio_data,
                "claim_context": {
                    "claim_id": "CLM-ANGRY-001",
                    "policy_number": "POL-2024-001",
                    "claim_type": "auto_collision",
                    "estimated_amount": 20000,
                    "customer_id": "CUST-001",
                    "incident_date": "2024-01-15",
                    "reported_date": "2024-01-16",
                    "description": "Customer was involved in a collision with another vehicle"
                }
            },
            {
                "audio_data": audio_data,
                "claim_context": {
                    "claim_id": "CLM-SAD-001", 
                    "policy_number": "POL-2024-002",
                    "claim_type": "auto_total_loss",
                    "estimated_amount": 50000,
                    "customer_id": "CUST-002",
                    "incident_date": "2024-01-20",
                    "reported_date": "2024-01-21",
                    "description": "Customer's vehicle was totaled in an accident"
                }
            }
        ]
        
        print("📋 Processing test claims with emotion analysis...")
        
        results = []
        for scenario in test_scenarios:
            result = await agent.negotiate_claim_full_pipeline(
                scenario["audio_data"],
                scenario["claim_context"]
            )
            results.append(result)
            # Handle both dictionary and object results
            if hasattr(result, 'get'):
                print(f"Processed {scenario['claim_context']['claim_id']}: {result.get('status', 'unknown')}")
            elif hasattr(result, 'status'):
                print(f"Processed {scenario['claim_context']['claim_id']}: {result.status}")
            else:
                print(f"Processed {scenario['claim_context']['claim_id']}: {type(result)}")
        
        print("\n=== Voice Integration Test Results ===")
        for result in results:
            # Handle both dictionary and object results
            if hasattr(result, 'get'):
                print(f"Claim ID: {result.get('claim_id', 'unknown')}")
                print(f"  Status: {result.get('status', 'unknown')}")
                print(f"  Plan Run ID: {result.get('plan_run_id', 'unknown')}")
            elif hasattr(result, 'claim_id'):
                print(f"Claim ID: {result.claim_id}")
                print(f"  Status: {result.status}")
                print(f"  Plan Run ID: {getattr(result, 'plan_run_id', 'unknown')}")
            else:
                print(f"Claim result: {result}")
            
        return results
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        # Print more detailed error information
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

async def test_microphone_recording():
    """Test microphone recording functionality"""
    print("🎙️ Testing Microphone Recording...")
    
    try:
        from src.voice.microphone_recorder import record_customer_voice, record_voice_to_file
        
        # Test recording to base64 string
        print("🎤 Recording 3 seconds of audio...")
        audio_data = record_customer_voice(record_seconds=3)
        
        if audio_data:
            print(f"✅ Recorded audio data (first 50 chars): {audio_data[:50]}...")
            print(f"   Data length: {len(audio_data)} characters")
        else:
            print("❌ Failed to record audio")
            return False
            
        # Test recording to file
        print("\n💾 Recording audio to file...")
        success = record_voice_to_file("test_claim_recording.wav", record_seconds=3)
        
        if success:
            print("✅ Audio recorded to test_claim_recording.wav")
        else:
            print("❌ Failed to record audio to file")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🧪 Voice-Driven Insurance Claim Negotiator - Voice Integration Tests")
    print("=" * 70)
    
    # Test microphone recording
    mic_success = await test_microphone_recording()
    
    if mic_success:
        print("\n✅ Microphone tests passed")
    else:
        print("\n❌ Microphone tests failed")
        print("💡 Make sure you have a working microphone and granted permissions")
        return
    
    # Get audio data for emotion analysis
    from src.voice.microphone_recorder import record_customer_voice
    print("\n🎤 Recording audio for emotion analysis...")
    audio_data = record_customer_voice(record_seconds=3)
    
    if not audio_data:
        print("❌ Failed to record audio for emotion analysis")
        return
    
    print(f"✅ Recorded audio data for emotion analysis (length: {len(audio_data)} characters)")
    
    # Test emotion awareness
    print("\n" + "=" * 70)
    emotion_results = await test_emotion_awareness(audio_data)
    
    print("\n" + "=" * 70)
    print("🏁 Voice Integration Testing Complete")
    
    return {
        "microphone_test": mic_success,
        "emotion_test": emotion_results
    }

if __name__ == "__main__":
    result = asyncio.run(main())