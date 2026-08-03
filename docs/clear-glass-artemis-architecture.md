# ClearGlassInc Artemis architecture

## Purpose and operating constraints

ClearGlassInc Artemis is a human-governed intelligence platform for secure,
coalition-aware, multi-domain operations. It combines Palantir Gotham for
investigations and operational entity tracking, Foundry for governed data and
ontology, AIP for copilots and agent workflows, and Apollo for controlled
delivery. The platform may propose changes to prompts, routing, heuristics, and
workflows, but it may never approve, deploy, or expand its own authority.

The design optimizes for evidence-backed recommendations rather than autonomous
action. Every derived claim carries provenance, event time, processing time,
confidence, policy context, and the versioned logic that produced it.

## System architecture

```text
Sources -> ingress gateways -> durable event log -> Foundry pipelines
                                                -> quarantine/dead-letter
                                                     |
                      governed lakehouse <- ontology <- search/vector indexes
                             |                  |
Gotham investigations <------+----- AIP tool gateway ----- model router
        |                                   |                    |
        +---- operations UI ---- workflow engine ---- approval service
                                      |
                         immutable decision/audit ledger

Apollo: build attestations -> staged rings -> policy checks -> deploy/rollback
Observability: metrics + logs + traces + evals + data/model drift
```

### Component boundaries

| Layer            | Responsibility                                                    | Never responsible for                            |
| ---------------- | ----------------------------------------------------------------- | ------------------------------------------------ |
| Web UI           | Case graph, timeline, evidence, approvals, eval review            | Reimplementing authorization or confidence logic |
| API gateway      | Identity, request validation, rate limits, trace context          | Direct model or database access                  |
| Mission services | Cases, alerts, tasks, approvals, feedback                         | Bypassing ontology actions                       |
| Event layer      | Ordered, replayable facts with schema contracts                   | Treating delivery as exactly once                |
| Foundry          | Source integration, lineage, transforms, ontology, applications   | Unreviewed operational action                    |
| Gotham           | Investigations, entity resolution, geospatial/temporal operations | Becoming an ungoverned duplicate store           |
| AIP              | Agent orchestration, model access, evals, tool use                | Self-approval or unrestricted tool execution     |
| Apollo           | Environment-aware rollout, health gates, rollback                 | Changing mission policy                          |
| Policy plane     | Need-to-know and action authorization                             | Trusting UI filtering as enforcement             |

### Runtime request path

1. The gateway validates workload or human identity, device posture, mission,
   compartment, purpose, and trace identifier.
2. The policy decision point returns an allow/deny decision plus obligations:
   redactions, maximum classification, allowed tools, and approval threshold.
3. A mission service reads ontology objects through a policy-enforcing adapter.
4. The AIP workflow receives only the least-privilege projection and a signed
   capability set. The model never receives database credentials.
5. Tool calls are schema validated, independently authorized, idempotent, and
   recorded with input/output hashes.
6. Operationally significant output becomes a proposed action. An authorized
   human approves it against the evidence bundle before execution.
7. Outcome, feedback, and telemetry are appended to the audit and learning
   streams; they do not mutate production behavior directly.

## Data and ontology

Foundry's ontology is the governed semantic contract connecting source-backed
objects, relationships, derived properties, and actions. Gotham consumes the
same mission semantics for investigation rather than maintaining incompatible
entity definitions.

### Core object types

| Object           | Key properties                                                |
| ---------------- | ------------------------------------------------------------- |
| `ObservedEntity` | stable ID, aliases, type, validity interval, confidence       |
| `Observation`    | source, event time, ingest time, payload hash, geolocation    |
| `Relationship`   | subject, predicate, object, valid interval, evidence IDs      |
| `Source`         | owner, reliability, handling caveats, retention policy        |
| `Mission`        | objective, jurisdiction, coalition, compartments, time bounds |
| `Case`           | mission, status, assignees, entity set, policy context        |
| `Alert`          | rule/model version, score, evidence, disposition, SLA         |
| `IntelProduct`   | claims, citations, classification, review state, version      |
| `ProposedAction` | capability, arguments, risk, evidence, approval state         |
| `Approval`       | approver, authority, decision, rationale, policy version      |
| `Feedback`       | target artifact, correction type, replacement, usefulness     |
| `EvaluationRun`  | dataset, candidate, metrics, slices, decision                 |
| `ChangeProposal` | prompt/workflow/router diff, evidence, risk, rollout plan     |

