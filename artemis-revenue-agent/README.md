# ClearGlass ARTEMIS Revenue Agent

Production-oriented lead qualification, scoring, fixed-scope service routing, and human handoff for ClearGlass Inc. cybersecurity engagements in Ontario.

ARTEMIS is designed to convert inbound interest into structured, reviewable sales opportunities without inventing prices, changing scope, or sending unauthorized communications.

## Revenue workflow

```text
Website / form / NEXUS intake
        |
        v
Validated Ontario lead record
        |
        v
Deterministic qualification + 0-100 score
        |
        v
Single approved service recommendation
        |
        v
CASL consent check + risk escalation
        |
        v
Signed human handoff to ClearGlass operator
        |
        v
Human-approved briefing, assessment, or proposal
```

## Included controls

- Exactly four fixed-scope offerings
- No invented pricing
- Ontario/Canadian location validation
- Lead scoring across budget, authority, timeline, and risk fit
- PHIPA, government, active-incident, regulated-data, and enterprise escalation
- Written-authorization requirement on every engagement
- CASL consent state captured separately from technical qualification
- HTTPS-only handoff webhook, with optional HMAC signing
- No autonomous proposal, contract, booking, or outbound message
- Kimi K3 tracked as an isolated **Assess** candidate, not a production default

## Install

```bash
cd artemis-revenue-agent
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest
```

## Run

```bash
artemis-revenue-agent
```

The default listener is `127.0.0.1:8080`.

```bash
curl http://127.0.0.1:8080/healthz
```

## Qualify a lead

```bash
curl -X POST http://127.0.0.1:8080/v1/qualify \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: sample-qualification-001' \
  -d '{
    "organization_name": "Ontario Sample Manufacturing",
    "contact_name": "Jordan Lee",
    "contact_email": "jordan@example.ca",
    "industry": "Manufacturing",
    "location": "Burlington, Ontario, Canada",
    "employee_count": 45,
    "microsoft_365_users": 38,
    "decision_role": "decision_maker",
    "primary_concern": "microsoft_365_security",
    "timeline": "0-30 days",
    "budget_cad": 7000,
    "regulated_data": false,
    "active_incident": false,
    "consent_to_contact": true
  }'
```

The response contains:

- Qualification summary
- Single recommended offering
- Approved price display or a refusal to quote
- Lead score and band
- Escalation reasons
- CASL contact permission
- Written-authorization flag
- Structured handoff data
- Optional delivery receipt

## Approved service catalog

Copy the example catalog, insert ClearGlass-approved fixed prices and wording, then configure the path:

```bash
cp config/service-catalog.example.json config/service-catalog.production.json
export ARTEMIS_SERVICE_CATALOG="$PWD/config/service-catalog.production.json"
```

ARTEMIS refuses catalogs that do not contain exactly the four expected service identifiers:

1. `security-quick-audit`
2. `m365-windows-hardening-sprint`
3. `phipa-readiness-assessment`
4. `automation-as-a-service`

Do not deploy with placeholder pricing. The built-in fallback deliberately displays `Approved fixed price required` rather than fabricating a number.

## Human handoff

Configure an operator-controlled NEXUS, CRM, or intake endpoint:

```bash
export ARTEMIS_HANDOFF_WEBHOOK_URL="https://nexus.example.ca/api/artemis/leads"
export ARTEMIS_HANDOFF_SECRET="replace-with-a-secret-from-your-secret-manager"
```

Rules:

- Only `hot` and `qualified` leads are eligible for delivery.
- Delivery is blocked when CASL consent is not recorded.
- Non-HTTPS endpoints are rejected, except localhost development.
- Network failure never destroys the qualification result.
- The optional `X-ARTEMIS-Signature-SHA256` header signs the exact JSON body.

## Lead scoring

| Dimension            | Maximum |
| -------------------- | ------: |
| Budget fit           |      25 |
| Decision authority   |      25 |
| Timeline             |      25 |
| Risk and service fit |      25 |
| **Total**            | **100** |

Bands:

- `80-100`: hot
- `60-79`: qualified
- `40-59`: nurture
- `0-39`: disqualify

Scoring ranks commercial readiness. It does not authorize technical work, contact, pricing, or contracting.

## Escalation

Human review is automatically required for:

- Active security incidents
- Government or public-sector entities
- Healthcare, finance, insurance, or other regulated environments
- Organizations above 500 employees
- PHIPA Readiness, Hardening Sprint, and Automation-as-a-Service recommendations

ARTEMIS is not an incident-response service. Active incidents must be routed to an authorized human who decides whether ClearGlass can accept the matter.

## Environment variables

| Variable                                   | Purpose                                                 | Default                    |
| ------------------------------------------ | ------------------------------------------------------- | -------------------------- |
| `ARTEMIS_HOST`                             | Listener host                                           | `127.0.0.1`                |
| `ARTEMIS_PORT`                             | Listener port                                           | `8080`                     |
| `ARTEMIS_SERVICE_CATALOG`                  | Approved four-service catalog                           | Built-in no-price fallback |
| `ARTEMIS_HANDOFF_WEBHOOK_URL`              | NEXUS/CRM handoff endpoint                              | Disabled                   |
| `ARTEMIS_HANDOFF_SECRET`                   | HMAC signing secret                                     | Unsigned                   |
| `ARTEMIS_EXTERNAL_WEBHOOKS_ENABLED`        | Requests external handoff activation; exact `true` only | Disabled                   |
| `ARTEMIS_EXTERNAL_WEBHOOKS_OWNER_APPROVED` | Records explicit owner approval; exact `true` only      | Disabled                   |
| `ARTEMIS_OPERATOR_MONITORING_KEY`          | Authorizes the job inventory route                      | Disabled                   |

Both external-webhook variables are required before delivery can occur. AI, email, billing, live-data, blue-team, and external-webhook capabilities otherwise fail closed.

Operational readiness is available at `/readyz`. The non-secret job inventory is available at `/v1/operations/jobs` only when `ARTEMIS_OPERATOR_MONITORING_KEY` is configured and supplied as `X-Operator-Key`; the response also denies public indexing. Replace this bootstrap control with deployment-edge identity and policy enforcement before production use. See `ADVANCED_OPERATIONS_COVERAGE_MAP.md` for evidence, status, validation, and rollback details.

## Deployment boundary

Recommended production placement:

```text
Internet
  -> WAF / rate limiter
  -> consent-aware website form
  -> ARTEMIS API on private service network
  -> NEXUS / CRM handoff endpoint
  -> human review
```

Add authentication, request throttling, structured logging, retention rules, and a privacy notice at the platform edge. Do not expose the development Uvicorn process directly to the public internet.

## Kimi K3 evaluation

Kimi K3 is recorded in `config/model-radar/kimi-k3.yaml` and documented in `docs/tech-radar/kimi-k3.md`.

Its current policy is:

- Radar status: `assess`
- Production allowed: `false`
- Data ceiling: synthetic or public
- Allowed environment: isolated sandbox and replay harness
- Human approval required for any model-routing change

The deterministic qualification and compliance core does not depend on Kimi K3 or any external language model. That separation prevents model behavior from changing pricing, scope, consent, scoring, or escalation decisions.

## Tests

```bash
pytest
```

The regression suite verifies service routing, PHIPA escalation, Microsoft 365 hardening selection, written authorization, CASL state, and the no-invented-price rule.
