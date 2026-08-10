# ClearGlassInc Artemis: strategic resilience intelligence architecture

## Purpose and operating boundary

ClearGlassInc Artemis is a human-governed, coalition-aware platform for converting lawful public Arctic and NATO signals into auditable commercial hypotheses. It is not an operational-intelligence collection system: it excludes classified or restricted material, personal targeting, automated outreach, bid submission, capital allocation, and claims of institutional endorsement. Every externally consequential action requires human approval.

The design uses **Gotham** for authorized operational analysis and entity-centric investigations, **Foundry** for governed integration, ontology, pipelines, and applications, **AIP** for model-backed workflows and evaluations, and **Apollo** for controlled delivery across environments. Product capabilities must be confirmed against the licensed Palantir environment before implementation; this blueprint describes integration contracts rather than claiming product entitlements.

## System architecture

```text
Public sources -> acquisition quarantine -> validation/deduplication -> Foundry datasets
                                                               |-> ontology + lineage
Analyst UI <-> API/BFF <-> policy decision point <-> workflow/event services
    |                              |                |-> search/geospatial index
    |                              |                |-> AIP model/tool router
    |                              |                |-> eval and proposal service
    +-> Gotham authorized views <--+                +-> immutable audit ledger
                                                         |
                                              Apollo signed promotion/rollback
```

| Plane                            | Responsibilities                                                                                                        | Failure boundary                                                         |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| React/TypeScript web application | Signal inbox, evidence viewer, graph/map, opportunity workbench, scenario lab, approval queue, eval dashboard           | Never trusts browser authorization; sensitive fields are server-filtered |
| Python API and services          | Typed commands, ontology projection, scoring, workflow state, idempotency, exports                                      | Stateless replicas; transactional outbox prevents dual writes            |
| Event plane                      | `source.observed`, `signal.validated`, `opportunity.scored`, `feedback.recorded`, `change.proposed`, `approval.decided` | At-least-once delivery, schema registry, tenant/compartment partitioning |
| Foundry data plane               | Source adapters, quarantine, transforms, quality checks, ontology-backed operational data                               | Raw evidence is append-only; derived records retain input lineage        |
| Gotham                           | Authorized entity tracking, cases, link analysis, geospatial/temporal investigation                                     | No data crosses coalition compartments through correlation               |
| AIP                              | Copilots, tool-using workflows, model routing, prompt registry, evals                                                   | Models receive minimum necessary projections, not unrestricted datasets  |
| Apollo                           | Signed artifacts, environment rings, health gates, rollback, disconnected/runtime control                               | Candidate release cannot promote itself                                  |
| Governance                       | Identity federation, policy-as-code, KMS, retention, immutable audit, legal review                                      | Deny by default and fail closed for sensitive actions                    |

### Deployment topology

Use separate development, evaluation, staging, and production projects plus coalition-specific runtime boundaries. Deploy containers and configuration as immutable, signed artifacts. Promotion follows `development -> offline evaluation -> shadow -> 5% canary -> 25% -> production`; each ring has latency, quality, policy-denial, and error-budget gates. Apollo performs health-controlled rollout and one-click rollback to the last signed prompt, workflow, model-route, ontology, and service bundle. Data migrations are expand/contract and backward compatible.

No runtime depends on one cloud: package OCI images, use object-storage and PostgreSQL-compatible abstractions, OpenTelemetry, OpenAPI, and portable event schemas. Keep provider-specific adapters behind capability interfaces. Operate without foreign hardware inventory; edge collection is partner-owned and store-and-forward.

## Data and ontology

### Core objects

