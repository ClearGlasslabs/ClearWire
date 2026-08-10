# ClearGlassInc Artemis Compliance Command

## System architecture

Compliance Command is continuous regulatory evidence infrastructure for Canadian critical enterprises. It converts enterprise telemetry into tested controls, owned findings, remediation work, immutable evidence, and reviewable packages. It is a readiness system, not a representation that a proposed or not-yet-effective obligation is already enforceable. Each framework release records its legal status, source, effective date, reviewer, and version.

```text
GitHub  M365  Azure/AWS  EDR  IAM  scanners  ticketing  vendor feeds
  └──────── signed connectors / streaming gateway / quarantine ───────┘
                 │
        Foundry governed datasets + lineage
                 │
     Foundry Ontology and action types ─── hybrid search
       │          │              │
  control tests  risk graph   incident timeline
       └──────────┼──────────────┘
                  │
     AIP tool router + bounded agent workflows
                  │
 policy decision point ─ approval service ─ immutable audit ledger
                  │
 Gotham operations / React command UI / evidence package exporter
                  │
       Apollo signed release rings and rollback
```

The six product engines share one ontology and authorization path:

1. **CCSPA Readiness Engine** versions obligations, applicability assumptions, controls, gaps, owners, and readiness scenarios.
2. **Continuous Control Monitor** collects freshness-bound evidence and runs deterministic, versioned tests before model interpretation.
3. **Supply-Chain Risk Graph** connects vendors, products, dependencies, systems, owners, findings, tickets, and compensating controls.
4. **Incident Evidence Engine** keeps bitemporal chronology, decisions, containment actions, approvals, source artifacts, and reporting state.
5. **AI Governance Engine** inventories AI use cases, models, datasets, providers, evaluations, access, risks, and approved deployment scope.
6. **Executive Evidence Vault** produces audience-specific, signed manifests for boards, insurers, procurement, auditors, and regulators.

Gotham provides case-centric investigation, entity tracking, link analysis, and operational views. Foundry provides governed ingestion, transforms, Ontology object/action types, lineage, and application logic. AIP hosts copilots, agent workflows, tool definitions, prompt/model registries, and evaluations. Apollo promotes signed application, workflow, policy, prompt, and model-route bundles through isolated environments and provides health-gated rollback. Exact capabilities and APIs must be confirmed against the licensed Palantir environment.

The web application is a React/TypeScript three-pane command surface: portfolios and queues on the left, the selected control/risk/incident graph in the center, and evidence, lineage, action, and approval detail on the right. Every generated claim opens its source artifact. Mobile supports approval and incident review; authoring remains desktop-first. The Python backend owns control state, calculations, policy checks, workflow transitions, and package manifests.

## Data and ontology

Every object has a stable Nano ID, tenant, coalition, compartments, data classification, owner, schema version, valid time, transaction time, confidence, source lineage, retention rule, and legal hold state.

| Object                           | Key properties                                                          | Relationships                                    |
| -------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------ |
| `RegulatoryFramework`            | jurisdiction, legal status, source URL, effective dates, counsel review | contains `Obligation`                            |
| `Obligation`                     | exact text, interpretation, applicability rule, reporting clock         | satisfied by `Control`                           |
| `Control`                        | test version, cadence, owner, tolerance, evidence contract              | protects `System`; yields `ControlResult`        |
| `EvidenceArtifact`               | source ID, content hash, collected/expiry time, connector version       | supports a result or incident event              |
| `Finding`                        | severity, confidence, due date, exception state                         | affects systems/vendors; remediated by tickets   |
| `Vendor` / `Product`             | criticality, service, contract, assurance status                        | supplies software used by systems                |
| `Dependency`                     | package/version/SBOM coordinates                                        | included in products; has vulnerabilities        |
| `Incident` / `IncidentEvent`     | valid and recorded time, impact, containment, decision                  | affects systems; grounded by evidence            |
| `AISystem` / `Model` / `Dataset` | purpose, provider, version, evaluation, access                          | uses data; serves a business process             |
| `EvidencePackage`                | audience, as-of time, scope, manifest hash, signer                      | contains frozen evidence and test results        |
| `Feedback` / `ChangeProposal`    | artifact versions, correction, outcome, eval report                     | improves a prompt, route, heuristic, or workflow |

Contradictory claims coexist. Confidence expresses calibrated uncertainty and never substitutes for provenance. Bitemporal fields preserve what was believed at an earlier reporting deadline. Ontology actions such as `runControlTest`, `recordIncidentEvent`, `acceptFinding`, `approveException`, `recordFeedback`, and `sealEvidencePackage` are the only write tools exposed to agents. This makes human and machine workflows share the same invariants.

Foundry pipelines retain raw source envelopes in append-only storage, validate schemas in quarantine, tokenize sensitive columns, deduplicate by source and content hash, and publish authorized Ontology projections. Retrieval applies tenant, coalition, compartment, purpose, and row/entity filters before lexical or vector search; post-filtering model output is not an authorization boundary.

