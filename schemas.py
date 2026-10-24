# schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import uuid

class LabCommand(BaseModel):
    session_id: str = Field(..., description="Unique ID for the multi-step experimental session")
    command_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for this specific command")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp of the command request")
    
    action: str = Field(..., description="Type of action, e.g., 'transfer_liquid', 'mix', 'synthesize'")
    source_container: str = Field(..., description="Source plate/well identifier")
    target_container: str = Field(..., description="Target plate/well identifier")
    
    volume_ul: float = Field(..., gt=0, description="Volume to transfer in microliters (must be > 0)")
    reagent_id: str = Field(..., description="Identifier for the biological or chemical reagent")
    sequence_data: Optional[str] = Field(None, description="Optional raw sequence string or hash if applicable")

    @field_validator('action')
    def validate_action_type(cls, v):
        allowed_actions = ['transfer_liquid', 'mix', 'dispense', 'aspirate']
        if v.lower() not in allowed_actions:
            raise ValueError(f"Invalid action '{v}'. Allowed actions: {allowed_actions}")
        return v.lower() 