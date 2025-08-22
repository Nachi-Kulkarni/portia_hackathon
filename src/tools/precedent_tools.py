from portia.tool import Tool, ToolRunContext
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import json
import logging
import os
import random

logger = logging.getLogger(__name__)

class PrecedentCase(BaseModel):
    """Historical precedent case"""
    case_id: str
    claim_type: str
    original_claim: float
    settlement_amount: float
    settlement_percentage: float
    resolution_time_days: int
    customer_satisfaction_score: float
    case_complexity: str  # simple, moderate, complex
    special_circumstances: List[str]

class SettlementRecommendation(BaseModel):
    """Settlement recommendation based on precedents"""
    recommended_amount: float
    confidence_level: float
    precedent_cases_analyzed: int
    settlement_range_min: float
    settlement_range_max: float
    estimated_resolution_days: int
    risk_factors: List[str]
    justification: str
    creative_options: List[Dict[str, Any]]  # New field for creative settlement options

class PrecedentAnalysisTool(Tool):
    """Analyze precedent cases to recommend settlement amounts"""
    
    def __init__(self):
        super().__init__()
        self.mock_data_path = os.getenv("MOCK_POLICY_DB_PATH", "./src/data/mock_policies.json")
    
    def run(self, ctx: ToolRunContext, claim_type: str, claim_amount: float, 
            case_complexity: str = "moderate", emotional_context: Dict = None) -> SettlementRecommendation:
        """Analyze precedents and recommend settlement with creative options"""
        
        # Load precedent data (in production, this would be ML-powered)
        precedents = self._load_relevant_precedents(claim_type, claim_amount)
        
        if not precedents:
            # Fallback recommendation with creative options
            creative_options = self._generate_creative_settlement_options(
                claim_amount, case_complexity, emotional_context
            )
            
            return SettlementRecommendation(
                recommended_amount=claim_amount * 0.85,  # Conservative 85%
                confidence_level=0.3,
                precedent_cases_analyzed=0,
                settlement_range_min=claim_amount * 0.7,
                settlement_range_max=claim_amount * 0.95,
                estimated_resolution_days=21,
                risk_factors=["no_precedent_data"],
                justification="No precedent data available. Using conservative estimate.",
                creative_options=creative_options
            )
        
        # Analyze precedents
        avg_settlement_pct = sum(p.settlement_percentage for p in precedents) / len(precedents)
        avg_resolution_time = sum(p.resolution_time_days for p in precedents) / len(precedents)
        
        # Calculate recommendation
        recommended_amount = claim_amount * avg_settlement_pct
        confidence = min(len(precedents) / 10.0, 1.0)  # More precedents = higher confidence
        
        # Generate creative settlement options
        creative_options = self._generate_creative_settlement_options(
            recommended_amount, case_complexity, emotional_context, precedents
        )
        
        return SettlementRecommendation(
            recommended_amount=recommended_amount,
            confidence_level=confidence,
            precedent_cases_analyzed=len(precedents),
            settlement_range_min=recommended_amount * 0.9,
            settlement_range_max=recommended_amount * 1.1,
            estimated_resolution_days=int(avg_resolution_time),
            risk_factors=self._identify_risk_factors(precedents, claim_amount),
            justification=f"Based on {len(precedents)} similar cases with avg settlement of {avg_settlement_pct:.1%}",
            creative_options=creative_options
        )
    
    def _load_relevant_precedents(self, claim_type: str, claim_amount: float) -> List[PrecedentCase]:
        """Load similar precedent cases"""
        # Mock implementation - in production would use ML similarity matching
        try:
            with open(self.mock_data_path, 'r') as f:
                data = json.load(f)
            
            precedents = []
            for case_data in data.get("precedent_cases", []):
                if (case_data["claim_type"] == claim_type and 
                    abs(case_data["original_claim"] - claim_amount) / claim_amount < 0.5):  # Within 50%
                    precedents.append(PrecedentCase(**case_data))
            
            return precedents[:10]  # Limit to top 10 matches
            
        except Exception as e:
            logger.error(f"Error loading precedents: {str(e)}")
            return []
    
    def _identify_risk_factors(self, precedents: List[PrecedentCase], claim_amount: float) -> List[str]:
        """Identify risk factors from precedent analysis"""
        risk_factors = []
        
        if claim_amount > 50000:
            risk_factors.append("high_value_claim")
        
        if len(precedents) < 3:
            risk_factors.append("limited_precedent_data")
        
        # Check if satisfaction scores are consistently low
        if precedents:
            avg_satisfaction = sum(p.customer_satisfaction_score for p in precedents) / len(precedents)
            if avg_satisfaction < 3.5:
                risk_factors.append("historically_low_satisfaction")
        
        return risk_factors
    
    def _generate_creative_settlement_options(self, settlement_amount: float, 
                                            case_complexity: str, 
                                            emotional_context: Dict = None,
                                            precedents: List[PrecedentCase] = None) -> List[Dict[str, Any]]:
        """Generate creative settlement options based on case details and emotional context"""
        options = []
        
        # Option 1: Immediate partial payment
        options.append({
            "type": "immediate_partial",
            "description": "Immediate partial payment with balance paid later",
            "amount": settlement_amount * 0.7,
            "immediate_payment": settlement_amount * 0.4,
            "balance_payment_days": 15,
            "benefit": "Provides immediate financial relief",
            "best_for": ["high_emotional_distress", "urgent_financial_need"]
        })
        
        # Option 2: Structured settlement
        options.append({
            "type": "structured",
            "description": "Structured monthly payments over time",
            "amount": settlement_amount * 0.95,  # Slightly higher total
            "monthly_payment": settlement_amount * 0.95 / 12,
            "payment_period_months": 12,
            "benefit": "Consistent income stream",
            "best_for": ["long_term_financial_planning", "retirees"]
        })
        
        # Option 3: Enhanced service package
        options.append({
            "type": "enhanced_service",
            "description": "Standard settlement plus additional services",
            "amount": settlement_amount * 0.9,
            "additional_services": ["rental_car_voucher", "home_repair_assessment", "legal_consultation_voucher"],
            "benefit": "Additional support beyond monetary settlement",
            "best_for": ["service_oriented_customers", "complex_situations"]
        })
        
        # Option 4: Premium fast-track
        options.append({
            "type": "fast_track",
            "description": "Premium processing with expedited resolution",
            "amount": settlement_amount * 0.85,
            "processing_time_days": 5,  # Much faster than standard
            "benefit": "Quick resolution and payment",
            "best_for": ["high_stress", "time_sensitive_needs"]
        })
        
        # Filter options based on emotional context if provided
        if emotional_context:
            primary_emotion = emotional_context.get("primary_emotion", "neutral")
            stress_level = emotional_context.get("stress_level", 0.5)
            
            # Adjust options based on emotional state
            if primary_emotion == "sadness" or stress_level > 0.7:
                # For emotionally distressed customers, emphasize fast-track and immediate payment options
                for option in options:
                    if option["type"] in ["immediate_partial", "fast_track"]:
                        option["recommended"] = True
            elif primary_emotion == "anxiety":
                # For anxious customers, emphasize structured settlement for predictability
                for option in options:
                    if option["type"] == "structured":
                        option["recommended"] = True
        
        # Add confidence scores to options
        for i, option in enumerate(options):
            # Higher confidence for options similar to successful precedents
            base_confidence = 0.7
            if precedents:
                # Check if any precedent used similar approach
                similar_precedents = [p for p in precedents if 
                                    any(circ in option["type"] for circ in p.special_circumstances)]
                if similar_precedents:
                    avg_satisfaction = sum(p.customer_satisfaction_score for p in similar_precedents) / len(similar_precedents)
                    base_confidence = avg_satisfaction / 5.0  # Normalize to 0-1 scale
            
            option["confidence_score"] = round(base_confidence, 2)
        
        return options