Relationships are first-class and time bounded: `Observation SUPPORTS Claim`,
`Entity PARTICIPATES_IN Event`, `Analyst REVIEWS Product`, and `Approval
AUTHORIZES ProposedAction`. A retracted claim remains addressable; a new
version supersedes it rather than deleting history.

### Confidence and temporal semantics

Store distinct values for source reliability, extraction confidence, entity
resolution probability, and analytic confidence. Do not collapse them into a
single unexplained score. Calibrate each probability against labeled outcomes,
retain the calibration version, and render uncertainty to operators.

Every fact uses bitemporal fields:

```sql
valid_from timestamptz not null,
valid_to timestamptz,
recorded_at timestamptz not null,
superseded_at timestamptz
```

`valid_*` describes the world; `recorded_at/superseded_at` describes platform
knowledge. This permits an analyst to reconstruct exactly what was knowable at
decision time without leaking later evidence into an evaluation.

### Lineage envelope

```json
{
  "artifact_id": "claim_01...",
  "source_refs": ["obs_01..."],
  "transform": { "name": "correlate_movements", "version": "sha256:..." },
  "model": { "provider": "approved", "model_id": "...", "version": "..." },
  "prompt_version": "prompt:triage:42",
  "policy_version": "policy:mission-access:18",
  "event_time": "2026-08-03T12:00:00Z",
  "processing_time": "2026-08-03T12:00:02Z"
}
```

### Permissions

Authorization intersects organization, coalition releasability, clearance,
compartment, mission assignment, geography, purpose, and time. Enforcement
occurs at ingress, ontology query, search retrieval, tool execution, and export.
Row/entity filters protect objects, column/property rules redact sensitive
fields, and relationship traversal applies the strictest effective policy of
the traversed evidence. Derived artifacts inherit source markings unless an
authorized release process explicitly changes them.

## AI and agent design

### Copilots

The analyst copilot builds cited timelines, finds contradictory evidence,
suggests entity merges, and drafts intelligence products. The commander
copilot summarizes mission state, alternatives, uncertainty, and second-order
effects. Both expose evidence and uncertainty before recommendations.

### Workflow graph

```text
receive -> validate -> deduplicate -> classify -> enrich (parallel)
                                           |-> entity resolution
                                           |-> geospatial correlation
                                           |-> source corroboration
        -> synthesize -> challenge -> policy review -> human approval
        -> execute authorized tool -> monitor outcome -> collect feedback
```

Agents are bounded roles, not unconstrained personas:

- **Triage** assigns urgency and routing with calibrated confidence.
- **Enrichment** invokes allowlisted, read-only tools under budgets.
- **Correlation** proposes links and includes counter-evidence.
- **Red team** searches for unsupported claims, contradictions, and policy risk.
- **Writer** produces a schema-constrained product with claim-level citations.
- **Action preparer** creates a non-executable action package.

The workflow engine owns state, deadlines, retries, compensation, and approval.
Models only propose the next transition. Each transition is deterministic,
validated, and authorized outside the model.

### Model router

Routing is constrained by classification, coalition, residency, modality,
latency SLO, observed quality, cost, and model approval status. Inputs are
content scanned and minimized before inference. Outputs pass schema,
groundedness, citation, data-loss-prevention, and policy checks. Fail closed for
action recommendations; degrade to a cited search experience for summaries.

## Self-improvement loop

```text
production signals -> privacy/quality validation -> immutable training ledger
 -> time-split eval sets -> candidate generator -> offline evaluation
 -> security/red-team review -> change proposal -> human approval
 -> shadow -> canary -> staged rollout -> continuous monitoring -> promote/rollback
```

### Signals

Capture explicit corrections, accept/reject rationale, claim edits, alert
dispositions, tool failures, retrieval misses, dwell time, escalation, mission
outcome, latency, and cost. Treat clicks and acceptance as weak labels rather
than truth. Sampling and review protect against automation bias and feedback
poisoning. Training datasets exclude unauthorized cross-compartment examples.