| Object             | Material properties                                                                             | Relationships                               |
| ------------------ | ----------------------------------------------------------------------------------------------- | ------------------------------------------- |
| `Source`           | publisher, URL, source type, authority tier, independence                                       | publishes `EvidenceArtifact`                |
| `EvidenceArtifact` | exact passage, content hash, published/observed time, retrieval method, classification, lineage | supports or contradicts `Claim`             |
| `Claim`            | fact/interpretation/inference/assumption/unknown, confidence, valid time, transaction time      | describes `Entity` or `Milestone`           |
| `Signal`           | type, lifecycle, domain, geography, urgency, reliability, review date                           | grounded by evidence; affects opportunities |
| `Entity`           | organization, program, asset class, geography, standard, vendor; stable ID and aliases          | participates in milestones and contracts    |
| `Milestone`        | policy, budget, tender, contract, pilot, deployment; amount and currency when public            | owned/funded/delivered by entities          |
| `Opportunity`      | buyer/user/pain, alternative, data, integrations, procurement, cost/revenue hypotheses          | derived from signals; maps to capabilities  |
| `Assessment`       | revenue-independence dimensions, bear-case variables, priority dimensions, assumptions          | versions an opportunity judgment            |
| `Case`             | mission purpose, compartment, owner, status, retention                                          | contains signals, hypotheses, tasks         |
| `Feedback`         | correction, disposition, alert outcome, reason code, mission result                             | evaluates a specific artifact version       |
| `ChangeProposal`   | diff, evidence set, eval report, risk, approvals, rollout and rollback target                   | proposes a versioned artifact               |
| `Approval`         | actor, role, decision, timestamp, justification                                                 | gates actions and promotions                |

Every object carries `object_id`, `schema_version`, `valid_from/to`, `recorded_at`, `confidence`, `provenance`, `policy_labels`, `coalition`, `compartments`, `owner`, and `retention_policy`. Confidence is a calibrated judgment, never a replacement for provenance. Bitemporal state distinguishes when a fact was true from when Artemis learned it. Contradictory claims coexist and are resolved explicitly rather than overwritten.

### Normalized signal contract

The reference Python model in `lib/artemis/intelligence.py` enforces timezone-aware publication/observation dates, HTTPS attribution, an exact evidence excerpt, lifecycle, 0–5 scoring, a next validation action, owner, and review date. Evidence hashes support deterministic deduplication without erasing the higher-confidence observation.

Foundry ontology actions are narrow verbs such as `validateSignal`, `linkEvidence`, `scoreOpportunity`, `recordFeedback`, and `submitChangeProposal`. Each action checks policy, validates invariants, creates an audit event, and emits an outbox record. Gotham and the web UI consume the same permission-filtered ontology projection; agents receive tool schemas generated from those actions, so human and machine workflows share semantics.

## AI and agent design

### Copilots

- **Analyst copilot:** searches authorized evidence, explains lineage, compares hypotheses, drafts a sourced brief, and flags missing fields.
- **Growth copilot:** maps validated signals to buyers, procurement paths, 90-day paid experiments, three independent markets, and reusable IP.
- **Resilience copilot:** runs trade-rupture and concentration tests and proposes reversible mitigations.
- **Executive copilot:** composes the prescribed intelligence brief while preserving fact/inference/unknown labels.
- **Commander view:** when legitimately deployed for a mission context, summarizes authorized cases; it cannot issue orders or perform consequential actions.

### Workflow graph

```text
OBSERVED -> QUARANTINED -> EXTRACTED -> CORROBORATION_REQUIRED
  -> HUMAN_VALIDATED -> SCORED -> OPPORTUNITY_DRAFTED -> HUMAN_APPROVED
  -> MONITORED
Any state -> REJECTED | EXPIRED | LEGAL_HOLD
```

Specialized agents execute bounded nodes:

1. **Triage** rejects unsupported or prohibited material and classifies source/domain.
2. **Extraction** produces entities, dates, amounts, claims, and exact passage offsets.
3. **Corroboration** discovers independent primary sources but never upgrades a search snippet into evidence.
4. **Correlation** links only authorized entities and presents competing hypotheses.
5. **Opportunity** identifies buyer, signer, budget mechanism, proof, partner, 90-day offer, recurrence, and cycle-reversal value.
6. **Scenario** calculates transparent revenue independence, bear exposure, priority, and stranded assets.
7. **Briefing** renders claims with citations and evidence status.

Agents may query, draft, score, prepare an unsigned product, or request case creation. They may not contact external parties, publish, open an operational case, submit bids, allocate funds, change goals, activate paid data, or deploy an improvement. Those operations create an approval task; the deterministic executor rechecks policy after approval to prevent time-of-check/time-of-use errors.