## AI and agent design

- **Analyst copilot:** explains control failures, retrieves evidence and lineage, and drafts sourced gap analysis.
- **CISO copilot:** summarizes exposure, remediation aging, control trends, and decision points without hiding uncertainty.
- **Incident commander copilot:** maintains chronology, highlights missing evidence, and prepares—not sends—action and reporting packages.
- **Vendor-risk copilot:** traces transitive exposure and drafts assurance requests.
- **AI-governance copilot:** inventories unregistered AI use, checks approved purpose/data/model combinations, and proposes assessments.
- **Executive copilot:** creates audience-specific narratives from sealed evidence only.

The orchestrator is an explicit state machine rather than an unconstrained agent conversation:

```text
RECEIVED -> QUARANTINED -> POLICY_FILTERED -> TRIAGED -> ENRICHED
 -> CORRELATED -> CONTROL_TESTED -> FINDING_PROPOSED -> HUMAN_REVIEW
 -> TICKETED -> RETESTED -> EVIDENCE_SEALED
Any state -> REJECTED | EXPIRED | LEGAL_HOLD
```

Specialists perform triage, schema extraction, entity resolution, graph correlation, evidence-grounded summarization, control-test explanation, and package preparation. Tools are narrow, typed, idempotent Ontology actions. Agents may query, draft, calculate, or request an action. Opening a case, modifying a control, accepting risk, sending a report, contacting a vendor, closing a finding, or deploying a candidate requires a payload-bound human approval. The deterministic executor rechecks authorization and current object version immediately before execution.

The model router chooses only allowlisted models using task type, classification, residency, latency, context size, evaluation tier, and cost. Sensitive prompts receive minimum-necessary projections. Retrieval precedes generation, output must validate against JSON Schema, citations must resolve to accessible evidence IDs, and unsupported conclusions cause abstention.

## Self-improvement loop

```text
traces + edits + dispositions + alert outcomes + mission results
 -> privacy minimization -> version-joined feedback dataset -> failure clusters
 -> bounded candidate -> offline replay/red team -> change proposal
 -> product + security approval -> shadow -> canary -> promote or rollback
```

Each interaction records the dataset snapshot, retrieval set, prompt, workflow, model route, policy decision, tool calls, latency, cost, answer, operator edits, acceptance reason, and delayed outcome. Clicks are weak signals; explicit corrections and verified control/incident outcomes are labels. Free text is minimized and retention is purpose-bound.

Candidates may adjust prompt wording, tool order, thresholds, routing, or heuristics. They cannot alter organizational goals, legal interpretations, approval gates, access policy, source hierarchy, retention, or safety constraints. An evaluation service replays time-split and tenant-separated golden sets and measures precision, recall, unsupported-claim rate, citation validity, confidence calibration, policy compliance, cross-compartment leakage, injection resistance, p95 latency, cost, operator acceptance, remediation time, and false-alert load.

Promotion requires minimum sample size, confidence intervals, no safety regression, bounded latency/cost, and separate product-owner and security/data-steward approvals. High-risk changes run shadow-only until reviewed. Low-risk UI or drafting variants may use deterministic A/B assignment; operational recommendations do not expose operators to unvalidated experiments. Apollo canaries advance from 5% to 25% to production and automatically roll back on leakage, unsupported claims, error budget, drift, or subgroup regression. The signed incumbent remains deployable.

Drift monitors input features, source mix, connector health, evidence freshness, label prevalence, confidence calibration, model/provider behavior, and outcome quality by tenant and language. Every proposal, diff, dataset hash, evaluation, approval, rollout decision, and rollback is appended to a tamper-evident hash chain.

## Full-stack implementation

```http
POST /v1/evidence:ingest                 signed envelope + Idempotency-Key
POST /v1/controls/{id}:test              expected_version, as_of
POST /v1/findings/{id}:create-ticket     payload-bound approval token
POST /v1/incidents/{id}/events           valid_time, evidence_ids
POST /v1/vendors/{id}:analyze-impact     authorized graph depth
POST /v1/ai-systems/{id}:assess          purpose, model, dataset versions
POST /v1/packages:seal                   audience, scope, as_of, signer
POST /v1/feedback                        artifact/version, reason, correction
POST /v1/changes/{id}:approve            expected_version, justification
POST /v1/deployments/{id}:promote        signed Apollo release reference
```

FastAPI services use Pydantic contracts, OIDC workload identity, request-purpose binding, optimistic concurrency, idempotency, transactional outbox, and OpenTelemetry. PostgreSQL-compatible storage owns workflow transactions; Foundry datasets and Ontology are the governed analytical and operational projection. Object storage retains immutable source captures. Kafka-compatible streams use tenant/compartment partition keys and a schema registry. Hybrid OpenSearch/vector retrieval enforces policy before retrieval.

