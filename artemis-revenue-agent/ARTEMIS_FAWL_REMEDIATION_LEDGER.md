# ARTEMIS // FAWL remediation ledger

## Executive assessment

This repository contains a large Gumroad Rails/TypeScript application plus focused ClearGlassInc Artemis Python services and architecture documentation. The safe high-value implementation completed here adds the first deterministic FAWL incident-control kernel to the existing revenue agent without claiming unavailable Palantir, SSO, deployment, customer, certification, or production telemetry status.

## Architecture map

- `artemis_revenue_agent.api`: FastAPI boundary for health, revenue qualification, and incident signal evaluation.
- `artemis_revenue_agent.engine`: deterministic Ontario lead qualification, fixed service routing, CASL state, and human handoff gating.
- `artemis_revenue_agent.incident`: DETECT → VALIDATE → CORRELATE → CLASSIFY → CONTAIN → PLAN → AUTHORIZE → EXECUTE → VERIFY → MONITOR → CLOSE/ROLLBACK/ESCALATE control kernel.
- `artemis_revenue_agent.handoff`: optional HTTPS/HMAC handoff delivery to operator-controlled systems.
- `clearglassinc_artemis_architecture.md`: Palantir Gotham/Foundry/AIP/Apollo target architecture blueprint.

## Threat model

Primary risks are unauthorized autonomous action, cross-tenant data exposure, fabricated AI conclusions, evidence tampering, excessive blast radius, secret leakage, deployment rollback failure, and commercial claims exceeding operational reality. The implemented control kernel treats AI output as untrusted, requires evidence, enforces tenant matching, applies role and human-approval checks, emits deterministic action scopes, and creates tamper-evident audit receipts.

## Ranked findings

| Priority | Finding                                                                            | Evidence                                          | Risk                                         | Commercial impact                    | Effort | Dependencies                         | Acceptance criteria                                                                 |
| -------- | ---------------------------------------------------------------------------------- | ------------------------------------------------- | -------------------------------------------- | ------------------------------------ | ------ | ------------------------------------ | ----------------------------------------------------------------------------------- |
| P0       | Autonomous incident lifecycle was documented but not executable                    | No incident evaluator existed before this change  | Unsafe demos or unverifiable recovery claims | Blocks credible paid pilots          | M      | None                                 | Deterministic lifecycle API and tests for approval denial and approved path         |
| P0       | Human authorization controls needed code-level enforcement                         | Existing revenue workflow had handoff gating only | AI/action overreach                          | Required for enterprise trust        | M      | Identity integration later           | Policy context denies high-impact actions without approval and role                 |
| P1       | Tamper-evident evidence receipts were absent                                       | No audit receipt primitive                        | Evidence disputes                            | Weakens regulated sales motion       | S      | Secret manager later                 | Stable HMAC receipt over incident, actor, denials, and evidence                     |
| P1       | Dependency/blast-radius graph was not represented                                  | No incident dependency response model             | Unsafe containment scope                     | Slower recovery and buyer skepticism | S      | CMDB/Foundry later                   | Response includes correlated assets, dependencies, and blast-radius ceiling denials |
| P2       | Live dashboard, SSO, SBOM, signed artifacts, canary rollback remain blueprint-only | Documentation only                                | Operational gaps                             | Pilot readiness incomplete           | L      | Deployment platform, IdP, CI secrets | CI artifacts signed, SBOM generated, dashboard backed by real metrics               |
| P3       | Palantir integrations are architectural placeholders                               | No Gotham/Foundry/AIP/Apollo SDK wiring           | Integration drift                            | Must be disclosed in sales           | L      | Palantir environment                 | Connector contracts tested against approved tenant sandbox                          |

## Recovery-control matrix

| Lifecycle stage         | Implemented control                                                         |
| ----------------------- | --------------------------------------------------------------------------- |
| Detect                  | `SignalInput` requires source, tenant, severity, and evidence               |
| Validate                | Pydantic bounds validate evidence, scope, confidence, retries, and timeouts |
| Correlate               | Assets and dependencies are normalized into a dependency graph              |
| Classify                | Deterministic keyword/severity classifier returns confidence                |
| Contain                 | High-impact actions are containment-first and scoped                        |
| Plan                    | `RecoveryAction` includes idempotency key, timeout, retries, rollback       |
| Authorize               | Tenant, role, kill switch, approval, and blast-radius policy checks         |
| Execute                 | Only represented when policy denials are empty                              |
| Verify                  | Lifecycle includes verification after authorized execution                  |
| Monitor                 | Lifecycle includes monitoring before close                                  |
| Close/Rollback/Escalate | Denials escalate; rollback strategy is mandatory per action                 |

## Deployment guide

1. Build an approved service catalog from `config/service-catalog.example.json` and set `ARTEMIS_SERVICE_CATALOG`.
2. Set `ARTEMIS_HANDOFF_WEBHOOK_URL` to an HTTPS operator endpoint and store `ARTEMIS_HANDOFF_SECRET` in a secret manager.
3. Run `pip install -e '.[test]'` in `artemis-revenue-agent`.
4. Run `python -m pytest tests`.
5. Start with `artemis-revenue-agent` behind WAF/API gateway, mTLS/OIDC, request limits, and centralized logs.
6. Treat `/v1/incidents/evaluate` as a decision API only until execution adapters have independent verification and rollback tests.

## Commercial pilot plan

- Pilot package: read-only signal intake, deterministic incident classification, recovery recommendation packages, and human-approved handoff.
- Value metrics: mean time to classify, false-positive reduction, approval latency, blast-radius size, rollback readiness, and operator trust score.
- Boundaries: no autonomous remediation, no unrestricted secret access, no production Palantir integration claim until validated in customer environment.

## Unresolved backlog

- Integrate real identity provider, tenant registry, and policy-as-code engine.
- Replace local receipt secret with KMS/HSM-backed signing and immutable log storage.
- Add event bus, dead-letter queue, replay harness, and reconciliation worker.
- Add OpenTelemetry traces/metrics and dashboard backed by real runtime data.
- Add SBOM generation, artifact signing, canary deployment, and rollback pipeline.
- Add chaos drills, disaster-recovery exercises, and recovery-quality scoring.
