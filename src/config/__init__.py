"""
Configuration management for the insurance claim negotiator.
"""
from .validation_config import (
    CLAIM_VALIDATION_CONFIG,
    COMPLIANCE_CONFIG, 
    SETTLEMENT_CONFIG,
    HUME_CONFIG
)

class ConfigurationError(Exception):
    """Raised when required configuration is missing"""
    pass

__all__ = [
    'CLAIM_VALIDATION_CONFIG',
    'COMPLIANCE_CONFIG',
    'SETTLEMENT_CONFIG', 
    'HUME_CONFIG',
    'ConfigurationError'
]