"""
Conversation State Management for Insurance Claim Negotiation

Tracks conversation history, context, and state throughout the claim process.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConversationTurn:
    """Single conversation turn"""
    timestamp: datetime
    speaker: str  # "customer" or "agent"
    message: str
    emotion_analysis: Optional[Dict[str, Any]] = None
    tool_calls: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ClaimContext:
    """Current claim context"""
    claim_id: str
    policy_number: str
    claim_type: str
    estimated_amount: float
    customer_id: str
    status: str = "in_progress"
    settlement_offer: Optional[Dict[str, Any]] = None
    escalation_needed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConversationState:
    """Manages conversation state and history"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.conversation_history: List[ConversationTurn] = []
        self.claim_context: Optional[ClaimContext] = None
        self.customer_profile: Dict[str, Any] = {}
        self.interaction_summary: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        
    def add_turn(self, 
                 speaker: str, 
                 message: str, 
                 emotion_analysis: Optional[Dict[str, Any]] = None,
                 tool_calls: List[str] = None) -> None:
        """Add a conversation turn"""
        turn = ConversationTurn(
            timestamp=datetime.now(),
            speaker=speaker,
            message=message,
            emotion_analysis=emotion_analysis,
            tool_calls=tool_calls or [],
            metadata={}
        )
        
        self.conversation_history.append(turn)
        self.last_updated = datetime.now()
        
        # Update interaction summary
        self._update_interaction_summary(turn)
        
        logger.info(f"Added conversation turn for {speaker} in session {self.session_id}")
    
    def set_claim_context(self, claim_data: Dict[str, Any]) -> None:
        """Set or update claim context"""
        self.claim_context = ClaimContext(
            claim_id=claim_data.get("claim_id", ""),
            policy_number=claim_data.get("policy_number", ""),
            claim_type=claim_data.get("claim_type", ""),
            estimated_amount=claim_data.get("estimated_amount", 0),
            customer_id=claim_data.get("customer_id", ""),
            status=claim_data.get("status", "in_progress"),
            metadata=claim_data
        )
        
        self.last_updated = datetime.now()
        logger.info(f"Updated claim context for {self.claim_context.claim_id}")
    
    def update_settlement_offer(self, settlement_data: Dict[str, Any]) -> None:
        """Update settlement offer in claim context"""
        if self.claim_context:
            self.claim_context.settlement_offer = settlement_data
            self.last_updated = datetime.now()
            logger.info(f"Updated settlement offer for claim {self.claim_context.claim_id}")
    
    def flag_for_escalation(self, reason: str) -> None:
        """Flag conversation for human escalation"""
        if self.claim_context:
            self.claim_context.escalation_needed = True
            self.claim_context.metadata["escalation_reason"] = reason
            self.last_updated = datetime.now()
            logger.warning(f"Conversation {self.session_id} flagged for escalation: {reason}")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation"""
        total_turns = len(self.conversation_history)
        customer_turns = [t for t in self.conversation_history if t.speaker == "customer"]
        agent_turns = [t for t in self.conversation_history if t.speaker == "agent"]
        
        # Analyze customer emotions throughout conversation
        emotions = []
        for turn in customer_turns:
            if turn.emotion_analysis:
                emotions.append(turn.emotion_analysis.get("primary_emotion", "neutral"))
        
        return {
            "session_id": self.session_id,
            "total_turns": total_turns,
            "customer_turns": len(customer_turns),
            "agent_turns": len(agent_turns),
            "duration_minutes": (self.last_updated - self.created_at).total_seconds() / 60,
            "emotions_detected": emotions,
            "escalation_needed": self.claim_context.escalation_needed if self.claim_context else False,
            "claim_status": self.claim_context.status if self.claim_context else "no_claim",
            "settlement_offered": bool(self.claim_context.settlement_offer) if self.claim_context else False,
            "interaction_summary": self.interaction_summary
        }
    
    def get_context_for_agent(self) -> Dict[str, Any]:
        """Get context information for the agent"""
        recent_turns = self.conversation_history[-5:]  # Last 5 turns
        
        return {
            "claim_context": self.claim_context.__dict__ if self.claim_context else None,
            "recent_conversation": [
                {
                    "speaker": turn.speaker,
                    "message": turn.message,
                    "emotion": turn.emotion_analysis.get("primary_emotion") if turn.emotion_analysis else "neutral",
                    "timestamp": turn.timestamp.isoformat()
                }
                for turn in recent_turns
            ],
            "customer_profile": self.customer_profile,
            "session_summary": self.get_conversation_summary()
        }
    
    def _update_interaction_summary(self, turn: ConversationTurn) -> None:
        """Update interaction summary based on new turn"""
        if turn.speaker == "customer":
            # Track customer sentiment trends
            if turn.emotion_analysis:
                emotion = turn.emotion_analysis.get("primary_emotion", "neutral")
                stress = turn.emotion_analysis.get("stress_level", 0)
                
                if "customer_emotions" not in self.interaction_summary:
                    self.interaction_summary["customer_emotions"] = []
                
                self.interaction_summary["customer_emotions"].append({
                    "emotion": emotion,
                    "stress_level": stress,
                    "timestamp": turn.timestamp.isoformat()
                })
                
                # Update current emotional state
                self.interaction_summary["current_emotion"] = emotion
                self.interaction_summary["current_stress"] = stress
        
        elif turn.speaker == "agent":
            # Track agent actions
            if "agent_actions" not in self.interaction_summary:
                self.interaction_summary["agent_actions"] = []
            
            self.interaction_summary["agent_actions"].extend(turn.tool_calls)
    
    def save_to_file(self, filepath: str) -> bool:
        """Save conversation state to JSON file"""
        try:
            data = {
                "session_id": self.session_id,
                "created_at": self.created_at.isoformat(),
                "last_updated": self.last_updated.isoformat(),
                "claim_context": self.claim_context.__dict__ if self.claim_context else None,
                "customer_profile": self.customer_profile,
                "interaction_summary": self.interaction_summary,
                "conversation_history": [
                    {
                        "timestamp": turn.timestamp.isoformat(),
                        "speaker": turn.speaker,
                        "message": turn.message,
                        "emotion_analysis": turn.emotion_analysis,
                        "tool_calls": turn.tool_calls,
                        "metadata": turn.metadata
                    }
                    for turn in self.conversation_history
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved conversation state to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save conversation state: {str(e)}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> Optional['ConversationState']:
        """Load conversation state from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            state = cls(data["session_id"])
            state.created_at = datetime.fromisoformat(data["created_at"])
            state.last_updated = datetime.fromisoformat(data["last_updated"])
            state.customer_profile = data.get("customer_profile", {})
            state.interaction_summary = data.get("interaction_summary", {})
            
            # Restore claim context
            if data.get("claim_context"):
                claim_data = data["claim_context"]
                state.claim_context = ClaimContext(**claim_data)
            
            # Restore conversation history
            for turn_data in data.get("conversation_history", []):
                turn = ConversationTurn(
                    timestamp=datetime.fromisoformat(turn_data["timestamp"]),
                    speaker=turn_data["speaker"],
                    message=turn_data["message"],
                    emotion_analysis=turn_data.get("emotion_analysis"),
                    tool_calls=turn_data.get("tool_calls", []),
                    metadata=turn_data.get("metadata", {})
                )
                state.conversation_history.append(turn)
            
            logger.info(f"Loaded conversation state from {filepath}")
            return state
            
        except Exception as e:
            logger.error(f"Failed to load conversation state: {str(e)}")
            return None


class ConversationManager:
    """Manages multiple conversation sessions"""
    
    def __init__(self):
        self.active_sessions: Dict[str, ConversationState] = {}
        self.session_timeout_minutes = 30
    
    def get_or_create_session(self, session_id: str) -> ConversationState:
        """Get existing session or create new one"""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = ConversationState(session_id)
            logger.info(f"Created new conversation session: {session_id}")
        
        return self.active_sessions[session_id]
    
    def end_session(self, session_id: str, save_to_file: bool = True) -> bool:
        """End conversation session and optionally save"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            if save_to_file:
                filepath = f"conversation_logs/session_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                session.save_to_file(filepath)
            
            del self.active_sessions[session_id]
            logger.info(f"Ended conversation session: {session_id}")
            return True
        
        return False
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of specific session"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id].get_conversation_summary()
        return None
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            time_since_update = (current_time - session.last_updated).total_seconds() / 60
            if time_since_update > self.session_timeout_minutes:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.end_session(session_id, save_to_file=True)
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        return len(expired_sessions)