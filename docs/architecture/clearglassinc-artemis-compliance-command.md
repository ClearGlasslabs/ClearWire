# ClearGlassInc Artemis Compliance Command

## System architecture

### Product boundary

ClearGlassInc Artemis Compliance Command is **continuous regulatory evidence infrastructure for Canadian critical enterprises**. It is not a vulnerability scanner and does not claim that proposed regulations are in force. It converts enterprise telemetry into tested controls, findings, remediation work, immutable evidence, executive views, and exportable assurance packages.

The initial regulatory mapping is a versioned legal interpretation, never executable law. Counsel and control owners approve every framework release. The product supports a pre-compliance readiness program for cyber, privacy, AI, and supplier risk without predicting the final content or commencement date of regulations.

| Palantir plane | Precise responsibility                                                                                                        |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Gotham         | Permission-aware investigations, incidents, entity tracking, relationship analysis, and operational case views                |
| Foundry        | Governed ingestion, transforms, lineage, Ontology object types, link types, properties, actions, and operational applications |
| AIP            | Model access, copilots, tool-using workflows, evaluations, prompt and model routing under policy                              |
| Apollo         | Environment-aware delivery, signed releases, health gates, canaries, rollback, and runtime control                            |

Actual product APIs, licensed capabilities, and disconnected deployment options must be validated against the customer's Palantir environment. Integration adapters isolate those details from the domain model.

```text
GitHub  M365  Entra  AWS  Azure  EDR  scanners  ITSM  vendor feeds
   \      |      |     |      |    |      |       |       /
      collector identities -> ingress quarantine -> schema registry
                                      |
                         Foundry batch/stream pipelines
                                      |
          raw evidence -> validated evidence -> Ontology -> search/index
                                                  |
Gotham incident/case views <-> policy query facade <-> AIP tool gateway
                                                  |
React command UI <-> API gateway <-> workflow/control/remediation services
                                      |
                append-only audit + metrics/logs/traces/evals

Apollo promotes one signed bundle: code + schema + control map + policy +
prompt + workflow + model route. It can roll the complete bundle back.
```

### Six engines

1. **CCSPA readiness engine** versions obligations, interpretations, controls, owners, applicability, test procedures, evidence requirements, exceptions, and counsel approval.
2. **Continuous control monitor** collects least-privilege snapshots and events, validates freshness and lineage, runs deterministic tests first, and raises evidence-backed findings.
3. **Supply-chain risk graph** links vendors, products, packages, dependencies, systems, data, contracts, owners, weaknesses, incidents, controls, and remediation.
4. **Incident evidence engine** preserves bitemporal chronology, source artifacts, decisions, containment, approvals, notifications, and reporting deadlines.
5. **AI governance engine** inventories models, datasets, prompts, agents, tools, vendors, purposes, assessments, evaluations, access, and releases.
6. **Executive evidence vault** creates audience-specific, policy-filtered, signed manifests for boards, auditors, insurers, procurement teams, and regulators.

### Runtime topology and failure boundaries

- Separate tenant, coalition, and high-side trust boundaries; separate development, evaluation, staging, and production projects.
- Use an at-least-once event log with tenant/compartment partition keys, idempotency keys, a transactional outbox, schema compatibility checks, quarantine, and dead-letter replay.
- The browser never authorizes. The API gateway validates OIDC identity, device posture, mTLS workload identity, tenant, purpose, mission, compartments, and trace context.
- Services access Foundry and Gotham only through a policy-first ontology facade. Models receive short-lived, scoped tool capabilities, never database credentials.
- Deterministic control tests remain authoritative. AIP may classify, correlate, summarize, or propose; it cannot silently change a control result, close a finding, notify an authority, or deploy a candidate.
- Every exported claim resolves to evidence IDs, source locators, content hashes, collection and validity times, control/evaluator versions, and policy decisions.

### Full-stack components