### Candidate generation and evaluation

A scheduled pipeline clusters failures by workflow and slice, then proposes a
minimal versioned diff: prompt text, few-shot examples, retrieval parameters,
workflow edges, or routing weights. It cannot alter system objectives, policy,
tool permissions, approval requirements, or its own acceptance thresholds.

Candidate evaluation uses frozen time-split datasets and reports precision,
recall, calibration error, citation accuracy, unsupported-claim rate, policy
violations, p50/p95/p99 latency, cost, override rate, and operator trust. All
gating metrics include mission, language, source, coalition, and classification
slices. A candidate fails on any safety regression even if aggregate quality
improves.

### Promotion contract

1. Generate a signed `ChangeProposal` with semantic diff and evidence.
2. Require independent mission owner, model risk, security, and data steward
   approval according to change risk.
3. Replay in an isolated environment with production-like policy fixtures.
4. Shadow without influencing operators; then canary to a bounded cohort.
5. Apollo promotes immutable artifacts through environment rings.
6. Automatically roll back on safety, quality, error-budget, or drift gates.
7. Retain the previous prompt, workflow, index, model route, and schema as one
   atomic release manifest so rollback cannot create an incompatible mixture.

## Full-stack implementation

### Services

```text
apps/operations-web       TypeScript UI and server-side gateway
services/ingress          Python validation, normalization, idempotency
services/case             case and mission lifecycle
services/workflow         durable state machines and approval waits
services/tool-gateway     signed capabilities and tool adapters
services/policy           policy decision/enforcement points
services/evaluation       dataset construction, scoring, promotion gates
packages/contracts        Protobuf/JSON Schema/OpenAPI contracts
packages/telemetry        trace, metric, audit conventions
```

Use a transactional outbox for service state plus emitted events. Consumers
deduplicate by `(event_id, handler_version)`. Partition by mission/entity when
ordering matters, set explicit retry budgets, and quarantine poison messages
with operator-visible replay controls.

### Python event contract and handler

```python
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class Marking(BaseModel):
    classification: Literal["UNCLASSIFIED", "CONFIDENTIAL", "SECRET"]
    compartments: frozenset[str]
    releasable_to: frozenset[str]


class ObservationReceived(BaseModel):
    event_id: str
    mission_id: str
    source_id: str
    event_time: datetime
    ingest_time: datetime
    schema_version: Literal[1]
    confidence: Annotated[float, Field(ge=0, le=1)]
    payload_sha256: str
    marking: Marking


async def handle_observation(event: ObservationReceived, uow, policy) -> None:
    decision = await policy.authorize(
        principal="workload:ingress",
        action="observation.create",
        resource=event.model_dump(),
    )
    decision.require_allowed()
    async with uow.transaction() as tx:
        if await tx.receipts.exists(event.event_id, "observation-v1"):
            return
        observation_id = await tx.observations.insert(event)
        await tx.outbox.append(
            topic="observation.normalized.v1",
            key=event.mission_id,
            value={"observation_id": observation_id},
            causation_id=event.event_id,
        )
        await tx.receipts.insert(event.event_id, "observation-v1")
```

### Policy-enforced ontology query

```python
class OntologyRepository:
    def __init__(self, client, policy):
        self.client = client
        self.policy = policy

    async def timeline(self, principal, mission_id: str, as_of: datetime):
        obligations = await self.policy.authorize(
            principal=principal,
            action="mission.timeline.read",
            resource={"mission_id": mission_id, "as_of": as_of.isoformat()},
        )
        obligations.require_allowed()
        rows = await self.client.query(
            object_type="Observation",
            filters={"mission_id": mission_id, "recorded_at_lte": as_of},
            properties=obligations.allowed_properties,
        )
        return [obligations.redact(row) for row in rows]
```

The concrete Foundry client is isolated behind this adapter because ontology
SDK surfaces and deployment-specific object names vary. Generated clients and
contract tests bind the adapter to the environment rather than leaking vendor
details through mission logic.

### Tool call and approval state machine

