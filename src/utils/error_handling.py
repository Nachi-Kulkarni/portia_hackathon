"""
Comprehensive Error Handling and Graceful Degradation

Provides robust error handling, retry mechanisms, and graceful fallbacks
for the insurance claim negotiation system.
"""

import logging
import time
import functools
from typing import Callable, Any, Dict, Optional, List, Type
from datetime import datetime, timedelta
import traceback

logger = logging.getLogger(__name__)

class SystemError(Exception):
    """Base exception for system errors"""
    def __init__(self, message: str, error_code: str = "SYSTEM_ERROR", details: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now()

class ErrorRecoveryManager:
    """Manages error recovery and system health"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.last_errors: Dict[str, datetime] = {}
        self.system_health: Dict[str, str] = {
            "voice_processing": "healthy",
            "emotion_analysis": "healthy", 
            "policy_lookup": "healthy",
            "claim_validation": "healthy",
            "settlement_generation": "healthy",
            "overall_system": "healthy"
        }
        self.degraded_mode = False
    
    def record_error(self, component: str, error: Exception, context: Dict[str, Any] = None) -> None:
        """Record an error for tracking and health monitoring"""
        error_key = f"{component}_{type(error).__name__}"
        
        # Update error counts
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        self.last_errors[error_key] = datetime.now()
        
        # Update component health
        if self.error_counts[error_key] >= 3:
            self.system_health[component] = "degraded"
            
        if self.error_counts[error_key] >= 5:
            self.system_health[component] = "failed"
        
        logger.error(f"Error recorded for {component}: {str(error)}")
    
    def record_success(self, component: str) -> None:
        """Record successful operation to improve health status"""
        # Reset error counts on success
        error_keys_to_reset = [k for k in self.error_counts.keys() if k.startswith(component)]
        for key in error_keys_to_reset:
            if self.error_counts[key] > 0:
                self.error_counts[key] = max(0, self.error_counts[key] - 1)
        
        # Improve health status
        if self.system_health.get(component) == "failed" and self.error_counts.get(component, 0) == 0:
            self.system_health[component] = "degraded"
        elif self.system_health.get(component) == "degraded" and self.error_counts.get(component, 0) == 0:
            self.system_health[component] = "healthy"
    
    def get_system_status_report(self) -> Dict[str, Any]:
        """Get comprehensive system status report"""
        return {
            "overall_health": self.system_health["overall_system"],
            "degraded_mode": self.degraded_mode,
            "component_health": {k: v for k, v in self.system_health.items() if k != "overall_system"},
            "error_counts": self.error_counts,
            "last_check": datetime.now().isoformat()
        }

# Global error recovery manager instance
error_recovery = ErrorRecoveryManager()

def get_user_friendly_error_message(error: Exception) -> str:
    """Convert technical errors to user-friendly messages"""
    error_messages = {
        "APIError": "We're experiencing connectivity issues. Please try again in a moment.",
        "VoiceProcessingError": "There was an issue processing your voice. You can continue with text input.",
        "ToolExecutionError": "We're having trouble accessing some services. Your request may take longer to process.",
        "SystemError": "We're experiencing technical difficulties. Our team has been notified."
    }
    
    error_type = type(error).__name__
    return error_messages.get(error_type, "An unexpected error occurred. Please contact support if this persists.")

def create_error_response(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "status": "error",
        "error_type": type(error).__name__,
        "error_message": get_user_friendly_error_message(error),
        "timestamp": datetime.now().isoformat(),
        "context": context or {}
    }