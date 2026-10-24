# sentinel_core.py
from schemas import LabCommand
from policy_engine import PolicyEngine
from crypto_signer import AttestationSigner
from typing import Dict, Any

class SynBioSentinelCore:
    """
    Core pipeline integrating Layer 1 (Stateful Policy Engine) 
    and Layer 2 (Ed25519 Cryptographic Attestation).
    """
    def __init__(self):
        self.policy_engine = PolicyEngine(max_cumulative_volume=1000.0)
        self.signer = AttestationSigner()

    def process_command(self, raw_command_data: dict) -> Dict[str, Any]:
        """
        Processes a raw command through structural validation, stateful policy inspection,
        and generates a signed attestation token if approved.
        """
        try:
            # Step 1: Structural Validation via Pydantic
            validated_cmd = LabCommand(**raw_command_data)
            cmd_dict = validated_cmd.model_dump(mode='json')
            
            # Step 2: Stateful Policy Engine Inspection
            policy_decision = self.policy_engine.evaluate_command(cmd_dict)
            
            if policy_decision["status"] != "APPROVED":
                return {
                    "execution_status": "BLOCKED",
                    "layer": "Layer-1 (Policy Engine)",
                    "decision": policy_decision
                }
            
            # Step 3: Cryptographic Attestation Generation (Layer 2)
            signed_token = self.signer.sign_command(cmd_dict, policy_version=policy_decision["policy_version"])
            
            return {
                "execution_status": "AUTHORIZED",
                "layer": "Layer-2 (Attestation Engine)",
                "policy_decision": policy_decision,
                "attestation_token": signed_token
            }

        except Exception as e:
            return {
                "execution_status": "ERROR",
                "layer": "Layer-1 (Pydantic Schema)",
                "reason": str(e)
            }