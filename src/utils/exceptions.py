"""
Custom exceptions for the insurance claim negotiator system.
Provides specific error types for better error handling and debugging.
"""


class ClaimProcessingError(Exception):
    """Base exception for claim processing errors"""
    pass


class PolicyNotFoundError(ClaimProcessingError):
    """Raised when a policy cannot be found in the database"""
    def __init__(self, policy_number: str):
        self.policy_number = policy_number
        super().__init__(f"Policy {policy_number} not found in database")


class ClaimValidationError(ClaimProcessingError):
    """Raised when claim validation fails due to data issues"""
    def __init__(self, message: str, validation_issues: list = None):
        self.validation_issues = validation_issues or []
        super().__init__(message)


class InvalidDateFormatError(ClaimProcessingError):
    """Raised when date parsing fails"""
    def __init__(self, date_value: str, expected_format: str = "ISO format"):
        self.date_value = date_value
        self.expected_format = expected_format
        super().__init__(f"Invalid date format: '{date_value}'. Expected {expected_format}")


class HumeAPIError(ClaimProcessingError):
    """Raised when Hume AI API calls fail"""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(f"Hume API Error: {message}" + (f" (Status: {status_code})" if status_code else ""))


class ComplianceViolationError(ClaimProcessingError):
    """Raised when regulatory compliance checks fail"""
    def __init__(self, violations: list, state: str = None):
        self.violations = violations
        self.state = state
        violation_text = "; ".join(violations)
        super().__init__(f"Compliance violations: {violation_text}" + (f" (State: {state})" if state else ""))


class SettlementCalculationError(ClaimProcessingError):
    """Raised when settlement calculation fails"""
    def __init__(self, message: str, claim_amount: float = None, policy_coverage: float = None):
        self.claim_amount = claim_amount
        self.policy_coverage = policy_coverage
        super().__init__(message)


class AudioProcessingError(ClaimProcessingError):
    """Raised when audio processing fails"""
    def __init__(self, message: str, audio_format: str = None):
        self.audio_format = audio_format
        super().__init__(f"Audio processing error: {message}" + (f" (Format: {audio_format})" if audio_format else ""))


class ConfigurationError(ClaimProcessingError):
    """Raised when configuration is invalid or missing"""
    def __init__(self, config_key: str, message: str = None):
        self.config_key = config_key
        default_message = f"Configuration error for key: {config_key}"
        super().__init__(message or default_message)