| Layer           | Production components                                                                                                                                                |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Web             | React/TypeScript command center; readiness heatmap; evidence inspector; supplier graph; incident timeline; AI inventory; approval queue; eval and release dashboards |
| Edge/API        | Envoy or equivalent gateway, BFF, OpenAPI contracts, OIDC/mTLS, request signatures, quotas, idempotency                                                              |
| Python services | evidence ingestion, ontology query, control execution, finding/remediation, incident, package export, feedback, eval, proposal, approval                             |
| Events          | Kafka-compatible durable log, schema registry, outbox relay, replay controller, quarantine and dead-letter topics                                                    |
| Data            | Foundry datasets and lineage, object storage evidence vault, PostgreSQL-compatible workflow state, immutable/WORM audit archive                                      |
| Retrieval       | lexical and semantic indices over authorized projections; citations mandatory; compartment-scoped indexes or pre-filtering                                           |
| AI              | AIP workflows, tool registry, prompt registry, model router, deterministic validators, eval runner                                                                   |
| Governance      | centralized policy decision and enforcement points, KMS/HSM, secrets broker, retention/legal hold, artifact signing                                                  |
| Operations      | OpenTelemetry traces, structured logs, SLO metrics, data quality, policy and eval dashboards, Apollo release rings                                                   |

## Data and ontology

Foundry's Ontology is the shared operational semantic layer. Object types represent governed business concepts; link types express navigable relationships; actions are narrow, validated mutations. Gotham, web applications, control tests, and AIP tools consume the same semantics rather than constructing incompatible graphs.

### Core object types

| Object             | Material properties                                                                          |
| ------------------ | -------------------------------------------------------------------------------------------- |
| `EnterpriseSystem` | owner, service tier, environments, data classes, criticality, recovery objectives            |
| `Asset`            | kind, cloud/account, region, identifiers, configuration state, exposure                      |
| `Identity`         | human/workload, assurance level, privileges, authentication factors, lifecycle               |
| `Control`          | statement, framework references, applicability, test, cadence, owner, version                |
| `ControlTest`      | evaluator version, inputs, expected predicate, result, confidence, execution time            |
| `EvidenceArtifact` | source locator, hashes, collector, valid/transaction time, classification, retention, state  |
| `Finding`          | failed control, severity, likelihood, impact, status, due date, exception, evidence          |
| `Remediation`      | owner, ticket, plan, SLA, approvals, verification test, completion evidence                  |
| `Vendor`           | legal identity, services, sub-processors, data access, contracts, assessments, concentration |
| `SoftwareProduct`  | vendor, version, SBOM, dependencies, systems, vulnerabilities, support state                 |
| `Incident`         | declaration, severity, scope, chronology, decisions, containment, recovery, report state     |
| `AIUseCase`        | purpose, owner, risk tier, affected people, decisions supported, prohibited uses             |
| `ModelArtifact`    | provider, version, card, datasets, evaluations, route, prompt/workflow versions              |
| `EvidencePackage`  | audience, as-of time, manifest hash, included claims/evidence, signer, expiry                |
| `Feedback`         | target version, correction, reason, disposition, outcome, operator confidence                |
| `ChangeProposal`   | typed diff, evidence, eval report, risk, approvers, release and rollback target              |

### Relationships

```text
Vendor -PROVIDES-> SoftwareProduct -DEPENDS_ON-> SoftwareProduct
SoftwareProduct -RUNS_ON-> Asset -SUPPORTS-> EnterpriseSystem
Vendor -CAN_ACCESS-> DataDomain
EnterpriseSystem -SUBJECT_TO-> Control -TESTED_BY-> ControlTest
ControlTest -SUPPORTED_BY-> EvidenceArtifact
ControlTest -RAISES-> Finding -RESOLVED_BY-> Remediation
Incident -AFFECTS-> EnterpriseSystem
Incident -HAS_EVENT-> TimelineEvent -SUPPORTED_BY-> EvidenceArtifact
AIUseCase -USES-> ModelArtifact -TRAINED_OR_GROUNDED_ON-> Dataset
ChangeProposal -MODIFIES-> Prompt|Workflow|Route|ControlMap|Policy
```

Every object and link carries a stable ID, tenant, schema version, valid-from/to, recorded-at, source lineage, confidence, classification, releasability, coalition, compartments, legal basis, retention, owner, and deletion/hold state. Bitemporality preserves both when a condition was true and when Artemis learned it. Contradictory observations coexist; resolution produces another sourced assertion instead of overwriting history.