```python
from enum import StrEnum


class State(StrEnum):
    TRIAGE = "triage"
    ENRICH = "enrich"
    REVIEW = "review"
    WAITING_APPROVAL = "waiting_approval"
    EXECUTING = "executing"
    COMPLETE = "complete"
    REJECTED = "rejected"


async def advance(run, command, services):
    transition = (run.state, command.kind)
    if transition == (State.REVIEW, "propose_action"):
        proposal = services.schemas.validate(command.payload)
        await services.policy.require(run.actor, proposal.capability, proposal)
        return await run.persist(State.WAITING_APPROVAL, proposal=proposal)
    if transition == (State.WAITING_APPROVAL, "approve"):
        await services.policy.require(command.actor, "action.approve", run.proposal)
        await services.approvals.verify_separation_of_duties(run, command.actor)
        return await run.persist(State.EXECUTING, approval=command.payload)
    if transition == (State.EXECUTING, "execute"):
        result = await services.tools.invoke(
            capability=run.proposal.capability,
            arguments=run.proposal.arguments,
            idempotency_key=run.id,
            approval_id=run.approval.id,
        )
        return await run.persist(State.COMPLETE, result=result)
    raise InvalidTransition(transition)
```

### Evaluation and promotion gate

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Gate:
    min_precision: float = 0.92
    min_recall: float = 0.85
    max_unsupported_claim_rate: float = 0.005
    max_policy_violations: int = 0
    max_p95_latency_ms: int = 2_000


def promotable(candidate, baseline, gate: Gate) -> bool:
    slices_pass = all(
        sample.precision >= gate.min_precision
        and sample.recall >= gate.min_recall
        and sample.unsupported_claim_rate <= gate.max_unsupported_claim_rate
        for sample in candidate.slices
    )
    return all(
        (
            slices_pass,
            candidate.policy_violations <= gate.max_policy_violations,
            candidate.p95_latency_ms <= gate.max_p95_latency_ms,
            candidate.operator_trust_lower_bound >= baseline.operator_trust_lower_bound,
        )
    )
```

Thresholds belong to a separately approved policy artifact, are tuned by risk
class, and must not be silently modified by candidate generation.

### API contract

```http
POST /v1/missions/{mission_id}/proposed-actions
Idempotency-Key: 01J...
Traceparent: 00-...

