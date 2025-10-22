# DataShield LLM

Prototype full-stack system that protects sensitive data flowing through Large Language Model (LLM) workloads. It masks detected entities, stores reversible mappings securely, proxies the LLM, and inspects egress traffic for leaks.

## Repository Layout

- `backend/` – FastAPI service handling detection, tokenization, vault encryption, LLM proxying, and auditing.
- `frontend/` – React (Vite) SPA for secure prompt submission, leak visibility, and token vault inspection.

## High-Level Flow

1. **Ingress Sanitization** – Requests hit FastAPI (`POST /v1/inference`). The detector masks PII/PHI/business secrets using regex rules and configurable synthesizers.
2. **Token Vault** – Encrypted mappings (Fernet) + metadata persist in SQLite (prototype). Replace with managed Postgres + HSM-backed keys in production.
3. **LLM Proxy** – Sanitized prompt routes to OpenAI (mocked if API key not supplied). Responses run through the same detector for egress enforcement.
4. **Leak Controls** – Policies (`default`, `block-on-leak`) control whether sanitized responses return or leaks block the call.
5. **RBAC & Audit** – JWT scopes (`sanitize:invoke`, `sanitize:view`) enforced; all actions recorded via structured audit logger.
6. **Frontend Console** – React client collects JWTs, submits prompts, displays sanitized output, and renders synthetic token previews for authorized users.

## Getting Started

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
$env:TOKEN_VAULT_KEY = "<Fernet key>"
uvicorn app.main:app --reload
```

Generate a Fernet key with:
```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The dev server proxies `/api` to `http://localhost:8000`. Paste a valid JWT (HS256, signed with `TOKEN_VAULT_KEY`) in the header bar so the API authorizes calls.

## Extensibility Checklist

- Swap regex detector with Microsoft Presidio analyzers or in-house ML models; retain the same `detect_and_tokenize` contract.
- Move the token vault to cloud KMS and managed database with row-level security; add rotation for `TOKEN_VAULT_KEY`.
- Extend policies (`settings.allowed_policies`) to tune leak posture per tenant or jurisdiction.
- Push audit logs to SIEM (Azure Sentinel, Splunk) by wiring a proper log handler.
- Harden secrets using Azure Key Vault/AWS KMS, adopt mutual TLS, and integrate with organization SSO for JWT issuance.
- Add integration tests covering leak scenarios (pytest + httpx) and frontend Cypress smoke checks.