Confidence is calibrated metadata, not permission and not proof. A claim without resolvable lineage is displayed as unsupported and cannot enter an external evidence package.

### Ontology actions

Actions include `recordEvidence`, `evaluateControl`, `acceptFinding`, `createRemediation`, `verifyRemediation`, `declareIncident`, `appendTimelineEvent`, `submitReportPackage`, `recordFeedback`, and `submitChangeProposal`. Each action validates invariants, calls policy, writes domain state and an outbox event atomically, and appends an immutable decision record. Agents invoke these exact actions through schemas; they do not receive a general write primitive.

### Supply-chain graph analytics

Compute blast radius from vendor to downstream systems and business services while retaining the path used. Risk is a vector, not one unexplained score: inherent impact, access, exploitability, concentration, substitutability, control coverage, evidence freshness, and remediation age. Graph outputs always expose inputs, versioned weights, uncertainty, and missing data.

## AI and agent design

### Copilots

- **Analyst copilot:** retrieves authorized evidence, explains control mappings, correlates findings, drafts sourced assessments, and highlights missing evidence.
- **CISO copilot:** summarizes risk movements, overdue remediation, systemic supplier paths, incidents, and decisions awaiting approval.
- **Incident commander copilot:** builds a sourced chronology, proposes containment options, records decisions, and prepares—not sends—report packages.
- **Control owner copilot:** explains failures, proposes tickets and compensating controls, and schedules verification.
- **AI governance copilot:** inventories AI use, detects unassessed changes, compares evals, and prepares model/prompt approval packets.

### Deterministic multi-agent graph

```text
RECEIVED -> POLICY_FILTERED -> NORMALIZED -> TRIAGED
    -> [ENRICHED, CORRELATED] -> CONTROL_EVALUATED -> HUMAN_REVIEW
    -> FINDING_ACCEPTED -> REMEDIATION_OPENED -> VERIFIED -> CLOSED
                                           \-> EXCEPTION_REVIEW
```

The workflow engine, not the model, owns state. Specialist workers return typed candidates:

- triage classifies event/control relevance and urgency;
- enrichment resolves authorized entity attributes and source reliability;
- correlation proposes graph links with evidence and confidence;
- summarization creates citation-complete deltas, never unsourced narratives;
- recommendation generates options, trade-offs, assumptions, and abstention reasons;
- package preparation resolves every assertion to immutable evidence.

Each tool call has a JSON schema, timeout, cost ceiling, data classification limit, idempotency semantics, and required approval class. Read tools are policy-filtered. Draft tools create non-executable artifacts. Consequential tools require a fresh authorization decision and two-person approval. The model cannot grant itself tools, broaden purpose, change mission goals, or approve its own output.

### Model routing

Route using data classification, task type, context size, measured quality, latency budget, residency, availability, and cost ceiling. Sensitive workloads use approved in-boundary models. Deterministic rules handle arithmetic, policy, transitions, and control predicates. The fallback ladder can move only to an equally authorized model; otherwise it abstains. Store route decision, candidate set, policy decision, model/version, prompt hash, token counts, latency, citations, and output hash.

## Self-improvement loop

Artemis improves behavior, never goals or authority.

```text
operator edit / disposition / outcome / telemetry / drift alert
      -> immutable learning event -> privacy and policy filter
      -> labeled eval candidate -> reviewer adjudication
      -> frozen, versioned evaluation set
      -> candidate prompt/workflow/heuristic/route generated offline
      -> replay + adversarial + policy + latency evaluations
      -> proposal packet and semantic diff
      -> risk/model/control owners approve
      -> Apollo shadow -> 5% canary -> 25% -> production
      -> continuous guard metrics -> automatic rollback or freeze
```

### Signals and labels

Capture accepted/rejected recommendations, exact operator edits, reason codes, false-positive and false-negative discoveries, alert disposition, ticket completion, reopened findings, incident outcomes, retrieval failures, citation defects, latency, tool errors, overrides, and trust ratings. Do not interpret silence or click behavior as truth. High-impact labels require adjudication, and training views exclude data outside purpose, consent, retention, and compartment constraints.

