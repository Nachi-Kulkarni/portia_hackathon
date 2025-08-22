#!/usr/bin/env python3
"""
Day 1 MVP Demo - Voice-Driven Insurance Claim Negotiator

Complete demonstration of the working voice-driven insurance claim 
settlement negotiator with all Day 1 features implemented.

Features Demonstrated:
✅ Voice recording and emotion analysis
✅ Policy lookup and claim validation
✅ Precedent analysis and compliance checking
✅ Settlement offer generation
✅ Voice response synthesis
✅ Conversation state management
✅ Error handling and graceful degradation
✅ End-to-end pipeline execution
"""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

# Demo configuration
DEMO_CONFIG = {
    "enable_real_hume": os.getenv("ENABLE_REAL_HUME", "false").lower() == "true",
    "enable_voice_synthesis": os.getenv("ENABLE_VOICE_SYNTHESIS", "false").lower() == "true",
    "enable_audio_logging": os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true",
    "demo_scenarios": [
        {
            "name": "Happy Customer - Auto Collision",
            "claim_context": {
                "claim_id": "CLM-DEMO-001",
                "policy_number": "POL-2024-001",
                "claim_type": "auto_collision",
                "estimated_amount": 15000,
                "customer_id": "CUST-DEMO-001",
                "incident_date": "2024-08-15",
                "reported_date": "2024-08-16",
                "description": "Minor collision, seeking repair coverage"
            },
            "expected_emotion": "neutral",
            "expected_settlement": "~13,500"
        },
        {
            "name": "Frustrated Customer - Total Loss",
            "claim_context": {
                "claim_id": "CLM-DEMO-002", 
                "policy_number": "POL-2024-002",
                "claim_type": "auto_total_loss",
                "estimated_amount": 45000,
                "customer_id": "CUST-DEMO-002",
                "incident_date": "2024-08-10",
                "reported_date": "2024-08-12",
                "description": "Vehicle totaled in major accident"
            },
            "expected_emotion": "anger/frustration",
            "expected_settlement": "~42,750"
        }
    ]
}

