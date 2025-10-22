# Sentinel LLM Guard Frontend

React + Vite single-page app that calls the FastAPI gateway while keeping all sensitive data client-side masked before submission.

## Quickstart

```powershell
npm install
npm run dev
```

Configure the API proxy in `vite.config.ts` if the backend runs on a different host. Paste your JWT bearer token in the header input to authorize requests.

The console shows masked responses, leak alerts, and token vault metadata for authorized users.