### Candidate generation and evaluation

Candidate generators may propose:

- prompt wording or few-shot example changes;
- workflow ordering, retry, abstention, or escalation changes;
- deterministic threshold or feature-weight changes;
- retrieval ranking and chunking changes;
- model routing changes among already approved models.

They may not alter objectives, permissions, approval thresholds, retention, classification, safety policy, or the definition of success. Evaluation datasets are frozen, hashed, leakage-checked, time-sliced, compartment-safe, and stratified by sector/control/severity. Required suites cover golden cases, recent failures, counterfactuals, prompt injection, cross-compartment exfiltration, tool misuse, citation faithfulness, unavailable dependencies, and rollback compatibility.

Promotion requires no policy violation, no critical-slice regression, two distinct human approvals, signed artifacts, and an explicit rollback target. Aggregate improvement cannot hide a regression in severe incidents, protected groups, a coalition boundary, or a rare critical control. The initial 5% canary is assignment-stable and excludes highest-impact actions. Automatic rollback triggers include policy violation, audit gap, material precision/recall regression, false-negative increase, error-budget breach, or operator emergency stop.

### Metrics

| Dimension  | Measures                                                                                               |
| ---------- | ------------------------------------------------------------------------------------------------------ |
| Quality    | precision, recall, false-negative rate, calibration error, citation precision/coverage                 |
| Operations | p50/p95/p99 latency, freshness, queue lag, tool success, abstention, availability                      |
| Human      | acceptance with outcome, correction distance, override reason, time-to-decision, calibrated trust      |
| Compliance | control coverage, evidence freshness, mean age of findings, verification success, package completeness |
| Mission    | time-to-triage, containment and recovery time, prevented recurrence, decision usefulness               |
| Safety     | policy violations, cross-boundary tests, unsupported claims, unapproved actions, rollback time         |

## Full-stack implementation

### API surface

```text
POST /v1/evidence:ingest                 collector-only, idempotent
POST /v1/controls/{id}:evaluate          deterministic evaluator
GET  /v1/findings                       policy-filtered cursor page
POST /v1/findings/{id}:accept            human approval
POST /v1/remediations                    draft or approved command
POST /v1/incidents/{id}/timeline         append-only event
POST /v1/packages:prepare                creates draft manifest
POST /v1/packages/{id}:approve-export    two-person control
POST /v1/feedback                        typed learning signal
POST /v1/proposals                       offline candidate only
POST /v1/proposals/{id}:approve          eligible human only
POST /v1/releases/{id}:promote           Apollo service identity only
```

Commands carry `Idempotency-Key`, signed mission context, expected resource version, trace ID, reason, and client timestamp. Responses include resource version, policy obligations, evidence lineage, and audit event ID. Optimistic concurrency prevents an approval from applying to a changed package.

### Event contracts

Topics use versioned envelopes: `evidence.observed.v1`, `control.evaluated.v1`, `finding.opened.v1`, `remediation.verified.v1`, `incident.timeline-appended.v1`, `feedback.recorded.v1`, `candidate.evaluated.v1`, `approval.decided.v1`, and `release.changed.v1`.

```json
{
  "event_id": "evt_01J...",
  "event_type": "control.evaluated.v1",
  "occurred_at": "2026-08-10T12:05:41Z",
  "recorded_at": "2026-08-10T12:05:42Z",
  "tenant_id": "tenant_01J...",
  "partition_key": "tenant_01J...:CAN-ENERGY",
  "classification": 2,
  "compartments": ["CAN-ENERGY"],
  "trace_id": "tr_01J...",
  "schema_version": 1,
  "producer_version": "control-runner@sha256:...",
  "payload": { "control_id": "IAM-01", "result": "fail" }
}
```

### Representative Python service flow

The executable reference domain types and policy/promotion gates live in `lib/artemis/compliance.py`. A service adapter would keep orchestration explicit:

