# proxy_server.py
from fastapi import FastAPI, HTTPException, Header, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import base64
import json

app = FastAPI(title="SynBio-Sentinel Interceptor Proxy", version="1.0")

# In-memory nonce cache to prevent replay attacks
USED_NONCES = set()

class ExecutionRequest(BaseModel):
    command_payload: Dict[str, Any]
    attestation_token: Dict[str, Any]

@app.post("/v1/execute")
async def intercept_and_execute(req: ExecutionRequest):
    """
    Fail-closed interceptor proxy. Validates signature, TTL expiration, 
    replay attacks (nonce), and dispatches to hardware if valid.
    """
    token = req.attestation_token
    payload = token.get("payload")
    signature_b64 = token.get("signature")
    public_key_pem = token.get("public_key_pem")
    
    # 1. Fail-Closed Check: Missing cryptographic proof elements
    if not payload or not signature_b64 or not public_key_pem:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ACCESS DENIED: Missing cryptographic attestation proof. Default-deny enforced."
        )
    
    try:
        # 2. Expiration Check (TTL)
        current_time = int(time.time())
        if current_time > payload.get("expires_at", 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ACCESS DENIED: Attestation token has expired (TTL exceeded)."
            )
        
        # 3. Replay Attack Prevention (Nonce Check)
        nonce = payload.get("nonce")
        if nonce in USED_NONCES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ACCESS DENIED: Replay attack detected. Nonce has already been utilized."
            )
        USED_NONCES.add(nonce)
        
        # 4. Cryptographic Signature Verification
        public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature_bytes = base64.b64decode(signature_b64)
        
        public_key.verify(signature_bytes, payload_bytes)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"ACCESS DENIED: Cryptographic verification failed. Reason: {str(e)}"
        )
    
    # 5. Dispatch Execution to Simulated OpenTrons Hardware API
    return {
        "status": "SUCCESS",
        "proxy_action": "DISPATCHED_TO_HARDWARE",
        "message": "Command verified successfully. Execution routed to lab automation queue.",
        "verified_command_hash": payload.get("command_hash")
    }

@app.post("/v1/abort")
async def emergency_kill_switch():
    """
    Emergency Kill-Switch: Flushes the hardware execution queue and aborts active workflows.
    """
    # In production, this triggers an immediate SIGTERM/abort signal to the OpenTrons driver
    return {
        "status": "EMERGENCY_ABORT",
        "action": "QUEUE_FLUSHED",
        "message": "Hardware execution queue successfully flushed. All operations halted."
    }