Model routing considers task, data sensitivity, residency, latency budget, context length, cost, and an allowlisted model capability. Retrieval comes before generation. Output must satisfy JSON Schema, cite evidence IDs, and abstain when support is inadequate. High-impact recommendations require a second independent model critique plus a human decision; model agreement is not independent-source corroboration.

## Self-improvement loop

```text
Interactions/outcomes -> privacy filtering -> labeled feedback dataset -> failure clusters
 -> candidate prompt/workflow/router/heuristic -> offline replay + red-team suite
 -> change proposal -> two-person approval -> shadow -> canary -> promote/rollback
```

1. Capture query/tool traces, retrieved evidence IDs, artifact versions, latency/cost, operator edits, accept/reject reason, alert outcome, and delayed mission/commercial result. Never treat clicks alone as truth.
2. Join feedback to the exact prompt, workflow, model route, ontology, policy, and dataset snapshot. Remove unnecessary free text and enforce retention.
3. Detect drift in input distributions, confidence calibration, source mix, tool failures, precision/recall, abstention, latency, cost, and acceptance by compartment and language.
4. Cluster failures and draft one bounded candidate. Candidates can change instructions, tool ordering, thresholds, or routing, but cannot change mission, approval requirements, source hierarchy, access policy, or safety boundaries.
5. Replay a time-split, source-separated golden set. Test evidence attribution, unsupported-claim rate, precision, recall, calibration, latency, cost, policy compliance, cross-compartment leakage, prompt injection, and adversarial sources.
6. Require no safety regression, statistical confidence, minimum sample size, and two distinct approvals (product owner and security/data steward). High-risk changes remain shadow-only until an explicit review.
7. Canary with deterministic assignment, predeclared success metrics, and automatic rollback on safety breach, elevated unsupported claims, latency/error budget, or material subgroup regression.
8. Seal the decision, diff, evaluation data hashes, approvals, rollout, and outcome into a hash-chained audit event. Retain the incumbent and rollback procedure.

A/B tests apply only to presentation and low-risk analytical assistance. Operationally significant recommendations use shadow evaluation, not experiments that expose operators to unvalidated behavior. Optimization is constrained multi-objective: improve attributable precision/recall and operator value subject to hard policy/safety limits and bounded latency/cost.

The executable reference in `lib/artemis/evolution.py` binds every feedback label to the exact prompt, workflow, route, ontology, policy, and dataset versions. Its release controller rejects protected configuration changes, requires distinct product and security approvers, enforces ordered shadow/canary promotion, blocks candidates with policy violations or cross-compartment leakage, and preserves rollback as a transition from every release stage. Deterministic hashing gives reproducible canary cohorts and evaluation dataset manifests without allowing the candidate to assign or promote itself.

## Full-stack implementation

### Service contracts

```http
POST /v1/signals:ingest          Idempotency-Key, signed source envelope
POST /v1/signals/{id}:validate   expected_version, disposition, evidence_ids
POST /v1/opportunities:score     signal_ids, explicit assumptions
POST /v1/briefs:draft            case_id, as_of, required_sections
POST /v1/feedback                artifact/version, correction, reason, outcome
POST /v1/changes/{id}:approve    expected_version, decision, justification
POST /v1/deployments/{id}:promote approval token; Apollo adapter executes
```

All writes use OIDC workload identity, purpose binding, idempotency, optimistic concurrency, policy evaluation, and transactional outbox. Reads return `decision_id` and filtered-field metadata. A PostgreSQL-compatible store owns workflow transactions; Foundry datasets and ontology are the governed analytical/operational projection. Object storage holds immutable source captures. Search uses hybrid lexical/vector retrieval with compartment filters applied before retrieval. The stream uses partition keys that prevent coalition mixing.

### Event handler pattern

```python
async def handle_signal_validated(event, unit_of_work, policy, scorer):
    async with unit_of_work(event.idempotency_key) as uow:
        signal = await uow.signals.lock(event.signal_id)
        policy.require("score_opportunity", event.actor, signal.policy_labels)
        assessment = scorer.score(signal, assumptions=event.assumptions)
        await uow.assessments.append(assessment)
        await uow.outbox.emit("opportunity.scored", assessment.to_event())
        await uow.audit.append(event.actor, "score_opportunity", assessment.audit_view())
```