{
  "capability": "case.open",
  "arguments": {"entity_ids": ["entity_01..."]},
  "evidence_ids": ["claim_01..."],
  "workflow_version": "triage:17"
}
```

The response is `202 Accepted` with a proposal ID and required approval roles;
it never executes the action inline. Mutations use ontology-backed actions or
mission services so validations and audit hooks have one authoritative path.

### Observability

Propagate W3C trace context from ingress through event headers, workflows,
retrieval, inference, policy, and tools. Structured logs include trace, mission,
artifact version, model route, and policy decision IDs, but exclude raw secrets
and restricted content. Metrics cover freshness, backlog age, deduplication,
tool errors, retry exhaustion, retrieval recall, model quality, approval time,
and rollback rate. Audit records are append-only, hash chained, signed, and
exported to independent retention storage.

## Security and governance

- Phishing-resistant workforce authentication and short-lived workload identity.
- Mutual TLS and per-request authorization; network location grants no trust.
- Hardware-backed signing for builds, policies, model manifests, and releases.
- Egress-denied inference zones with allowlisted, brokered external access.
- Encryption keys segmented by environment, coalition, and compartment.
- Search and vector indexes physically or cryptographically partitioned where
  filter correctness alone is insufficient.
- Prompt-injection controls treat retrieved content as untrusted data; retrieved
  instructions cannot grant tools or override system policy.
- Dual control for releases and significant actions, including emergency access
  that is time limited, justified, alerted, and retrospectively reviewed.
- Retention, legal hold, correction, and deletion propagate to derived indexes
  while preserving authorized audit evidence.

## Diagnosis and incident response

The supplied incident fields contain placeholders, so there is not enough
evidence to identify a defect or failure domain. The minimum diagnostic input is
one reproducible request or event: timestamp, environment, trace/event ID,
expected result, actual result, deployment version, and sanitized error.

### Hypothesis ladder

| Rank | Hypothesis                                        | Proof or disproof                                                        |
| ---- | ------------------------------------------------- | ------------------------------------------------------------------------ |
| 1    | Contract or policy rejection at a boundary        | Follow trace ID; compare request schema, markings, and policy decision   |
| 2    | Configuration/version drift or partial deployment | Compare Apollo release manifests, flags, schemas, and env hashes         |
| 3    | Stale or incorrectly partitioned cache/index      | Compare source/ontology/index versions and bypass cache safely           |
| 4    | Async race, duplicate, or out-of-order event      | Reconstruct causation IDs, partition offsets, receipts, and retries      |
| 5    | Upstream/downstream latency or outage             | Inspect dependency spans, timeout budgets, circuit breakers, and SLOs    |
| 6    | Database/query or temporal-boundary error         | Run read-only as-of query and inspect plan, locks, replica lag, and rows |

### Fault-isolation procedure

1. Freeze deploys and risky configuration changes while preserving evidence.
2. Establish impact, classification, start time, determinism, and load sensitivity.
3. Query a single trace across gateway, policy, mission service, event bus,
   Foundry transform, retrieval, model route, and tool gateway.
4. At each boundary record expected input/output, actual input/output, version,
   latency, retry count, and policy decision. The first divergence is the likely
   failure domain; later errors are consequences.
5. Compare a successful trace from the same cohort and an affected trace. Change
   one variable at a time: release, tenant/mission, identity, source, or load.
6. Add a runtime assertion at the divergence, then build a sanitized minimal
   replay. Avoid broad debug logging that could expose classified payloads.
7. Prefer rollback or a narrow feature-flag disablement over an untested hotfix.

Hidden risks include silent dead-letter accumulation, stale authorization
caches, mixed prompt/workflow/index versions, replica lag, clock skew,
non-idempotent retries, schema drift, feedback poisoning, and evaluations that
leak future evidence.

## Regression strategy

- Contract tests for every producer/consumer schema and ontology adapter.
- Property tests for policy monotonicity: adding restrictions never grants data.
- Bitemporal tests proving decisions see only evidence knowable at the time.
- State-machine tests covering invalid transitions, duplicate commands, timeout,
  approval revocation, compensation, and replay.
- Golden evals plus adversarial prompt-injection, citation, and policy suites.
- Load tests for p99 latency, backpressure, partition skew, and retry storms.
- Deployment tests proving manifest compatibility and one-command rollback.
- Chaos tests for broker duplication, model outage, index lag, and policy timeout.

## Scenario walkthrough

At 02:14:03Z, a signed sensor message enters an ingress enclave. The gateway
validates its schema and marking, assigns an event ID, and writes both the
observation and outbox record atomically. Foundry pipelines normalize the event,
attach lineage, and update ontology relationships. Gotham displays the new
observation in an existing investigation.

At 02:14:05Z, triage correlates it with two time-valid observations. Enrichment
runs read-only geospatial and source-corroboration tools in parallel. The red-team
agent finds that one alias match is weak, so synthesis lowers confidence and
shows the counter-evidence. The action preparer recommends opening a priority
case, producing a cited evidence bundle rather than executing the action.

At 02:15:10Z, an authorized operator rejects the priority level, selects
"insufficient corroboration," and changes it to routine. The case service stores
the original proposal, correction, rationale, policy version, and outcome. The
running workflow respects the decision immediately; the production prompt does
not change.

Overnight, the evaluation pipeline adds the reviewed example to a quarantined,
time-split dataset. Failure clustering identifies over-weighting of alias
similarity and proposes a routing/threshold diff. Offline replay improves false
positive rate without reducing recall, but the low-source-reliability slice
regresses, so the gate rejects it. A second minimal candidate passes all slices,
security review, and human approval. Apollo deploys it in shadow mode, then to a
5% canary. Drift and quality monitors remain within bounds, so it advances
through deployment rings. The signed release manifest and complete predecessor
remain available for atomic rollback.

This is how ClearGlassInc Artemis improves: observed outcomes create evidence;
evidence creates evaluated proposals; humans authorize bounded changes; and the
deployment plane promotes only immutable, reversible artifacts.
