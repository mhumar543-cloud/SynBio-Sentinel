# policy_engine.py
from typing import Dict, List, Any
from datetime import datetime

class PolicyEngine:
    """
    Evaluates incoming lab automation commands against deterministic 
    safety policies and maintains stateful session history for cumulative risk analysis.
    """
    def __init__(self, max_cumulative_volume: float = 1000.0):
        # Database of restricted or hazardous biological/chemical reagents (mock)
        self.restricted_reagents = {"toxin_b_agent", "unverified_viral_vector"}
        self.max_cumulative_volume = max_cumulative_volume
        
        # In-memory stateful session storage to track multi-step workflow history
        # Format: {session_id: {"total_volume": float, "history": List[dict]}}
        self.session_store: Dict[str, Dict[str, Any]] = {}

    def evaluate_command(self, command_dict: dict) -> Dict[str, Any]:
        """
        Evaluates a validated command dictionary against static rules and session state.
        Returns a structured audit decision dictionary.
        """
        session_id = command_dict.get("session_id")
        reagent_id = command_dict.get("reagent_id")
        volume = command_dict.get("volume_ul", 0.0)
        
        # Initialize session state tracker if it does not exist
        if session_id not in self.session_store:
            self.session_store[session_id] = {
                "total_volume": 0.0,
                "history": []
            }
        
        session_state = self.session_store[session_id]
        
        # Rule 1: Check against restricted reagent identifiers
        if reagent_id in self.restricted_reagents:
            return {
                "status": "REJECTED",
                "policy_version": "v1.0",
                "timestamp": datetime.utcnow().isoformat(),
                "reason": f"Prohibited reagent identifier detected: {reagent_id}"
            }
        
        # Rule 2: Stateful cumulative volume threshold check
        if session_state["total_volume"] + volume > self.max_cumulative_volume:
            return {
                "status": "REJECTED",
                "policy_version": "v1.0",
                "timestamp": datetime.utcnow().isoformat(),
                "reason": f"Cumulative session volume limit exceeded. Current: {session_state['total_volume']}ul, Requested: {volume}ul, Max Allowed: {self.max_cumulative_volume}ul"
            }
        
        # Update session state on successful evaluation
        session_state["total_volume"] += volume
        session_state["history"].append(command_dict)
        
        return {
            "status": "APPROVED",
            "policy_version": "v1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "reason": "Command satisfies all structural, re-agent safety, and stateful volume constraints."
        }