### Policy-as-code shape

```rego
package artemis.action
default allow := false
allow if {
  input.identity.authenticated
  input.purpose in input.identity.allowed_purposes
  every label in input.resource.compartments { label in input.identity.compartments }
  not input.resource.coalition_release_to[_] == input.identity.coalition
  not input.action in {"publish", "outreach", "deploy"}
}
allow if {
  input.action in {"publish", "outreach", "deploy"}
  input.approval.valid
  input.approval.action_hash == input.action_hash
  input.approval.approver != input.identity.subject
}
```

Production policy must correct the illustrative coalition-release condition to the local label semantics and pass deny/allow unit tests before activation. Policy decisions are cached only within a short, label-aware TTL and are always rechecked on write.

### Scoring and eval implementation

`RevenueIndependence.score()` sums the nine named 0–5 dimensions and divides by 45. `BearCase.exposure()` multiplies four documented 0–5 variables and also returns a normalized value. Scores remain decision aids: no opportunity enters pipeline without buyer, budget/procurement, eligibility, timing, delivery fit, and human validation. `PromotionGate` requires precision, recall, p95 latency, operator acceptance, two approvals, no quality regression, and a 10% latency budget. Real deployment adds confidence intervals, sample-size gates, leakage tests, and signed evaluation manifests.

### Operator application

The workbench uses a three-pane layout: queue, evidence/graph, and assessment. Every generated sentence has a status chip (`verified fact`, `source-backed interpretation`, `analyst inference`, `assumption`, `unknown`, `recommendation`, `decision trigger`, `validation requirement`) and opens its source passage. Users can compare temporal snapshots, inspect transformation lineage, correct entities, run bear scenarios, and approve/reject with a reason. Accessibility, keyboard navigation, low-bandwidth mode, localization, mobile incident review, and disconnected read-only bundles are release criteria.

### Observability and SLOs

Trace `request -> policy -> retrieval -> model -> tool -> ontology action -> audit` with correlation IDs but never raw secrets in telemetry. Dashboards cover ingestion freshness, source failures, duplicate rate, lineage completeness, unsupported claims, confidence calibration, tool success, policy denies, prompt-injection blocks, p50/p95/p99 latency, tokens/cost, feedback coverage, acceptance by use case, buyer validation, paid pilots, recurring revenue, market/geography concentration, bear exposure, and stranded assets.

Initial SLOs: 99.9% API availability, 99% priority-source ingestion within 15 minutes of observation, 100% generated claims linked to evidence or labeled inference, zero cross-compartment disclosures, and rollback initiation within five minutes of a breached promotion gate.

## Security and governance

- Federated MFA and workload identity; short-lived credentials; no shared service users.
- Relationship-based need-to-know plus row, column, object, action, purpose, geography, coalition, and compartment policies.
- Pre-retrieval authorization, post-retrieval minimization, output DLP, and action-time reauthorization.
- Encryption in transit/at rest, tenant-scoped keys, rotation, HSM-backed signing, egress allowlists, malware scanning, and source quarantine.
- Sandboxed, network-denied code execution; allowlisted parameterized tools; quotas, timeouts, and circuit breakers.
- Immutable evidence captures and hash-chained audit events exported to write-once retention; legal holds are explicit.
- Versioned model cards, data cards, prompts, tools, workflows, policies, eval sets, approval records, and deployment manifests.
- Threat tests cover indirect prompt injection, poisoned sources, SSRF, tool argument injection, excessive agency, data exfiltration, inference across compartments, and malicious feedback.
- Human approval is mandatory for outreach, publication, customer proposals, government/defense positioning, sensitive data, paid sources, capital, contracts, and material decisions.

## Strategic monitoring and revenue architecture

### Signal weighting

| Evidence class                          | Credibility | Permitted commercial treatment                        |
| --------------------------------------- | ----------: | ----------------------------------------------------- |
| Mention only                            |           0 | Research; no revenue assumption                       |
| Official policy                         |           1 | Positioning; no pipeline value                        |
| Approved budget/program owner           |           2 | Discovery and capability mapping                      |
| Tender/pilot/contract/partnership       |           3 | Qualify only with buyer, eligibility, timing, and fit |
| Deployment/renewal/multi-buyer adoption |           4 | Consider repeatable product or licensing              |

