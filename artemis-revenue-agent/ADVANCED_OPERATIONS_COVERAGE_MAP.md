# ClearGlassInc Artemis advanced operations coverage map

## Scope and evidence method

This map audits the runnable Python service in `artemis-revenue-agent` and the Palantir target blueprint in `clearglassinc_artemis_architecture.md`. Claims are based on repository code and deterministic local tests only. No production credentials, customer communications, billing, infrastructure, destructive migrations, external providers, AI models, or live data were used.

## Coverage map

| Operation                            | Owner                                | Trigger                       | Authorization/input                                                 | Duplicate control                                                                      | Timeout/retry/failure                                    | Monitoring/audit                                                     | Retention/recovery                                      | Status                    |
| ------------------------------------ | ------------------------------------ | ----------------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------- | ------------------------- |
| Lead qualification                   | Revenue operations owner             | `POST /v1/qualify`            | Pydantic validation; deployment-edge authorization remains required | Required `Idempotency-Key`, payload conflict rejection, 15-minute bounded local replay | 5-second registry budget; one attempt; HTTP error states | Correlation header, structured completion event, outcome counter     | Local replay expiry; revert route/store changes         | `PARTIAL`                 |
| External lead handoff                | Revenue operations owner             | Eligible qualification        | Consent check plus HTTPS validation                                 | Inherits qualification key; durable receiver dedupe is unverified                      | 5-second network timeout; one attempt; disabled state    | Qualification event records whether handoff is enabled               | No local payload persistence; unset both flag variables | `REQUIRES_OWNER_APPROVAL` |
| Incident evaluation                  | Incident operations owner            | `POST /v1/incidents/evaluate` | Tenant, role, approval, blast-radius and schema policy checks       | Deterministic tenant/signal incident ID                                                | 5-second registry budget; one attempt; escalation state  | Correlation header, structured event, audit receipt, outcome counter | Audit-sink policy; no local persistence                 | `PARTIAL`                 |
| AI/copilot/agent execution           | AI governance owner not yet assigned | None in runnable service      | Blueprint only                                                      | Not implemented                                                                        | Not implemented                                          | Not implemented                                                      | Keep disabled                                           | `BLOCKED_BY_CREDENTIALS`  |
| Live ingestion and Palantir adapters | Platform owner not yet assigned      | None in runnable service      | Blueprint only                                                      | Not implemented                                                                        | Not implemented                                          | Not implemented                                                      | Keep disabled                                           | `BLOCKED_BY_CREDENTIALS`  |

No row is classified `OPTIMIZED`: edge authentication, durable metrics/audit sinks, tested user-facing states, and production recovery exercises are not evidenced.

## Implemented safe improvements

### 1. Centralized typed job registry

- **Current-state evidence:** workflow controls were distributed across `api.py`, `handoff.py`, and `incident.py`; no registry enumerated ownership, trigger, lifecycle, feature flag, timeout, retry, idempotency, retention, audit, and rollback together.
- **Exact gap:** operators and readiness automation had no authoritative inventory and could not distinguish ready work from disabled external side effects.
- **Smallest complete fix:** immutable typed definitions now register lead qualification, external handoff, and incident evaluation. `/readyz` reports registry loading, while `/v1/operations/jobs` exposes non-secret operational metadata only to a configured operator key and returns a no-index policy.
- **Regression tests:** registry completeness, required control fields, readiness, disabled monitoring, authorization denial, no-index headers, and registry serialization.
- **Monitoring/audit:** each registered runnable path emits an outcome event; registry entries declare audit requirements.
- **Rollback:** revert `operations.py` and remove `/readyz` plus `/v1/operations/jobs`; no stored data or migration must be reversed.

### 2. Fail-closed feature flags

- **Current-state evidence:** configuring `ARTEMIS_HANDOFF_WEBHOOK_URL` was sufficient for an eligible qualification to attempt customer-data delivery.
- **Exact gap:** sensitive capabilities lacked a common disabled default and an explicit owner-approval control.
- **Smallest complete fix:** typed flags cover AI, email, billing, live data, blue-team adapters, and external webhooks. Enabling requires both exact lowercase `true` request and owner-approval variables. External handoff now checks this decision before delivery.
- **Regression tests:** default denial, request-without-approval denial, and dual-control enablement.
- **Monitoring/audit:** lead completion events contain the resolved external-handoff state without contact data.
- **Rollback:** unset `ARTEMIS_EXTERNAL_WEBHOOKS_ENABLED` and `ARTEMIS_EXTERNAL_WEBHOOKS_OWNER_APPROVED` for immediate fail-closed rollback; code rollback removes the module and restores the previous call site.

### 3. Correlation, structured outcomes, and duplicate protection

- **Current-state evidence:** API requests did not accept or return correlation IDs; qualification had no duplicate-submission control; workflow-level counters and structured audit events were absent.
- **Exact gap:** retries could repeat an external side effect, and an operator could not connect a request to a workflow outcome.
- **Smallest complete fix:** middleware validates or generates a correlation ID, qualification requires an idempotency key, same-key/same-payload calls replay, conflicts fail, and sensitive values are excluded from structured outcome events. The in-memory store is TTL- and size-bounded.
- **Regression tests:** missing keys, matching replay, payload conflict, correlation propagation, disabled handoff, and readiness behavior.
- **Monitoring/audit:** per-job/outcome counters and JSON completion events are available for an approved collector; in-memory audit events support deterministic tests only.
- **Rollback:** disable external webhooks first, revert middleware/store integration, then remove the helper modules. No persistent records require cleanup.

## Validation record

The final commit records exact commands, output, and exit codes in its change history and pull request. The deterministic project checks are `python -m pytest`, `python -m compileall -q artemis_revenue_agent`, and formatting/lint checks configured for this package.

## Next approval-gated work

1. Replace the monitoring route's bootstrap operator key with the production identity and policy layer before any public deployment.
2. Replace in-process metrics, audit events, and idempotency with approved durable stores after retention, residency, access, and deletion policies are signed off.
3. Connect Foundry, Gotham, AIP, or Apollo only in an approved sandbox with credentials, ontology permissions, connector contracts, and rollback exercises.