```python
async def evaluate_control(command: EvaluateControl, context: MissionContext) -> ControlFinding:
    decision = policy.decide(
        "evaluate_control",
        context,
        command.compartments,
        command.classification,
    )
    if not decision.allowed:
        raise Forbidden(decision.reason)

    evidence = await ontology.authorized_evidence(command.control_id, context)
    finding = deterministic_tests[command.control_id].evaluate(evidence)
    async with database.transaction() as transaction:
        await findings.save(finding, expected_version=command.expected_version, transaction=transaction)
        await outbox.append(ControlEvaluated.from_finding(finding, context), transaction=transaction)
        await audit.append(command, decision, finding, transaction=transaction)
    return finding
```

### Ontology-driven retrieval and AIP tool call

```python
@tool("find_control_evidence", side_effect="read", citations_required=True)
async def find_control_evidence(args: EvidenceQuery, context: MissionContext) -> ToolResult:
    decision = policy.decide("read_evidence", context, args.compartments, args.classification)
    if not decision.allowed:
        return ToolResult.denied(decision.reason)
    objects = await foundry_ontology.query(
        object_type="EvidenceArtifact",
        linked_from=("Control", args.control_id, "SUPPORTED_BY"),
        valid_at=args.as_of,
        projection=("evidence_id", "source_locator", "payload_hash", "valid_at", "state"),
        policy_filter=context,
    )
    return ToolResult(data=objects, citations=[item.evidence_id for item in objects])
```

### Frontend contract

Every recommendation card shows classification/releasability, confidence and calibration band, facts versus inferences, exact citations, missing evidence, model/prompt/workflow versions, policy state, and approval requirements. The operator can compare the original draft with edits and must select a reason when rejecting or materially correcting it. High-impact buttons invoke server actions; the UI never turns a draft into execution locally.

### Deployment and SRE

Apollo release manifests pin OCI digests, SBOMs, signatures, database/ontology compatibility, policy bundle hash, control-map hash, prompt/workflow hashes, model routes, and eval report. Promotion is `development -> offline evaluation -> shadow -> 5% -> 25% -> production`. Expand/contract migrations are backward compatible across one rollback window. Break-glass access is time-limited, two-person approved, recorded, and reviewed.

Service SLOs include 99.95% policy facade availability, zero accepted cross-compartment reads, complete audit linkage for all decisions, bounded evidence freshness by control, and a tested rollback recovery objective. Run restore drills, partition replay, collector revocation, model-provider outage, poisoned evidence, prompt injection, and coalition-boundary exercises.

## Security and governance

- **Need to know:** RBAC grants job function; ABAC evaluates tenant, mission, purpose, coalition, compartment, classification, releasability, device, time, and resource state.
- **Fine-grained enforcement:** row/entity filters constrain objects, column masks remove properties, link traversal re-authorizes each hop, and search/vector retrieval applies filters before ranking.
- **Coalition separation:** separate encryption domains and indexes where warranted; explicit releasability markings; no inference from counts, embeddings, cache keys, logs, or error messages across boundaries.
- **Zero trust:** workload mTLS, short-lived identities, egress allowlists, sandboxed tools, signed inputs, no ambient credentials, per-tool capabilities, and deny-by-default network policy.
- **Provenance:** content-addressed artifacts, signed collection manifests, bitemporal lineage, evaluator and behavior versions, hash-linked audit events, WORM replication, and legal holds.
- **Model governance:** approved-model registry, model cards, data residency and classification limits, slice evals, red-team results, expiry/review dates, and emergency disable.
- **Prompt/workflow governance:** semantic diffs, owner, rationale, eval hash, approvers, release, observation window, and rollback target. Production runtime cannot write its own registry.
- **Policy as code:** versioned decision bundles, unit and boundary tests, four-eyes review, signed promotion, shadow decisions before enforcement, and fail-closed behavior for sensitive actions.
- **Privacy:** purpose limitation, minimization, field tokenization, retention enforcement, subject/counsel workflows, and exclusion of disallowed feedback from learning datasets.

## Code examples

### Policy and evidence invariants

```python
decision = CompliancePolicy().decide(
    action="export_regulatory_package",
    context=mission_context,
    resource_compartments=frozenset({"CAN-ENERGY"}),
    resource_classification=2,
    approval_ids=("control-owner", "legal-owner"),
)
if not decision.allowed:
    raise PermissionError(decision.reason)
```

