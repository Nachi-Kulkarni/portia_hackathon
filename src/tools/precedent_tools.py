from portia import Tool, ToolRunContext
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import json
import logging
import os

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

class PrecedentAnalysisArgs(BaseModel):
    """Arguments for precedent analysis"""
    claim_type: str = Field(description="The type of claim")
    claim_amount: float = Field(description="The claim amount")
    case_complexity: str = Field(default="moderate", description="The complexity of the case")

class PrecedentAnalysisTool(Tool):
    """Analyze precedent cases to recommend settlement amounts"""
    
    def __init__(self):
        super().__init__(
            id="precedent_analysis",
            name="Precedent Analysis",
            description="Analyze precedent cases to recommend settlement amounts",
            args_schema=PrecedentAnalysisArgs,
            output_schema=("json", "Settlement recommendation based on precedents"),
            structured_output_schema=SettlementRecommendation
        )
        # Store the mock data path in a private variable
        self._mock_data_path = os.getenv("MOCK_POLICY_DB_PATH", "./src/data/mock_policies.json")
    
    def run(self, ctx: ToolRunContext, claim_type: str, claim_amount: float, case_complexity: str = "moderate") -> SettlementRecommendation:
        """Analyze precedents and recommend settlement"""
        
        # Load precedent data (in production, this would be ML-powered)
        precedents = self._load_relevant_precedents(claim_type, claim_amount)
        
        if not precedents:
            # Fallback recommendation
            return SettlementRecommendation(
                recommended_amount=claim_amount * 0.85,  # Conservative 85%
                confidence_level=0.3,
                precedent_cases_analyzed=0,
                settlement_range_min=claim_amount * 0.7,
                settlement_range_max=claim_amount * 0.95,
                estimated_resolution_days=21,
                risk_factors=["no_precedent_data"],
                justification="No precedent data available. Using conservative estimate."
            )
        
        # Analyze precedents
        avg_settlement_pct = sum(p.settlement_percentage for p in precedents) / len(precedents)
        avg_resolution_time = sum(p.resolution_time_days for p in precedents) / len(precedents)
        
        # Calculate recommendation
        recommended_amount = claim_amount * avg_settlement_pct
        confidence = min(len(precedents) / 10.0, 1.0)  # More precedents = higher confidence
        
        return SettlementRecommendation(
            recommended_amount=recommended_amount,
            confidence_level=confidence,
            precedent_cases_analyzed=len(precedents),
            settlement_range_min=recommended_amount * 0.9,
            settlement_range_max=recommended_amount * 1.1,
            estimated_resolution_days=int(avg_resolution_time),
            risk_factors=self._identify_risk_factors(precedents, claim_amount),
            justification=f"Based on {len(precedents)} similar cases with avg settlement of {avg_settlement_pct:.1%}"
        )
    
    def _load_relevant_precedents(self, claim_type: str, claim_amount: float) -> List[PrecedentCase]:
        """Load similar precedent cases"""
        # Mock implementation - in production would use ML similarity matching
        try:
            with open(self._mock_data_path, 'r') as f:
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