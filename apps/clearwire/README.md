# Clearwire

Clearwire is a lawful, defensive wireless OSINT and telemetry platform for user-owned or explicitly authorized environments.

## Non-negotiable safety boundary

- Passive telemetry only; no packet-content capture.
- No credential interception, cracking, deauthentication, jamming, spoofing, exploitation, or unauthorized access.
- Device identifiers are pseudonymized by default.
- Precise location is disabled unless explicitly enabled inside an authorization scope.
- Every scan requires an authorization scope and creates an audit event.
- Credential-exposure auditing is privacy-preserving and never stores plaintext secrets.

## Stack

- Next.js + React + TypeScript + Tailwind CSS
- FastAPI telemetry API
- PostgreSQL/PostGIS-ready data model
- Redis-ready jobs/cache boundary
- WebSocket/SSE-ready realtime boundary
- OAuth2/OIDC + MFA integration boundary
- Docker Compose local development
- Kubernetes-ready deployment boundary

## Local development

```bash
cd apps/clearwire
cp .env.example .env
cd backend && python -m uvicorn app.main:app --reload --port 8000
cd ../frontend && npm install && npm run dev
```

The included simulator is the default provider, so hardware and API credentials are not required.