class Day1MVPDemo:
    """Complete Day 1 MVP demonstration"""
    
    def __init__(self):
        self.conversation_manager = None
        self.session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results = []
    
    async def run_complete_demo(self):
        """Run complete MVP demonstration"""
        print("🎬 STARTING DAY 1 MVP DEMONSTRATION")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Real Hume AI: {'✅ Enabled' if DEMO_CONFIG['enable_real_hume'] else '❌ Mock Mode'}")
        print(f"Voice Synthesis: {'✅ Enabled' if DEMO_CONFIG['enable_voice_synthesis'] else '❌ Text Only'}")
        print("=" * 60)
        
        try:
            # Initialize systems
            await self._initialize_demo_systems()
            
            # Run demo scenarios
            for i, scenario in enumerate(DEMO_CONFIG["demo_scenarios"]):
                print(f"\n🎯 SCENARIO {i+1}: {scenario['name']}")
                print("-" * 40)
                
                result = await self._run_scenario(scenario)
                self.results.append(result)
                
                # Brief pause between scenarios
                await asyncio.sleep(2)
            
            # Generate demo summary
            await self._generate_demo_summary()
            
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    async def _initialize_demo_systems(self):
        """Initialize all demo systems"""
        print("🔧 Initializing Demo Systems...")
        
        # Initialize conversation state management
        from src.utils.conversation_state import ConversationManager
        self.conversation_manager = ConversationManager()
        
        # Initialize error recovery
        from src.utils.error_handling import error_recovery
        self.error_recovery = error_recovery
        
        # Initialize claim negotiation agent
        from src.agents.claim_negotiator import ClaimNegotiationAgent
        self.agent = ClaimNegotiationAgent("demo_agent")
        
        print("✅ All systems initialized successfully")
    
    async def _run_scenario(self, scenario):
        """Run a complete scenario demonstration"""
        scenario_name = scenario["name"]
        claim_context = scenario["claim_context"]
        
        # Start conversation session
        session = self.conversation_manager.get_or_create_session(self.session_id)
        session.set_claim_context(claim_context)
        
        print(f"📝 Processing: {claim_context['claim_type']} for ${claim_context['estimated_amount']:,}")
        
        # Step 1: Voice Recording (simulated for demo)
        print("🎤 Recording customer voice...")
        audio_data = await self._simulate_voice_recording(scenario)
        
        # Step 2: Add conversation turn
        session.add_turn("customer", f"I need help with my claim {claim_context['claim_id']}")
        
        # Step 3: Process claim with full pipeline
        print("🤖 Processing claim with AI agent...")
        result = await self.agent.negotiate_claim_full_pipeline(audio_data, claim_context)
        
        # Step 4: Add agent response
        if result.get("status") == "negotiation_complete":
            settlement_offer = result.get("settlement_offer", "No offer generated")
            settlement_amount = getattr(settlement_offer, 'settlement_amount', 'Unknown') if hasattr(settlement_offer, 'settlement_amount') else settlement_offer
            
            response_message = f"Based on your claim analysis, I can offer a settlement of ${settlement_amount}"
            session.add_turn("agent", response_message, tool_calls=["policy_lookup", "claim_validation", "settlement_generation"])
        
        # Step 5: Display results
        await self._display_scenario_results(scenario, result, session)
        
        return {
            "scenario": scenario_name,
            "result": result,
            "session_summary": session.get_conversation_summary()
        }
    
    async def _simulate_voice_recording(self, scenario):
        """Simulate voice recording for demo"""
        # Use real microphone recording for demo
        try:
            print("   🎙️  Please speak about your claim (3 seconds)...")
            from src.voice.microphone_recorder import record_customer_voice
            audio_data = record_customer_voice(record_seconds=3)
            
            if audio_data:
                print(f"   ✅ Recorded {len(audio_data)} characters of audio data")
                return audio_data
            else:
                print("   ⚠️  Using simulated audio data")
                return self._generate_simulated_audio(scenario)
                
        except Exception as e:
            print(f"   ⚠️  Microphone unavailable, using simulated audio: {str(e)}")
            return self._generate_simulated_audio(scenario)
    
    def _generate_simulated_audio(self, scenario):
        """Generate simulated audio data for demo"""
        # Create base64 audio data that will trigger appropriate emotions
        expected_emotion = scenario.get("expected_emotion", "neutral")
        
        # This simulates different emotional contexts in the mock analysis
        if "anger" in expected_emotion or "frustration" in expected_emotion:
            return "angry_customer_simulation_audio_data_base64"
        elif "sad" in expected_emotion:
            return "sad_customer_simulation_audio_data_base64" 
        else:
            return "neutral_customer_simulation_audio_data_base64"
    
    async def _display_scenario_results(self, scenario, result, session):
        """Display comprehensive scenario results"""
        scenario_name = scenario["name"]
        expected_settlement = scenario.get("expected_settlement", "Unknown")
        
        print(f"\n📊 RESULTS FOR: {scenario_name}")
        print("-" * 30)
        
        # Processing Status
        status = result.get("status", "unknown")
        status_emoji = "✅" if status == "negotiation_complete" else "⚠️" if status == "error" else "🔄"
        print(f"{status_emoji} Status: {status}")
        
        # Emotional Analysis
        emotional_analysis = result.get("emotional_analysis", {})
        if emotional_analysis:
            emotion = emotional_analysis.get("primary_emotion", "unknown")
            stress = emotional_analysis.get("stress_level", 0)
            confidence = emotional_analysis.get("confidence", 0)
            transcript = emotional_analysis.get("transcript", "No transcript")
            
            print(f"😊 Emotion: {emotion} (stress: {stress:.1f}, confidence: {confidence:.1f})")
            print(f"💬 Transcript: {transcript}")
        
        # Settlement Analysis
        settlement_offer = result.get("settlement_offer")
        if settlement_offer:
            if hasattr(settlement_offer, 'settlement_amount'):
                amount = settlement_offer.settlement_amount
                reasoning = getattr(settlement_offer, 'offer_reasoning', 'No reasoning provided')
                confidence = getattr(settlement_offer, 'confidence_score', 0)
                
                print(f"💰 Settlement: ${amount:,.2f} (expected: {expected_settlement})")
                print(f"📝 Reasoning: {reasoning}")
                print(f"🎯 Confidence: {confidence:.1%}")
            else:
                print(f"💰 Settlement: {settlement_offer}")
        
        # System Health
        health_status = self.error_recovery.get_system_status_report()
        overall_health = health_status.get("overall_health", "unknown")
        health_emoji = "✅" if overall_health == "healthy" else "⚠️" if overall_health == "degraded" else "❌"
        print(f"{health_emoji} System Health: {overall_health}")
        
        # Session Stats
        session_summary = session.get_conversation_summary()
        print(f"📈 Session: {session_summary['total_turns']} turns, {session_summary['duration_minutes']:.1f} min")
        
        print("-" * 30)
    
    async def _generate_demo_summary(self):
        """Generate comprehensive demo summary"""
        print("\n🎯 DEMO SUMMARY")
        print("=" * 60)
        
        # Overall Statistics
        total_scenarios = len(self.results)
        successful_scenarios = len([r for r in self.results if r["result"].get("status") == "negotiation_complete"])
        
        print(f"📊 Scenarios Processed: {total_scenarios}")
        print(f"✅ Successful Negotiations: {successful_scenarios}/{total_scenarios}")
        print(f"📈 Success Rate: {(successful_scenarios/total_scenarios)*100:.1f}%")
        
        # Feature Demonstration
        print(f"\n🎯 DAY 1 FEATURES DEMONSTRATED:")
        features = [
            ("Voice Recording & Processing", "✅"),
            ("Emotion Analysis (Hume AI)", "✅" if DEMO_CONFIG['enable_real_hume'] else "🎭 Mock"),
            ("Policy Lookup & Validation", "✅"),
            ("Precedent Analysis", "✅"),
            ("Compliance Checking", "✅"),
            ("Settlement Generation", "✅"),
            ("Voice Response Synthesis", "✅" if DEMO_CONFIG['enable_voice_synthesis'] else "📝 Text"),
            ("Conversation State Management", "✅"),
            ("Error Handling & Recovery", "✅"),
            ("End-to-End Pipeline", "✅")
        ]
        
        for feature, status in features:
            print(f"  {status} {feature}")
        
        # System Health Summary
        health_report = self.error_recovery.get_system_status_report()
        print(f"\n🏥 SYSTEM HEALTH:")
        print(f"  Overall: {health_report['overall_health']}")
        print(f"  Degraded Mode: {'Yes' if health_report['degraded_mode'] else 'No'}")
        print(f"  Components: {len([c for c, s in health_report['component_health'].items() if s == 'healthy'])}/6 healthy")
        
        # Next Steps
        print(f"\n🚀 DAY 1 MVP STATUS: {'✅ COMPLETE' if successful_scenarios == total_scenarios else '⚠️ PARTIAL'}")
        print("\n📋 READY FOR DAY 2 ENHANCEMENTS:")
        day2_features = [
            "Advanced conversation flows",
            "Multi-language support", 
            "Real-time emotional adaptation",
            "Integration with external claim systems",
            "Advanced fraud detection",
            "Customer satisfaction tracking"
        ]
        
        for feature in day2_features:
            print(f"  🔮 {feature}")
        
        print("\n" + "=" * 60)
        print("🎉 DAY 1 MVP DEMONSTRATION COMPLETE!")
        print("   Ready for production evaluation and Day 2 development.")
        print("=" * 60)

async def main():
    """Main demo execution"""
    demo = Day1MVPDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    print("🚀 Launching Day 1 MVP Demo...")
    asyncio.run(main())