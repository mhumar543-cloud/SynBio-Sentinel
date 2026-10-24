# crypto_signer.py
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import hashlib
import json
import base64
import time
from typing import Dict, Any, Tuple

class AttestationSigner:
    """
    Manages Ed25519 cryptographic key-pairs and generates cryptographically 
    signed authorization payloads for validated lab commands.
    """
    def __init__(self):
        # Generate an Ed25519 private/public key pair securely in-memory
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def get_public_key_pem(self) -> str:
        """Exports the public key in PEM format for verifiers/proxies."""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    def generate_command_hash(self, command_dict: dict) -> str:
        """Computes a deterministic SHA-256 hash of the command payload."""
        canonical_json = json.dumps(command_dict, sort_keys=True)
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

    def sign_command(self, command_dict: dict, policy_version: str = "v1.0", ttl_seconds: int = 60) -> Dict[str, Any]:
        """
        Creates a signed attestation payload containing the command hash, 
        policy version, expiration TTL, and a unique cryptographic nonce.
        """
        command_hash = self.generate_command_hash(command_dict)
        timestamp = int(time.time())
        nonce = base64.b64encode(os_urandom(16)).decode('utf-8') if 'os_urandom' in globals() else base64.b64encode(hashlib.sha256(str(time.time()).encode()).digest()[:16]).decode('utf-8')
        
        # Construct the payload to be signed
        payload = {
            "command_hash": command_hash,
            "policy_version": policy_version,
            "issued_at": timestamp,
            "expires_at": timestamp + ttl_seconds,
            "nonce": nonce
        }
        
        # Serialize payload into bytes for signing
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        
        # Sign using Ed25519 private key
        signature_bytes = self.private_key.sign(payload_bytes)
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
        
        return {
            "payload": payload,
            "signature": signature_b64,
            "public_key_pem": self.get_public_key_pem()
        }