```python
async def handle_evidence_collected(event, uow, policy, control_runner):
    async with uow.idempotent(event.idempotency_key) as tx:
        envelope = await tx.evidence.verify_and_store(event.signed_envelope)
        policy.require("run_control_test", event.actor, envelope.policy_labels)
        control = await tx.controls.lock(envelope.control_id)
        result = control_runner.evaluate(control, [envelope.artifact], event.observed_at)
        await tx.control_results.append(result)
        if not result.passed:
            await tx.outbox.emit("finding.proposed", result.to_event())
        await tx.audit.append(event.actor, "run_control_test", result.audit_view())
```

```sql
SELECT r.control_id, r.passed, r.tested_at, e.artifact_id, e.expires_at
FROM authorized_control_results(:actor_id, :purpose, :as_of) r
LEFT JOIN authorized_evidence(:actor_id, :purpose, :as_of) e
  ON e.artifact_id = ANY(r.evidence_ids)
WHERE r.tenant_id = :tenant_id
  AND r.tested_at <= :as_of
  AND (r.superseded_at IS NULL OR r.superseded_at > :as_of);
```

The reference implementation in `lib/artemis/compliance.py` supplies strict evidence/provenance contracts, freshness-aware control testing, transitive supply-chain impact, incident chronology, tenant/compartment authorization, payload-bound approvals, and deterministic evidence manifests. Production adapters map these domain contracts to licensed Foundry Ontology actions and Gotham cases.

## Security and governance

Identity federation uses phishing-resistant MFA and short-lived workload credentials. ABAC combines tenant, role, purpose, mission, coalition, compartment, geography, classification, legal basis, and time. Field-level projections protect secrets and personal data; entity-level policy prevents graph traversal from becoming a side channel. Break-glass access is time-boxed, dual-approved, alerted, and reviewed.

Services use mutually authenticated identities, egress allowlists, signed images, software bills of materials, isolated connector runtimes, encrypted queues/storage, HSM-backed signing, secret rotation, and default-deny network policy. Connectors cannot invoke models. Models cannot reach arbitrary networks. Tool execution occurs in constrained workers with quotas and action-specific credentials.

Audit records include actor, purpose, policy version/decision ID, input/output hashes, source lineage, artifact versions, approval, and execution result. WORM retention and external timestamping make logs tamper-evident. Prompt, model, workflow, ontology, control, policy, and connector registries are versioned and signed. Legal and compliance owners approve framework interpretations; the platform labels proposed, enacted, in-force, and superseded obligations distinctly.

SLO dashboards trace `connector -> evidence -> policy -> retrieval -> model -> tool -> ontology action -> audit`. They expose ingestion freshness, test coverage, stale evidence, open findings, remediation aging, graph exposure, incident completeness, policy denials, injection blocks, unsupported claims, calibration, p50/p95/p99 latency, cost, feedback coverage, and deployment health without placing raw protected data in telemetry.

## Scenario walkthrough

At 02:14, an endpoint connector reports suspicious encryption behavior on a dispatch server. The signed event enters quarantine; schema, signature, tenant, residency, and replay checks pass. Foundry links the server to its owner, identity service, vendor software, transport process, controls, and current evidence. Gotham opens an analyst-visible event view, not an operational case.

The triage agent retrieves only the authorized projection. It correlates the signal with an identity anomaly and a newly published vendor advisory, labels the advisory as external evidence rather than confirmed exploitation, and assigns calibrated confidence. The graph agent finds two dependent dispatch systems. Deterministic control tests show current backups but stale privileged-access evidence. The incident agent builds a bitemporal chronology and identifies the missing containment approval.

The commander copilot recommends isolating one host, rotating a scoped credential, collecting volatile evidence, and preparing notification analysis. Each sentence cites an accessible artifact; assumptions and unknowns are explicit. Isolation and credential rotation become separate action packages containing target, scope, expiry, rollback, expected object versions, and action hashes. An operator rejects broad credential rotation, narrows it to the affected service account, and approves isolation. The executor hashes the amended payload, requires a new approval, rechecks policy, executes through the authorized tool, and records the result. No agent sends a regulatory report.

After containment, the operator marks the original severity too high because the backup-control evidence was omitted from the first retrieval. The eventual incident outcome confirms limited impact. Feedback is joined to the exact retrieval, prompt, route, workflow, and policy versions. The eval service clusters similar failures and proposes a bounded retrieval-order change: fetch recent compensating-control results before severity synthesis.

The candidate is replayed against time-split incidents, injection tests, and compartment-leakage cases. Precision improves while recall, safety, and latency remain inside gates. Product and security reviewers approve the signed diff. Apollo shadows it, canaries it to 5%, then 25%, and promotes it. Drift monitors stay armed; rollback still points to the previous signed bundle. Artemis improved its evidence ordering, not its mission, authority, policy, or goals.