### Safe promotion

```python
eligible, failures = PromotionPolicy().evaluate(candidate, incumbent_metrics)
if not eligible:
    await proposal_store.block(candidate.candidate_id, failures)
else:
    await apollo_release_service.stage_signed_canary(candidate.candidate_id, traffic_percent=5)
```

### SQL learning view

```sql
create view governed_feedback_examples as
select
  f.feedback_id,
  f.target_artifact_id,
  f.target_version,
  f.reason_code,
  f.operator_correction,
  o.outcome_label,
  f.compartments,
  f.recorded_at
from feedback f
join mission_outcome o on o.case_id = f.case_id
where f.adjudication_status = 'accepted'
  and f.learning_use_allowed = true
  and f.retention_expires_at > current_timestamp;
```

The eval builder additionally intersects the executing service's compartments and purpose with every row. A SQL view alone is not the security boundary.

## Scenario walkthrough

At 02:14:03 UTC an authorized EDR connector observes encryption-like behavior on a billing server used by an energy operator. It signs the envelope and sends `evidence.observed.v1`. Ingress verifies the collector identity, schema, tenant, compartment, clock tolerance, and content hash. The raw artifact enters quarantine; a Foundry pipeline normalizes it without destroying the original and links it to the asset, enterprise system, software, vendor, and applicable incident controls.

At 02:14:05 the workflow policy-filters the event. The triage worker labels it probable ransomware behavior with calibrated confidence, but a deterministic rule sets severity from asset criticality and observed impact. Enrichment queries only authorized Gotham and ontology projections. Correlation finds a recent privileged-login observation and an overdue endpoint-isolation finding; each graph edge cites evidence. The summarizer produces a chronology whose every sentence resolves to an artifact.

At 02:14:08 the incident copilot proposes three containment options, their expected service impact, assumptions, and missing facts. It prepares an isolation action package but cannot execute it. The commander sees source timestamps, classification, blast-radius paths, uncertainty, and the control versions. A second authorized operator confirms. Policy re-evaluates identity, device, purpose, current evidence version, compartments, and two distinct approvals before the execution adapter receives a short-lived capability.

The commander rejects the proposed customer-impact statement because the affected host is standby, not active. The UI records the exact correction, reason `ASSET_ROLE_STALE`, target prompt/workflow/ontology versions, and eventual outcome. Operations validate the correction, update the source-backed asset state, contain the incident, and record recovery evidence. No live prompt changes.

During the next offline learning cycle, the adjudicated correction becomes an eval example. Drift analysis shows that stale asset roles caused four similar overstatements. A candidate workflow proposes a mandatory freshness check and abstention when role evidence exceeds its TTL. It is replayed against frozen golden, recent-failure, severe-incident, injection, boundary, latency, and tool-failure suites. Precision improves, recall is unchanged, p95 remains within budget, citation coverage is complete, and policy violations remain zero.

The proposal packet contains the typed workflow diff, four source cases, evaluation dataset hash, slice metrics, risk assessment, approvers, and rollback target. The control owner and model-risk owner approve it. Apollo deploys it in shadow, then to a stable 5% cohort. Guard metrics remain healthy through the observation window, so humans authorize staged promotion. If false negatives, audit gaps, policy violations, or latency cross a threshold, Apollo restores the complete prior behavior bundle automatically and freezes further promotion.

Artemis has become better at one bounded behavior—checking asset-role freshness—without changing its mission, authority, policies, approval thresholds, or goals. The correction, proposal, tests, decisions, rollout, outcome, and possible rollback remain reconstructable from immutable records.

## Regulatory implementation notes

Maintain a legal register that distinguishes enacted, in-force, proposed, anticipated, and internal obligations. Each framework mapping records source URL, exact provision, retrieved date, jurisdiction, applicability logic, counsel owner, interpretation, confidence, effective/commencement state, and supersession history. Customer-facing exports render those states prominently. Legislative or threat-landscape assertions must be reverified from authoritative sources at implementation and package-generation time; this architecture does not encode the supplied dates or claims as timeless facts.
