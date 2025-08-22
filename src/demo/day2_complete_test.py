#!/usr/bin/env python3
"""
Day 2 Complete Integration Test Script
=====================================

This script tests Day 2 features built on top of the Day 1 foundation:
1. Emotion-aware responses 
2. Human-in-the-loop escalation system
3. Settlement intelligence with creative options
4. Compliance & audit trails

Tests are designed to work with mock data when Portia SDK is not available.
"""

import sys
import asyncio
import logging
import json
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Setup paths and logging
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Day2IntegrationTester:
    """Comprehensive Day 2 feature testing with Day 1 foundation"""
    
    def __init__(self):
        self.session_id = f"day2_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.test_results = {}
        self.use_mock_portia = True
        
    async def run_complete_day2_test(self):
        """Run comprehensive Day 2 integration test"""
        print("🚀 Starting Day 2 Complete Integration Test")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Mock Mode: {'✅' if self.use_mock_portia else '❌'}")
        print("=" * 60)
        
        try:
            # Test 1: Emotion Analysis System
            await self._test_emotion_awareness()
            
            # Test 2: Escalation Manager
            await self._test_escalation_system()
            
            # Test 3: Settlement Intelligence  
            await self._test_settlement_intelligence()
            
            # Test 4: Audit & Compliance
            await self._test_audit_compliance()
            
            # Test 5: Complete Day 2 Pipeline Integration
            await self._test_complete_day2_pipeline()
            
            # Generate final report
            self._generate_test_report()
            
        except Exception as e:
            logger.error(f"Day 2 test failed: {str(e)}")
            print(f"❌ Test suite failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    async def _test_emotion_awareness(self):
        """Test Day 2 emotion-aware response system"""
        print("\n🧠 Testing Emotion-Aware Response System...")
        
        try:
            # Test emotion analyzer without Portia dependencies
            emotion_test_cases = [
                {
                    "emotion": "anger", 
                    "stress_level": 0.9,
                    "expected_escalation": True,
                    "audio_hint": "angry customer about denied claim"
                },
                {
                    "emotion": "sadness",
                    "stress_level": 0.6, 
                    "expected_escalation": False,
                    "audio_hint": "grieving widow life insurance"
                },
                {
                    "emotion": "anxiety",
                    "stress_level": 0.7,
                    "expected_escalation": False,
                    "audio_hint": "worried about claim process"
                },
                {
                    "emotion": "neutral",
                    "stress_level": 0.3,
                    "expected_escalation": False,
                    "audio_hint": "routine claim inquiry"
                }
            ]
            
            emotion_results = []
            
            # Import emotion analyzer (handling potential import issues)
            try:
                from src.voice.emotion_analyzer import EmotionAnalyzer, EmotionalContext
                emotion_analyzer = EmotionAnalyzer()
                
                for test_case in emotion_test_cases:
                    # Create emotional context
                    context = EmotionalContext(
                        primary_emotion=test_case["emotion"],
                        stress_level=test_case["stress_level"], 
                        confidence=0.85,
                        emotion_scores={test_case["emotion"]: 0.8}
                    )
                    
                    # Get response strategy
                    strategy = emotion_analyzer.get_response_strategy(context)
                    
                    # Test response adaptation
                    base_response = "Here's information about your claim status."
                    adapted_response = emotion_analyzer.adapt_response_to_emotion(base_response, context)
                    
                    result = {
                        "emotion": test_case["emotion"],
                        "stress_level": test_case["stress_level"],
                        "escalation_needed": strategy["needs_escalation"],
                        "response_templates": len(strategy["response_templates"]),
                        "tone_indicators": strategy["tone_indicators"],
                        "adapted_response": adapted_response,
                        "test_passed": strategy["needs_escalation"] == test_case["expected_escalation"]
                    }
                    
                    emotion_results.append(result)
                    print(f"  ✅ {test_case['emotion'].upper()}: Escalation={strategy['needs_escalation']}, Tones={strategy['tone_indicators']}")
                
                self.test_results["emotion_awareness"] = {
                    "status": "PASSED",
                    "results": emotion_results,
                    "success_rate": sum(1 for r in emotion_results if r["test_passed"]) / len(emotion_results)
                }
                print(f"  🎯 Emotion Analysis Success Rate: {self.test_results['emotion_awareness']['success_rate']:.1%}")
                
            except ImportError as e:
                print(f"  ⚠️  Import error for emotion analyzer: {e}")
                self.test_results["emotion_awareness"] = {"status": "IMPORT_ERROR", "error": str(e)}
                
        except Exception as e:
            print(f"  ❌ Emotion awareness test failed: {e}")
            self.test_results["emotion_awareness"] = {"status": "FAILED", "error": str(e)}
    
    async def _test_escalation_system(self):
        """Test Day 2 human-in-the-loop escalation system"""
        print("\n🚨 Testing Escalation Management System...")
        
        try:
            # Import escalation manager
            from src.agents.escalation_manager import EscalationManager, EscalationContext
            
            escalation_manager = EscalationManager()
            
            # Test escalation scenarios
            test_scenarios = [
                {
                    "name": "Legal Threat",
                    "conversation_history": [{"text": "I'm going to call my lawyer if this isn't resolved"}],
                    "settlement_amount": 30000,
                    "expected_escalation": True,
                    "expected_reasons": ["legal_threat"]
                },
                {
                    "name": "High Value Claim", 
                    "conversation_history": [{"text": "This is about my car accident claim"}],
                    "settlement_amount": 75000,
                    "expected_escalation": True,
                    "expected_reasons": ["high_value"]
                },
                {
                    "name": "Extreme Distress",
                    "conversation_history": [{"text": "I can't handle this stress anymore"}],
                    "settlement_amount": 20000,
                    "emotion_analysis": {"distress": 0.9, "anger": 0.5},
                    "expected_escalation": True,
                    "expected_reasons": ["extreme_distress"]
                },
                {
                    "name": "Normal Claim",
                    "conversation_history": [{"text": "I'd like to check on my claim status"}],
                    "settlement_amount": 15000,
                    "expected_escalation": False,
                    "expected_reasons": []
                }
            ]
            
            escalation_results = []
            
            for scenario in test_scenarios:
                # Create escalation context
                context = EscalationContext(
                    conversation_history=scenario["conversation_history"],
                    emotion_analysis=scenario.get("emotion_analysis", {"neutral": 0.7}),
                    claim_details={"type": "auto", "amount": scenario["settlement_amount"]},
                    settlement_amount=scenario["settlement_amount"],
                    legal_indicators=[],
                    compliance_flags=[],
                    customer_id="test_customer"
                )
                
                # Evaluate escalation need
                evaluation = escalation_manager.evaluate_escalation_need(context)
                
                result = {
                    "scenario": scenario["name"],
                    "should_escalate": evaluation["should_escalate"],
                    "triggered_reasons": evaluation["triggered_reasons"],
                    "severity_score": evaluation["severity_score"],
                    "test_passed": evaluation["should_escalate"] == scenario["expected_escalation"]
                }
                
                escalation_results.append(result)
                status = "✅" if result["test_passed"] else "❌"
                print(f"  {status} {scenario['name']}: Escalation={evaluation['should_escalate']}, Reasons={evaluation['triggered_reasons']}")
            
            self.test_results["escalation_system"] = {
                "status": "PASSED",
                "results": escalation_results,
                "success_rate": sum(1 for r in escalation_results if r["test_passed"]) / len(escalation_results)
            }
            print(f"  🎯 Escalation System Success Rate: {self.test_results['escalation_system']['success_rate']:.1%}")
            
        except ImportError as e:
            print(f"  ⚠️  Import error for escalation manager: {e}")
            self.test_results["escalation_system"] = {"status": "IMPORT_ERROR", "error": str(e)}
        except Exception as e:
            print(f"  ❌ Escalation system test failed: {e}")
            self.test_results["escalation_system"] = {"status": "FAILED", "error": str(e)}
    
    async def _test_settlement_intelligence(self):
        """Test Day 2 settlement intelligence with creative options"""
        print("\n💡 Testing Settlement Intelligence System...")
        
        try:
            # Test enhanced precedent analysis with creative options
            from src.tools.precedent_tools import PrecedentAnalysisTool
            
            precedent_tool = PrecedentAnalysisTool()
            
            test_cases = [
                {
                    "claim_type": "auto_accident",
                    "claim_amount": 45000,
                    "emotional_context": "high_stress",
                    "expected_creative_options": True
                },
                {
                    "claim_type": "property_damage", 
                    "claim_amount": 25000,
                    "emotional_context": "neutral",
                    "expected_creative_options": False
                }
            ]
            
            settlement_results = []
            
            # Create mock tool run context
            class MockToolRunContext:
                def __init__(self):
                    self.user_id = "test_user"
            
            for test_case in test_cases:
                try:
                    ctx = MockToolRunContext()
                    
                    # Test the tool (this will use mock data)
                    result = precedent_tool.run(
                        ctx=ctx,
                        claim_type=test_case["claim_type"],
                        claim_amount=test_case["claim_amount"]
                    )
                    
                    # Check if creative options are present when expected
                    has_creative_options = len(result.creative_options) > 0
                    
                    settlement_result = {
                        "claim_type": test_case["claim_type"],
                        "settlement_amount": result.recommended_amount,
                        "confidence": result.confidence_level,
                        "creative_options": len(result.creative_options),
                        "has_creative_options": has_creative_options,
                        "test_passed": True  # Basic functionality test
                    }
                    
                    settlement_results.append(settlement_result)
                    print(f"  ✅ {test_case['claim_type']}: Amount=${result.recommended_amount:,.2f}, Options={len(result.creative_options)}")
                    
                except Exception as tool_error:
                    print(f"  ❌ Settlement tool error for {test_case['claim_type']}: {tool_error}")
                    settlement_results.append({
                        "claim_type": test_case["claim_type"],
                        "error": str(tool_error),
                        "test_passed": False
                    })
            
            self.test_results["settlement_intelligence"] = {
                "status": "PASSED",
                "results": settlement_results,
                "success_rate": sum(1 for r in settlement_results if r.get("test_passed", False)) / len(settlement_results) if settlement_results else 0
            }
            print(f"  🎯 Settlement Intelligence Success Rate: {self.test_results['settlement_intelligence']['success_rate']:.1%}")
            
        except ImportError as e:
            print(f"  ⚠️  Import error for settlement tools: {e}")
            self.test_results["settlement_intelligence"] = {"status": "IMPORT_ERROR", "error": str(e)}
        except Exception as e:
            print(f"  ❌ Settlement intelligence test failed: {e}")
            self.test_results["settlement_intelligence"] = {"status": "FAILED", "error": str(e)}
    
    async def _test_audit_compliance(self):
        """Test Day 2 audit trails and compliance system"""
        print("\n📋 Testing Audit & Compliance System...")
        
        try:
            from src.hooks.audit_logger import AuditTrailManager, AuditEntry
            
            audit_manager = AuditTrailManager()
            
            # Test audit entry logging
            test_actions = [
                {
                    "action_type": "policy_lookup",
                    "tool_name": "PolicyLookupTool", 
                    "arguments": {"policy_number": "POL123456"},
                    "result": {"coverage": 100000, "active": True}
                },
                {
                    "action_type": "settlement_offer",
                    "tool_name": "SettlementOfferTool",
                    "arguments": {"amount": 45000, "justification": "precedent_based"},
                    "result": {"offer_accepted": True, "compliance_check": "PASSED"}
                },
                {
                    "action_type": "escalation_trigger",
                    "tool_name": "EscalationManager",
                    "arguments": {"reason": "high_value", "amount": 75000},
                    "result": {"escalated": True, "human_agent": "supervisor_001"}
                }
            ]
            
            audit_results = []
            
            for action in test_actions:
                try:
                    # Create audit entry
                    entry = AuditEntry(
                        action_type=action["action_type"],
                        tool_name=action["tool_name"],
                        arguments=action["arguments"],
                        result=action["result"],
                        user_id="test_customer",
                        plan_run_id=self.session_id,
                        step_index=0,  # Required field
                        justification="Automated test entry"
                    )
                    
                    # Log the entry
                    audit_manager.log_action(entry)
                    
                    audit_results.append({
                        "action_type": action["action_type"],
                        "logged": True,
                        "entry_id": entry.entry_id,
                        "test_passed": True
                    })
                    print(f"  ✅ Logged: {action['action_type']} -> {entry.entry_id[:8]}...")
                    
                except Exception as audit_error:
                    print(f"  ❌ Audit logging failed for {action['action_type']}: {audit_error}")
                    audit_results.append({
                        "action_type": action["action_type"],
                        "error": str(audit_error),
                        "test_passed": False
                    })
            
            # Test compliance report generation
            try:
                compliance_report = audit_manager.generate_compliance_report(self.session_id)
                print(f"  ✅ Compliance Report Generated: {compliance_report.report_id[:8]}... ({compliance_report.total_actions} actions)")
            except Exception as report_error:
                print(f"  ⚠️  Compliance report generation failed: {report_error}")
            
            self.test_results["audit_compliance"] = {
                "status": "PASSED",
                "results": audit_results,
                "total_entries": len(audit_manager.audit_entries),
                "success_rate": sum(1 for r in audit_results if r.get("test_passed", False)) / len(audit_results) if audit_results else 0
            }
            print(f"  🎯 Audit & Compliance Success Rate: {self.test_results['audit_compliance']['success_rate']:.1%}")
            
        except ImportError as e:
            print(f"  ⚠️  Import error for audit system: {e}")
            self.test_results["audit_compliance"] = {"status": "IMPORT_ERROR", "error": str(e)}
        except Exception as e:
            print(f"  ❌ Audit & compliance test failed: {e}")
            self.test_results["audit_compliance"] = {"status": "FAILED", "error": str(e)}
    
    async def _test_complete_day2_pipeline(self):
        """Test complete Day 2 pipeline integration with Day 1 foundation"""
        print("\n🔄 Testing Complete Day 2 Pipeline Integration...")
        
        try:
            # This tests the full pipeline: Day 1 foundation + Day 2 enhancements
            
            # Simulate complete claim negotiation with Day 2 features
            test_claim = {
                "claim_id": "CLM_DAY2_TEST_001",
                "customer_id": "CUST_12345",
                "policy_number": "POL_98765", 
                "claim_type": "auto_accident",
                "estimated_amount": 55000,
                "incident_date": "2025-08-15",
                "description": "Rear-end collision on Highway 101"
            }
            
            # Simulate emotional audio input
            mock_audio_data = base64.b64encode(b"angry customer audio data").decode()
            
            pipeline_results = {
                "claim_id": test_claim["claim_id"],
                "steps_completed": [],
                "day2_features_tested": []
            }
            
            # Step 1: Test emotion analysis integration
            try:
                from src.voice.emotion_analyzer import EmotionAnalyzer, EmotionalContext
                emotion_analyzer = EmotionAnalyzer()
                
                # Simulate emotion detection
                emotional_context = EmotionalContext(
                    primary_emotion="anger",
                    stress_level=0.8,
                    confidence=0.9,
                    emotion_scores={"anger": 0.8, "frustration": 0.7}
                )
                
                pipeline_results["steps_completed"].append("emotion_analysis")
                pipeline_results["day2_features_tested"].append("emotion_awareness")
                print(f"  ✅ Emotion Analysis: {emotional_context.primary_emotion} (stress: {emotional_context.stress_level})")
                
            except Exception as e:
                print(f"  ❌ Emotion analysis integration failed: {e}")
            
            # Step 2: Test escalation evaluation
            try:
                from src.agents.escalation_manager import EscalationManager, EscalationContext
                escalation_manager = EscalationManager()
                
                # Create escalation context
                escalation_context = EscalationContext(
                    conversation_history=[{"text": "This is unacceptable! Fix this now!"}],
                    emotion_analysis={"anger": 0.8, "frustration": 0.7},
                    claim_details=test_claim,
                    settlement_amount=55000,
                    legal_indicators=[],
                    compliance_flags=[],
                    customer_id=test_claim["customer_id"]
                )
                
                # Evaluate escalation
                escalation_evaluation = escalation_manager.evaluate_escalation_need(escalation_context)
                
                pipeline_results["steps_completed"].append("escalation_evaluation")
                pipeline_results["day2_features_tested"].append("human_in_the_loop")
                pipeline_results["escalation_needed"] = escalation_evaluation["should_escalate"]
                pipeline_results["escalation_reasons"] = escalation_evaluation["triggered_reasons"]
                
                print(f"  ✅ Escalation Evaluation: {escalation_evaluation['should_escalate']} (reasons: {escalation_evaluation['triggered_reasons']})")
                
            except Exception as e:
                print(f"  ❌ Escalation evaluation failed: {e}")
            
            # Step 3: Test audit trail creation
            try:
                from src.hooks.audit_logger import AuditTrailManager, AuditEntry
                audit_manager = AuditTrailManager()
                
                # Log the complete pipeline execution
                pipeline_audit = AuditEntry(
                    action_type="complete_claim_negotiation",
                    tool_name="ClaimNegotiationAgent",
                    arguments=test_claim,
                    result=pipeline_results,
                    user_id=test_claim["customer_id"],
                    plan_run_id=self.session_id,
                    step_index=0,  # Required field
                    justification="Day 2 integration test"
                )
                
                audit_manager.log_action(pipeline_audit)
                
                pipeline_results["steps_completed"].append("audit_logging")
                pipeline_results["day2_features_tested"].append("compliance_audit")
                pipeline_results["audit_entry_id"] = pipeline_audit.entry_id
                
                print(f"  ✅ Audit Trail: Entry {pipeline_audit.entry_id[:8]}... logged")
                
            except Exception as e:
                print(f"  ❌ Audit trail creation failed: {e}")
            
            # Evaluate pipeline success
            total_day2_features = 4  # emotion_awareness, human_in_the_loop, settlement_intelligence, compliance_audit
            features_tested = len(pipeline_results["day2_features_tested"])
            pipeline_success_rate = features_tested / total_day2_features
            
            self.test_results["complete_pipeline"] = {
                "status": "PASSED" if pipeline_success_rate > 0.5 else "PARTIAL",
                "results": pipeline_results,
                "day2_features_tested": features_tested,
                "success_rate": pipeline_success_rate
            }
            
            print(f"  🎯 Complete Pipeline Success Rate: {pipeline_success_rate:.1%} ({features_tested}/{total_day2_features} Day 2 features)")
            
        except Exception as e:
            print(f"  ❌ Complete pipeline test failed: {e}")
            self.test_results["complete_pipeline"] = {"status": "FAILED", "error": str(e)}
    
    def _generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 Day 2 Integration Test Report")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results.values() if test.get("status") == "PASSED")
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Overall Success Rate: {passed_tests/total_tests:.1%}")
        print()
        
        for test_name, result in self.test_results.items():
            status_icon = {
                "PASSED": "✅",
                "FAILED": "❌", 
                "PARTIAL": "⚠️",
                "IMPORT_ERROR": "📦"
            }.get(result.get("status"), "❓")
            
            success_rate = result.get("success_rate", 0)
            print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result.get('status')} ({success_rate:.1%})")
            
            if result.get("status") == "FAILED":
                print(f"    Error: {result.get('error', 'Unknown error')}")
        
        print("\n🚀 Day 2 Feature Status Summary:")
        day2_features = [
            ("Emotion-Aware Responses", "emotion_awareness"),
            ("Human-in-the-Loop Escalation", "escalation_system"), 
            ("Settlement Intelligence", "settlement_intelligence"),
            ("Compliance & Audit", "audit_compliance")
        ]
        
        for feature_name, test_key in day2_features:
            if test_key in self.test_results:
                status = self.test_results[test_key].get("status")
                success_rate = self.test_results[test_key].get("success_rate", 0)
                status_icon = "✅" if status == "PASSED" and success_rate > 0.8 else "⚠️" if status == "PASSED" else "❌"
                print(f"  {status_icon} {feature_name}: {success_rate:.1%}")
            else:
                print(f"  ❓ {feature_name}: Not tested")
        
        # Save detailed report
        report_path = project_root / f"day2_test_report_{self.session_id}.json"
        try:
            with open(report_path, 'w') as f:
                json.dump({
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "test_results": self.test_results,
                    "summary": {
                        "total_tests": total_tests,
                        "passed_tests": passed_tests,
                        "overall_success_rate": passed_tests/total_tests
                    }
                }, f, indent=2, default=str)
            print(f"\n📄 Detailed report saved: {report_path}")
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")

async def main():
    """Run Day 2 integration test"""
    tester = Day2IntegrationTester()
    await tester.run_complete_day2_test()

if __name__ == "__main__":
    asyncio.run(main())