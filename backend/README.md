# Sentinel LLM Guard Backend

Prototype FastAPI service that sanitizes prompts, proxies LLM requests, and enforces secure token vault storage.

## Quickstart

1. Create environment variables:
   - `TOKEN_VAULT_KEY` – 32-byte base64 Fernet key (`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`).
   - Optional: `OPENAI_API_KEY` if calling OpenAI.

2. Create virtualenv and install dependencies:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate
   pip install -r requirements.txt
   ```

3. Run development server:
   ```powershell
   uvicorn app.main:app --reload
   ```

4. Hit `POST /v1/inference` with bearer token signed using `TOKEN_VAULT_KEY` (HS256). Payload example:
   ```json
   {
     "session_id": "chat-123",
     "input_text": "Email John Smith at john@example.com",
     "policy": "default"
   }
   ```

5. Retrieve stored secrets (requires `sanitize:view` scope):
   ```powershell
   Invoke-RestMethod -Headers @{Authorization="Bearer <token>"} -Uri http://localhost:8000/v1/secret/1
   ```

## Architecture Notes

- Detection uses regex-based rules with Faker-generated synthetic replacements; replace with Presidio analyzers for production.
- Token vault encrypts mappings with Fernet and stores metadata in SQLite (swap with managed PG + pgcrypto).
- Egress sanitizer checks model output for new leaks and optionally blocks responses when policy is `block-on-leak`.
- Audit logger writes structured logs to `sentinel.audit`; wire to SIEM or append-only store.
