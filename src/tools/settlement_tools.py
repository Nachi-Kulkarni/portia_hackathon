from portia import Tool, ToolRunContext
from pydantic import BaseModel, Field
from typing import Dict, Optional
import logging
from datetime import datetime
from src.config import SETTLEMENT_CONFIG
from src.utils.exceptions import SettlementCalculationError

logger = logging.getLogger(__name__)

class SettlementOfferArgs(BaseModel):
    """Arguments for settlement offer generation"""
    claim_amount: float = Field(description="The claimed amount")
    policy_coverage: float = Field(description="The policy coverage limit")
    damage_assessment: float = Field(description="The assessed damage amount")
    emotional_context: Optional[str] = Field(default="neutral", description="Customer emotional state")
    stress_level: Optional[float] = Field(default=0.5, description="Customer stress level (0-1)")

class SettlementOfferResult(BaseModel):
    """Settlement offer result"""
    settlement_amount: float = Field(description="The calculated settlement amount")
    offer_reasoning: str = Field(description="Explanation of how the offer was calculated")
    confidence_score: float = Field(description="Confidence in the offer (0-1)")
    recommended_next_steps: str = Field(description="Recommended next steps")
    requires_approval: bool = Field(description="Whether the offer requires special approval")

class SettlementOfferTool(Tool):
    """Generate settlement offers based on claim analysis and emotional context"""
    
    def __init__(self):
        # Initialize the Tool with required parameters
        super().__init__(
            id="settlement_offer",
            name="Settlement Offer Generator",
            description="Generate settlement offers based on claim analysis and emotional context",
            args_schema=SettlementOfferArgs,
            output_schema=("json", "Settlement offer including amount and reasoning"),
            structured_output_schema=SettlementOfferResult
        )
    
    def run(self, ctx: ToolRunContext, claim_amount: float, policy_coverage: float, 
            damage_assessment: float, emotional_context: Optional[str] = "neutral", 
            stress_level: Optional[float] = 0.5) -> SettlementOfferResult:
        """Generate a settlement offer"""
        
        try:
            # Calculate base settlement (lesser of claim or policy coverage)
            base_settlement = min(claim_amount, policy_coverage, damage_assessment)
            
            # Adjust for emotional context
            adjustment_factor = self._calculate_emotional_adjustment(emotional_context, stress_level)
            adjusted_settlement = base_settlement * adjustment_factor
            
            # Ensure settlement doesn't exceed policy limits
            final_settlement = min(adjusted_settlement, policy_coverage)
            
            # Determine confidence and approval needs
            confidence = self._calculate_confidence(claim_amount, policy_coverage, damage_assessment)
            requires_approval = self._requires_special_approval(final_settlement, policy_coverage)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                base_settlement, final_settlement, emotional_context, 
                adjustment_factor, confidence
            )
            
            return SettlementOfferResult(
                settlement_amount=final_settlement,
                offer_reasoning=reasoning,
                confidence_score=confidence,
                recommended_next_steps="Send offer to customer with explanation",
                requires_approval=requires_approval
            )
            
        except Exception as e:
            logger.error(f"Error generating settlement offer: {str(e)}")
            # Fallback to basic calculation
            base_settlement = min(claim_amount, policy_coverage, damage_assessment)
            return SettlementOfferResult(
                settlement_amount=base_settlement,
                offer_reasoning="Fallback calculation due to processing error",
                confidence_score=0.3,
                recommended_next_steps="Review manually due to error",
                requires_approval=True
            )
    
    def _calculate_emotional_adjustment(self, emotional_context: str, stress_level: float) -> float:
        """Calculate adjustment factor based on emotional context using configurable thresholds"""
        # Base adjustment
        adjustment = 1.0
        
        # Log emotional context for audit
        logger.info(f"Calculating emotional adjustment for {emotional_context} with stress level {stress_level:.2f}")
        
        # Increase for high stress/negative emotions (show empathy) using config
        if emotional_context in ["anger", "frustration", "sadness"] and stress_level > SETTLEMENT_CONFIG.HIGH_STRESS_THRESHOLD:
            adjustment = SETTLEMENT_CONFIG.EMPATHY_ADJUSTMENT_FACTOR
            logger.info(f"Applied empathy adjustment: {adjustment:.3f} for {emotional_context}")
        elif emotional_context in ["anger", "frustration"] and stress_level > SETTLEMENT_CONFIG.VERY_HIGH_STRESS_THRESHOLD:
            adjustment = SETTLEMENT_CONFIG.HIGH_ANGER_ADJUSTMENT_FACTOR
            logger.warning(f"Applied high anger adjustment: {adjustment:.3f} for very stressed customer")
        
        # Ensure reasonable bounds using config
        bounded_adjustment = max(SETTLEMENT_CONFIG.MIN_ADJUSTMENT_FACTOR, 
                                min(SETTLEMENT_CONFIG.MAX_ADJUSTMENT_FACTOR, adjustment))
        
        if bounded_adjustment != adjustment:
            logger.warning(f"Adjustment factor bounded from {adjustment:.3f} to {bounded_adjustment:.3f}")
        
        return bounded_adjustment
    
    def _calculate_confidence(self, claim_amount: float, policy_coverage: float, 
                             damage_assessment: float) -> float:
        """Calculate confidence score for the settlement"""
        # High confidence when all values are close
        values = [claim_amount, policy_coverage, damage_assessment]
        max_val = max(values)
        min_val = min(values)
        
        if max_val == 0:
            return 0.5
            
        # Confidence decreases with variance
        variance = (max_val - min_val) / max_val
        confidence = 1.0 - variance
        return max(0.1, min(0.95, confidence))
    
    def _requires_special_approval(self, settlement_amount: float, 
                                  policy_coverage: float) -> bool:
        """Determine if special approval is required using configurable threshold"""
        threshold_amount = policy_coverage * SETTLEMENT_CONFIG.SPECIAL_APPROVAL_PERCENTAGE
        requires_approval = settlement_amount > threshold_amount
        
        if requires_approval:
            logger.warning(f"Special approval required: ${settlement_amount:,.2f} > ${threshold_amount:,.2f} ({SETTLEMENT_CONFIG.SPECIAL_APPROVAL_PERCENTAGE:.1%} of coverage)")
        
        return requires_approval
    
    def _generate_reasoning(self, base_settlement: float, final_settlement: float,
                           emotional_context: str, adjustment_factor: float,
                           confidence: float) -> str:
        """Generate human-readable reasoning for the offer"""
        reasoning_parts = []
        
        if base_settlement != final_settlement:
            reasoning_parts.append(f"Adjusted from base amount of ${base_settlement:,.2f}")
        
        if adjustment_factor != 1.0:
            reasoning_parts.append(f"Emotional adjustment applied for {emotional_context} context")
        
        if confidence < 0.7:
            reasoning_parts.append("Lower confidence due to data variance")
        
        if not reasoning_parts:
            reasoning_parts.append("Standard settlement calculation applied")
            
        return "; ".join(reasoning_parts) if reasoning_parts else "Settlement calculated based on policy terms and damage assessment"