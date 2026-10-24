# SynBio-Sentinel 🛡️
> *Privacy-Aware, Cryptographically Verified Workflow Authorization Proxy for Autonomous Wet-Labs*

---

## 🔬 Executive Overview

In high-stakes synthetic biology and wet-lab automation, relying on probabilistic AI guardrails (like basic chat prompts or regex text filters) is a critical security vulnerability. **SynBio-Sentinel** decouples autonomous AI workflow planning from physical lab hardware execution. 

It enforces an immutable, **fail-closed cryptographic proxy** between AI agents and lab automation drivers (e.g., OpenTrons), ensuring that zero unauthorized reagents, policy violations, or cumulative volume breaches can ever reach physical laboratory infrastructure.

---

## 🏛️ 3-Layer System Architecture


[ Autonomous Agent Command (JSON) ]
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: Semantic & Stateful Policy Engine                                  │
│ ├─ Pydantic Validation: Enforces strict structural typing & formatting.     │
│ └─ Stateful Session Tracker: Tracks multi-step history & cumulative volume. │
└──────────────────────────────────────┬──────────────────────────────────────┘
│ Pass / Clean Session Audit
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: Cryptographic Attestation Module                                   │
│ ├─ Ed25519 Asymmetric Signatures: Tamper-proof cryptographic token binding. │
│ └─ Nonce & TTL Controls: Cryptographically binds command hashes to prevent  │
│    replay and Man-in-the-Middle (MITM) attacks.                             │
└──────────────────────────────────────┬──────────────────────────────────────┘
│ Signed Attestation Token
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: Fail-Closed Interceptor Proxy (FastAPI)                            │
│ ├─ Default-Deny Gateway: Rejects all unsigned or unverified requests (403). │
│ ├─ Active Replay Cache: Verifies single-use nonces and expiration windows.  │
│ └─ Emergency Hardware Kill-Switch: Async /v1/abort hook to flush execution│
│    queues and halt laboratory hardware instantly.                           │
└─────────────────────────────────────────────────────────────────────────────┘


---

## 📂 Project File Structure

```text
synbio-sentinel/
├── schemas.py                 # Layer 1: Pydantic data schemas & typing
├── policy_engine.py           # Layer 1: Stateful session & volume checker
├── crypto_signer.py           # Layer 2: Ed25519 key management & signing
├── sentinel_core.py           # Core pipeline orchestration glue
├── proxy_server.py            # Layer 3: FastAPI fail-closed gateway & abort hook
├── run_security_audit.py      # Automated penetration & security audit suite
└── README.md                  # System architecture & documentation

⚙️ Understanding the Dual-Terminal Architecture
When evaluating or testing this system, you will notice two terminal windows are utilized. This is not arbitrary; it mirrors enterprise-grade Client-Server decoupling:

Terminal 1 (The Secure Gateway Daemon):

Runs the FastAPI interceptor proxy (proxy_server.py).

Acts as the immutable gatekeeper sitting directly in front of the lab hardware, continuously listening for inbound requests under a strict default-deny policy.

Terminal 2 (The Automated Audit Client):

Runs the security audit suite (run_security_audit.py).

Simulates an external client (or autonomous agent) attempting to push valid commands, violate safety policies, execute replay attacks, or trigger emergency hardware aborts.

🚀 Quick Start & Verification Guide
1. Install Dependencies
Ensure you have Python installed, activate your virtual environment, and run:

Bash
pip install fastapi uvicorn cryptography requests pydantic
2. Start Terminal 1 (The Proxy Server)
Launch the FastAPI fail-closed gateway:

Bash
uvicorn proxy_server:app --reload
(Verify that the server reports running on http://127.0.0.1:8000)

3. Start Terminal 2 (Run Security Audit Suite)
Open a second terminal tab (keeping the server running in the first), activate your virtual environment, and execute the audit runner:

Bash
python run_security_audit.py
This automated suite will sequentially verify:

✅ Test 1: Valid & Authorized Command Dispatch (Status 200)

❌ Test 2: Policy Violation / Volume Threshold Breach (Blocked by Layer 1)

❌ Test 3: Replay Attack / Nonce Reuse (HTTP 403 Forbidden)

🛑 Test 4: Emergency Hardware Kill-Switch (Queue Successfully Flushed)

4. Interactive API Documentation (Swagger UI)
While the proxy server is running in Terminal 1, open your browser and navigate to:

👉 http://127.0.0.1:8000/docs 

Here, reviewers can interactively inspect endpoints and test custom JSON payloads manually using the built-in Swagger interface.