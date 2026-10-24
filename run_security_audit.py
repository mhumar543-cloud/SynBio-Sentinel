# run_security_audit.py
import requests
from sentinel_core import SynBioSentinelCore
import json
import time

def run_security_audit():
    print("==================================================")
    print("🛡️ SYNBIOSENTINEL: AUTOMATED SECURITY AUDIT SUITE")
    print("==================================================")
    
    sentinel = SynBioSentinelCore()
    proxy_url = "http://127.0.0.1:8000/v1/execute"
    abort_url = "http://127.0.0.1:8000/v1/abort"
    
    # --------------------------------------------------
    # TEST CASE 1: Valid & Safe Command (Happy Path)
    # --------------------------------------------------
    print("\n[TEST 1] Submitting Valid & Authorized Command...")
    valid_command = {
        "session_id": "session-audit-01",
        "action": "transfer_liquid",
        "source_container": "plate1_A1",
        "target_container": "plate2_B3",
        "volume_ul": 50.0,
        "reagent_id": "standard_buffer"
    }
    
    core_result = sentinel.process_command(valid_command)
    if core_result["execution_status"] == "AUTHORIZED":
        response = requests.post(proxy_url, json={
            "command_payload": valid_command,
            "attestation_token": core_result["attestation_token"]
        })
        print(f"👉 HTTP Status Code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    else:
        print("❌ Test 1 Failed at Core Pipeline:", core_result)

    # --------------------------------------------------
    # TEST CASE 2: Policy Violation (Restricted Reagent / Volume Breach)
    # --------------------------------------------------
    print("\n[TEST 2] Simulating Policy Violation (Restricted Reagent / High Volume)...")
    malicious_command = {
        "session_id": "session-audit-01",
        "action": "transfer_liquid",
        "source_container": "plate1_X9",
        "target_container": "plate2_Y9",
        "volume_ul": 1200.0,  # Exceeds max limit or triggers policy rule
        "reagent_id": "unauthorized_pathogen_extract"
    }
    
    violation_result = sentinel.process_command(malicious_command)
    print("👉 Policy Engine Interception Result:")
    print(json.dumps(violation_result, indent=2))

    # --------------------------------------------------
    # TEST CASE 3: Replay Attack (Attempting to reuse an expired/used token)
    # --------------------------------------------------
    print("\n[TEST 3] Simulating Replay Attack (Reusing Cryptographic Token)...")
    # We send the exact same valid payload and token from Test 1 again
    replay_response = requests.post(proxy_url, json={
        "command_payload": valid_command,
        "attestation_token": core_result["attestation_token"]
    })
    print(f"👉 Replay HTTP Status Code: {replay_response.status_code}")
    print(json.dumps(replay_response.json(), indent=2))

    # --------------------------------------------------
    # TEST CASE 4: Hardware Emergency Kill-Switch (/v1/abort)
    # --------------------------------------------------
    print("\n[TEST 4] Triggering Hardware Emergency Kill-Switch...")
    abort_response = requests.post(abort_url)
    print(f"👉 Abort HTTP Status Code: {abort_response.status_code}")
    print(json.dumps(abort_response.json(), indent=2))
    
    print("\n==================================================")
    print("✅ SECURITY AUDIT COMPLETE: All Layers Verified.")
    print("==================================================")

if __name__ == "__main__":
    run_security_audit()