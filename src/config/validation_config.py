"""
Configuration settings for claim validation and compliance checks.
Centralizes all magic numbers and thresholds for better maintainability.
"""
import os
from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class ClaimValidationConfig:
    """Configuration for claim validation thresholds"""
    # Fraud detection thresholds
    HIGH_VALUE_CLAIM_THRESHOLD: float = float(os.getenv("CLAIM_HIGH_VALUE_THRESHOLD", "50000"))
    HIGH_VALUE_FRAUD_SCORE_INCREASE: float = float(os.getenv("CLAIM_HIGH_VALUE_FRAUD_SCORE", "0.2"))
    
    # Late reporting thresholds
    LATE_REPORTING_DAYS_THRESHOLD: int = int(os.getenv("CLAIM_LATE_REPORTING_DAYS", "30"))
    LATE_REPORTING_FRAUD_SCORE_INCREASE: float = float(os.getenv("CLAIM_LATE_REPORTING_FRAUD_SCORE", "0.1"))
    
    # Documentation thresholds
    MIN_SUPPORTING_DOCUMENTS: int = int(os.getenv("CLAIM_MIN_DOCUMENTS", "2"))
    INSUFFICIENT_DOCS_FRAUD_SCORE_INCREASE: float = float(os.getenv("CLAIM_INSUFFICIENT_DOCS_FRAUD_SCORE", "0.3"))
    
    # Overall validation thresholds
    FRAUD_SCORE_THRESHOLD: float = float(os.getenv("CLAIM_FRAUD_THRESHOLD", "0.7"))
    INVESTIGATION_THRESHOLD: float = float(os.getenv("CLAIM_INVESTIGATION_THRESHOLD", "0.5"))


@dataclass
class ComplianceConfig:
    """Configuration for regulatory compliance thresholds"""
    # High-value settlement approval thresholds
    SENIOR_MANAGER_APPROVAL_THRESHOLD: float = float(os.getenv("COMPLIANCE_SENIOR_MANAGER_THRESHOLD", "100000"))
    EXECUTIVE_APPROVAL_THRESHOLD: float = float(os.getenv("COMPLIANCE_EXECUTIVE_THRESHOLD", "250000"))
    
    # State-specific regulations
    STATE_REGULATIONS: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "CA": {
            "max_auto_settlement": float(os.getenv("CA_MAX_AUTO_SETTLEMENT", "50000")),
            "required_disclosure": "california_consumer_privacy_notice"
        },
        "NY": {
            "max_auto_settlement": float(os.getenv("NY_MAX_AUTO_SETTLEMENT", "45000")),
            "required_disclosure": "new_york_insurance_disclosure"
        },
        "TX": {
            "max_auto_settlement": float(os.getenv("TX_MAX_AUTO_SETTLEMENT", "55000")),
            "required_disclosure": "texas_insurance_disclosure"
        },
        "FL": {
            "max_auto_settlement": float(os.getenv("FL_MAX_AUTO_SETTLEMENT", "48000")),
            "required_disclosure": "florida_insurance_disclosure"
        }
    })


@dataclass
class SettlementConfig:
    """Configuration for settlement calculation"""
    # Emotional adjustment factors
    HIGH_STRESS_THRESHOLD: float = float(os.getenv("SETTLEMENT_HIGH_STRESS_THRESHOLD", "0.7"))
    VERY_HIGH_STRESS_THRESHOLD: float = float(os.getenv("SETTLEMENT_VERY_HIGH_STRESS_THRESHOLD", "0.8"))
    
    # Adjustment factors
    EMPATHY_ADJUSTMENT_FACTOR: float = float(os.getenv("SETTLEMENT_EMPATHY_ADJUSTMENT", "1.05"))
    HIGH_ANGER_ADJUSTMENT_FACTOR: float = float(os.getenv("SETTLEMENT_HIGH_ANGER_ADJUSTMENT", "1.07"))
    
    # Settlement bounds
    MIN_ADJUSTMENT_FACTOR: float = float(os.getenv("SETTLEMENT_MIN_ADJUSTMENT", "0.9"))
    MAX_ADJUSTMENT_FACTOR: float = float(os.getenv("SETTLEMENT_MAX_ADJUSTMENT", "1.1"))
    
    # Approval thresholds
    SPECIAL_APPROVAL_PERCENTAGE: float = float(os.getenv("SETTLEMENT_SPECIAL_APPROVAL_PERCENTAGE", "0.8"))


@dataclass
class HumeConfig:
    """Configuration for Hume AI integration"""
    # API timeouts
    JOB_POLL_MAX_ATTEMPTS: int = int(os.getenv("HUME_POLL_MAX_ATTEMPTS", "30"))
    JOB_POLL_INTERVAL_SECONDS: int = int(os.getenv("HUME_POLL_INTERVAL", "1"))
    
    # API timeouts
    HUME_API_TIMEOUT: int = int(os.getenv("HUME_API_TIMEOUT", "10"))
    HUME_RESULTS_TIMEOUT: int = int(os.getenv("HUME_RESULTS_TIMEOUT", "10"))


# Singleton instances for easy import
CLAIM_VALIDATION_CONFIG = ClaimValidationConfig()
COMPLIANCE_CONFIG = ComplianceConfig()
SETTLEMENT_CONFIG = SettlementConfig()
HUME_CONFIG = HumeConfig()