A political announcement never becomes forecast revenue. Artemis separately stores announced, approved, contracted, deployed, addressable, and realistically reachable spend.

### Portfolio design

Prioritize three portable pathways: (1) remote asset/resilience monitoring for ports, energy, telecom, municipalities, insurers, and research operators; (2) supply-chain and vendor-risk workflows for logistics, industrial, regulated commercial, and public buyers; (3) secure evidence/incident collaboration for critical infrastructure, emergency management, and enterprise security. Each uses public/lawful data, open interfaces, cloud-neutral packaging, and no owned sensor inventory.

The opportunity record must identify money controller, pain owner, signer, mechanism, proof, partner, 90-day paid offer, recurring unit, and cycle-reversal reuse. Priority scoring is displayed with every 1–5 input and assumption; division-by-zero is prohibited because priority dimensions use 1–5.

## Scenario walkthrough

At 08:12 UTC an allowlisted Arctic port authority publishes a modernization tender. The acquisition adapter stores the page and document hash in quarantine and emits `source.observed`. Triage classifies it as civilian infrastructure; extraction identifies dates, buyer, budget language, and exact passages. The source is authoritative, but corroboration discovers that funding authorization is separate from procurement, so Artemis records two non-collapsed claims and labels the unknown delivery budget.

At 08:16 the policy engine projects only releasable fields into the analyst workspace. The opportunity agent maps a cloud-neutral asset-health dashboard to the public requirements, identifies port operations as user and procurement as signer, and proposes a six-week paid software pilot with synthetic and buyer-supplied data. The scenario agent scores recurring reuse across ports, energy, and telecom, then exposes elevated geographic and public-budget concentration. It recommends a commercial insurer/logistics validation track and no hardware purchase.

At 08:22 the analyst corrects an extracted deadline, rejects an unsupported claim that funding guarantees award, and approves the corrected brief—not external outreach. Those edits become labeled feedback linked to extraction prompt `p17`, workflow `w9`, model route `r4`, and the evidence snapshot. The system never silently edits production behavior.

Over the week, the eval service finds the same “approved versus contracted” confusion in 14 reviewed records. It proposes prompt `p18` and a deterministic lifecycle rule. A time-split replay raises milestone precision from 0.88 to 0.94 with unchanged recall, acceptable latency, zero policy violations, and better confidence calibration. A product owner and data steward approve the signed change. Apollo deploys it to shadow, then a 5% canary. If unsupported-claim rate rises or p95 latency exceeds the gate, rollout automatically returns to `p17/w9`; otherwise it promotes. The hash-chained ledger preserves inputs, diff, eval manifest, approvals, release, and observed outcome.

## 90-day delivery plan

1. **Days 0–30:** finalize lawful source register and coalition policy matrix; implement evidence, signal, claim, feedback, and audit objects; ingest five representative public sources; establish golden eval set and threat tests.
2. **Days 31–60:** deliver signal inbox, lineage viewer, hybrid authorized search, deterministic scoring, executive brief renderer, and analyst feedback; run three customer-discovery tracks without automated outreach.
3. **Days 61–90:** add opportunity/scenario agents, approval queue, shadow evaluation, Apollo canary/rollback, SLO dashboards, and one paid software-only pilot contingent on buyer validation.

Go/no-go requires at least three distinct buyer conversations across two civilian segments, one credible paid pilot path, complete evidence attribution, no critical policy leakage, acceptable unit economics, and a reusable architecture. Stop if no budget owner or paid validation emerges, source licensing is incompatible, required data cannot be lawfully obtained, or delivery requires single-supplier hardware/fixed capacity.

## Executive output contract

Each reporting run renders: mission, objective, reporting period, status, executive signal and unknowns; credibility table; Arctic and NATO-related public opportunities; bear-case table; revenue-independence matrix; stranded-asset review; competitor/partner evidence; 90-day actions; KPI dashboard; decision; and one next action with owner, deadline, expected evidence, and stop condition. Every row retains the eight evidence/decision labels, source metadata, confidence, assumptions, owner, and review date.
