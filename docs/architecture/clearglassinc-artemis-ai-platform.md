# ClearGlassInc Artemis — Self-evolving AI intelligence platform

ClearGlassInc Artemis is a secure, coalition-aware, multi-domain intelligence platform built around Palantir Gotham, Foundry, AIP, and Apollo. It fuses live and historical data, reasons over mission context, supports audited human decisions at machine speed, and safely improves its prompts, workflows, model routing, and evaluation logic through explicit approval gates.

Palantir terminology used in this design:

- **Gotham**: operational intelligence environment for investigations, entity tracking, link analysis, and mission workflows.
- **Foundry**: data integration, ontology, transforms, application logic, and governed operational datasets.
- **AIP**: AI orchestration layer for copilots, tool-using agents, workflow automation, evaluations, and guardrailed model execution.
- **Apollo**: secure deployment, release orchestration, runtime control, staged rollout, rollback, and environment policy enforcement.

The design assumes a high-assurance deployment where AI may recommend and prepare work products, but operationally significant actions require human approval and policy validation.

---

## System Architecture

### End-to-end reference architecture

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                              ClearGlassInc Artemis                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ Web UI                                                                        │
│  - Analyst console  - Commander view  - Case workspace  - Eval dashboard      │
│  - Coalition markings  - Approval queues  - Ontology graph explorer           │
├──────────────────────────────────────────────────────────────────────────────┤
│ API Gateway                                                                   │
│  - mTLS / OIDC  - request signing  - rate limits  - schema validation         │
│  - ABAC decision point  - audit envelope injection                            │
├──────────────────────────────────────────────────────────────────────────────┤
│ Backend Services                                                              │
│  - Ingestion control  - Case service  - Alert service  - Feedback service     │
│  - Intel product service  - Workflow state service  - Policy service          │
├──────────────────────────────────────────────────────────────────────────────┤
│ Event and Streaming Layer                                                     │
│  - Kafka/Pulsar topics  - dead-letter queues  - exactly-once sinks            │
│  - temporal ordering  - watermarking  - replay windows                        │
├──────────────────────────────────────────────────────────────────────────────┤
│ Foundry Data and Ontology Layer                                                │
│  - Raw sources  - normalized datasets  - derived features  - ontology objects │
│  - object lineage  - temporal state  - row/column/entity permissions          │
├──────────────────────────────────────────────────────────────────────────────┤
│ Search and Retrieval Layer                                                     │
│  - entity search  - vector retrieval  - geospatial index  - temporal index    │
│  - hybrid sparse+dense retrieval with policy-filtered results                 │
├──────────────────────────────────────────────────────────────────────────────┤
│ AIP AI Orchestration Layer                                                     │
│  - copilots  - multi-agent workflows  - tool registry  - model router         │
│  - prompt registry  - eval harness  - human approval gates                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ Self-Improvement Control Plane                                                 │
│  - feedback aggregation  - drift detection  - experiment manager              │
│  - proposal generator  - review board workflow  - rollback manager            │
├──────────────────────────────────────────────────────────────────────────────┤
│ Observability and Governance                                                   │
│  - immutable audit logs  - traces  - metrics  - eval dashboards               │
│  - model cards  - prompt cards  - lineage viewer  - policy-as-code            │
├──────────────────────────────────────────────────────────────────────────────┤
│ Apollo Deployment Layer                                                        │
│  - environment pinning  - signed artifacts  - phased rollout  - rollback      │
│  - runtime config  - health gates  - disconnected operation support           │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Runtime decomposition

```text
artemis/
  apps/
    web-console/                 # TypeScript/React mission UI
    commander-dashboard/          # Readiness, risk, and approval view
  services/
    api-gateway/                  # Python FastAPI or Envoy fronted gateway
    ingestion-control/            # source registration and replay control
    ontology-query/               # policy-aware Foundry/Gotham query facade
    alert-orchestrator/           # triage and escalation workflows
    case-management/              # cases, tasks, notes, products
    feedback-capture/             # corrections, ratings, outcomes
    aip-agent-runtime/            # AIP tool calls, agent state, eval hooks
    self-improvement/             # prompt/workflow/model proposal service
    policy-engine/                # ABAC/Rego decisions and obligation checks
    audit-ledger/                 # append-only audit and provenance envelope
  data/
    foundry-transforms/           # source normalization and feature pipelines
    ontology/                     # object, link, action, and permission models
    evals/                        # goldens, rubrics, replay suites
  deploy/
    apollo/                       # Apollo package specs, rollout rings, health gates
    policy/                       # policy-as-code bundles
```

### Core principles

1. **Ontology-first operations**: all human and AI workflows operate over governed ontology objects, links, actions, and temporal states instead of ad hoc tables.
2. **Policy-filtered retrieval**: every query, embedding lookup, and tool call is constrained by need-to-know, classification, compartment, releasability, and mission scope.
3. **Human-controlled self-improvement**: the platform may propose upgrades, but it cannot autonomously change operational policy, mission goals, or production behavior without approval.
4. **Replayable decisions**: every AI recommendation records inputs, prompt versions, model versions, tools invoked, policy decisions, retrieved evidence, and operator outcome.
5. **Safe deployment by Apollo**: all code, prompts, workflows, and model routing changes are packaged, signed, staged, monitored, and rollbackable.

---

## Data and Ontology

### Foundry data zones

```text
Raw zone
  live_sensor_events
  partner_reports
  osint_feeds
  case_notes
  operator_feedback

Normalized zone
  normalized_event
  normalized_entity_observation
  normalized_relationship_observation
  normalized_geospatial_observation
  normalized_intel_product

Curated zone
  entity_resolution_candidate
  alert_candidate
  mission_context_feature
  model_eval_example
  approved_training_signal

Ontology-backed operational layer
  ArtemisEntity
  ArtemisEvent
  ArtemisRelationship
  ArtemisCase
  ArtemisAlert
  ArtemisIntelProduct
  ArtemisRecommendation
  ArtemisFeedback
```

### Ontology entities

```yaml
ontology: ClearGlassIncArtemis
version: 1.0
objects:
  Person:
    primary_key: person_id
    properties:
      display_name: string
      aliases: string[]
      biometric_refs: string[]
      confidence: float
      classification: ClassificationMarking
      compartments: string[]
      valid_time: TimeRange
      system_time: TimeRange
      lineage_refs: string[]
  Organization:
    primary_key: org_id
    properties:
      name: string
      type: enum[commercial, government, ngo, unknown]
      jurisdictions: string[]
      confidence: float
      classification: ClassificationMarking
  Asset:
    primary_key: asset_id
    properties:
      asset_type: enum[vehicle, vessel, aircraft, device, facility, cyber_asset]
      identifiers: string[]
      last_known_location: GeoPoint
      operational_status: enum[active, dormant, decommissioned, unknown]
  Event:
    primary_key: event_id
    properties:
      event_type: string
      event_time: datetime
      ingest_time: datetime
      location: GeoShape
      source_refs: string[]
      confidence: float
      severity: float
      mission_refs: string[]
  Mission:
    primary_key: mission_id
    properties:
      name: string
      objectives: string[]
      authority_refs: string[]
      authorized_actions: string[]
      coalition_scope: string[]
      start_time: datetime
      end_time: datetime
  Case:
    primary_key: case_id
    properties:
      title: string
      status: enum[open, triage, active, pending_review, closed]
      lead_unit: string
      mission_id: string
      priority: enum[low, medium, high, critical]
      assigned_users: string[]
  Recommendation:
    primary_key: recommendation_id
    properties:
      recommendation_type: string
      generated_by_agent: string
      prompt_version: string
      model_version: string
      evidence_refs: string[]
      confidence: float
      required_approval_level: string
      status: enum[draft, pending_approval, approved, rejected, expired]
```

### Ontology relationships

```yaml
links:
  OBSERVED_AT:
    from: [Person, Asset, Organization]
    to: Event
    properties:
      observation_id: string
      source_ref: string
      confidence: float
      valid_time: TimeRange
      lineage_refs: string[]
  ASSOCIATED_WITH:
    from: [Person, Organization, Asset]
    to: [Person, Organization, Asset]
    properties:
      association_type: string
      strength: float
      first_seen: datetime
      last_seen: datetime
      evidence_refs: string[]
  PART_OF_MISSION:
    from: [Case, Alert, Recommendation, IntelProduct]
    to: Mission
  DERIVED_FROM:
    from: [Alert, Recommendation, IntelProduct]
    to: [Event, Entity, Relationship]
  REVIEWED_BY:
    from: Recommendation
    to: Operator
    properties:
      outcome: enum[approved, rejected, edited]
      review_time: datetime
      rationale_code: string
```

### Confidence, lineage, and temporal state

Every ontology object carries three separate confidence concepts:

- **Source confidence**: reliability of the source that produced the observation.
- **Extraction confidence**: confidence in parsing or AI extraction from raw evidence.
- **Analytic confidence**: confidence in the fused entity, link, alert, or recommendation.

Temporal state is bitemporal:

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class BitemporalState:
    valid_from: datetime
    valid_to: datetime | None
    system_from: datetime
    system_to: datetime | None

@dataclass(frozen=True)
class LineageRef:
    dataset_rid: str
    row_id: str
    transform_version: str
    source_hash: str
    observed_at: datetime
```

AI agents must cite lineage references for claims. If an agent cannot find sufficient lineage-backed evidence, it must lower confidence, ask for human review, or abstain.

### Permission model

Permissions are evaluated at five layers:

1. **Dataset-level**: access to raw or transformed datasets.
2. **Row-level**: mission, compartment, coalition, and classification filtering.
3. **Column-level**: sensitive field redaction, such as biometrics or source identities.
4. **Entity-level**: object-specific caveats and need-to-know access.
5. **Action-level**: whether the user or agent may perform a workflow action.

```yaml
classification_marking:
  level: enum[unclassified, controlled, confidential, secret, top_secret]
  compartments: string[]
  releasable_to: string[]
  originator_controls: string[]
  retention_policy: string
```

The ontology drives both workflows and AI behavior by exposing typed object actions. For example, an `Alert` object may expose `triage`, `link_to_case`, `request_enrichment`, and `draft_intel_product`; each action has policy rules, audit obligations, required fields, and approval thresholds.

---

## AI and Agent Design

### Copilots

- **Analyst copilot**: asks ontology-aware questions, summarizes evidence, proposes entity links, drafts case notes, and explains confidence.
- **Commander copilot**: summarizes mission state, readiness, risk, open approvals, and competing courses of action.
- **Data steward copilot**: detects schema drift, source quality degradation, transform failures, and ontology mapping gaps.
- **Governance copilot**: reviews proposed prompts, workflows, and model routing changes against policy, evals, and audit requirements.

### Multi-agent workflows

```text
Live event received
  → TriageAgent classifies event severity and mission relevance
  → EnrichmentAgent retrieves related entities, events, and cases
  → CorrelationAgent scores links and competing hypotheses
  → SummarizationAgent drafts evidence-backed narrative
  → RecommendationAgent proposes next best action
  → PolicyAgent validates permissions and approval requirements
  → Human operator approves, edits, or rejects
  → FeedbackAgent converts outcome into eval and improvement signals
```

### Agent constraints

Agents are allowed to:

- Query policy-filtered ontology objects.
- Generate draft summaries, link hypotheses, and recommendations.
- Open cases in draft or triage status when permitted.
- Prepare action packages for human review.
- Propose prompt, workflow, heuristic, and routing changes.

Agents are not allowed to:

- Change mission objectives or authorities.
- Bypass approval gates.
- Escalate privileges.
- Release data across coalition boundaries.
- Execute operationally significant actions without human approval.
- Train or deploy new model artifacts directly into production.

### Model routing

The AIP model router selects the lowest-risk capable model based on task sensitivity, latency, context length, eval score, classification boundary, and tool needs.

```yaml
model_routing_policy:
  summarization:
    default: aip.secure-medium
    high_classification: aip.secure-isolated-large
    max_latency_ms: 2500
  entity_resolution:
    default: aip.extraction-specialist
    requires_structured_output: true
  commander_recommendation:
    default: aip.reasoning-large
    requires_human_review: true
    min_eval_score: 0.92
  prompt_proposal:
    default: aip.reasoning-large
    output_guardrails:
      - no_policy_bypass
      - no_new_authorities
      - approval_required
```

---

## Self-Improvement Loop

### Signal capture

The platform captures improvement signals without collecting unnecessary sensitive data:

```text
Operator feedback
  explicit ratings, corrections, edits, rejection reasons, trust scores

Behavioral signals
  accepted recommendations, time-to-triage, reopened cases, ignored alerts

Mission outcomes
  alert true/false positives, response quality, timeliness, downstream impact

System signals
  latency, retrieval misses, policy denials, tool failures, hallucination reports

Data quality signals
  source drift, schema changes, missing fields, stale entities, conflict rates
```

### Improvement pipeline

```text
1. Capture feedback event
2. Validate policy and redact sensitive fields
3. Convert signal into structured eval example
4. Replay current production prompt/workflow/model route
5. Generate candidate improvement
6. Run offline eval suite and regression suite
7. Run shadow evaluation on live traffic without affecting output
8. Prepare change proposal with metrics, risks, and rollback plan
9. Human review board approves or rejects
10. Apollo deploys to canary ring
11. Monitor eval, latency, trust, and incident metrics
12. Promote, pause, or roll back
```

### Versioned improvement artifacts

```yaml
prompt_version:
  prompt_id: alert_triage.v17
  parent_prompt_id: alert_triage.v16
  author: aip-proposal-agent
  approver: human-review-board
  eval_suite: alert_triage_regression_2026_07
  deployment_state: canary
  rollback_target: alert_triage.v16

workflow_version:
  workflow_id: live_event_triage.v9
  graph_hash: sha256:...
  changed_nodes:
    - correlation.score_links
    - recommendation.require_evidence_threshold

routing_version:
  route_id: commander_recommendation.v5
  change: increase threshold for large reasoning model on critical alerts
```

### Drift detection

```python
from dataclasses import dataclass
from statistics import mean

@dataclass(frozen=True)
class DriftWindow:
    metric_name: str
    baseline_values: list[float]
    current_values: list[float]
    warn_delta: float
    block_delta: float

    def decision(self) -> str:
        baseline = mean(self.baseline_values)
        current = mean(self.current_values)
        delta = abs(current - baseline)
        if delta >= self.block_delta:
            return "block_deployment"
        if delta >= self.warn_delta:
            return "require_review"
        return "continue"
```

### Safety gates

A self-upgrade cannot ship unless all conditions pass:

- No policy rule regression.
- No classification leakage in sampled outputs.
- No material latency regression for latency-sensitive workflows.
- Precision and recall meet workflow-specific thresholds.
- Human trust score does not decline beyond tolerance.
- Rollback target is valid and tested.
- Apollo canary health checks are green.

---

## Full-Stack Implementation

### Web UI

The web console is a mission workspace with strict data markings and approval UX.

```tsx
type ClassificationMarking = {
  level: "unclassified" | "controlled" | "confidential" | "secret" | "top_secret";
  compartments: string[];
  releasableTo: string[];
};

type RecommendationCardProps = {
  id: string;
  title: string;
  confidence: number;
  evidenceCount: number;
  marking: ClassificationMarking;
  requiredApprovalLevel: string;
  onApprove: (id: string) => void;
  onReject: (id: string, reason: string) => void;
};

export function RecommendationCard(props: RecommendationCardProps) {
  return (
    <section data-recommendation-id={props.id} className="rounded-xl border p-4">
      <div className="flex items-center justify-between">
        <h3>{props.title}</h3>
        <span>{props.marking.level.toUpperCase()}</span>
      </div>
      <p>Confidence: {(props.confidence * 100).toFixed(1)}%</p>
      <p>Evidence items: {props.evidenceCount}</p>
      <p>Approval required: {props.requiredApprovalLevel}</p>
      <div className="flex gap-2">
        <button onClick={() => props.onApprove(props.id)}>Approve</button>
        <button onClick={() => props.onReject(props.id, "operator_rejected")}>Reject</button>
      </div>
    </section>
  );
}
```

### API gateway request envelope

```python
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class RequestContext(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)
    user_id: str
    mission_id: str
    coalition: str
    compartments: list[str]
    classification_ceiling: str
    client_ip_hash: str
    received_at: datetime = Field(default_factory=datetime.utcnow)

class GatewayEnvelope(BaseModel):
    context: RequestContext
    payload: dict
    signature: str
```

### Backend services

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

app = FastAPI(title="ClearGlassInc Artemis API")

class TriageRequest(BaseModel):
    event_id: str
    mission_id: str

class TriageResponse(BaseModel):
    alert_id: str
    severity: float
    recommendation_id: str | None
    approval_required: bool

async def get_context() -> RequestContext:
    raise NotImplementedError

async def authorize(ctx: RequestContext, action: str, resource: str) -> None:
    decision = await policy_decision(ctx, action, resource)
    if not decision.allowed:
        raise HTTPException(status_code=403, detail="Access denied")

@app.post("/v1/triage", response_model=TriageResponse)
async def triage_event(request: TriageRequest, ctx: RequestContext = Depends(get_context)):
    await authorize(ctx, "triage:event", request.event_id)
    event = await ontology_get_event(request.event_id, ctx)
    result = await run_triage_workflow(event=event, context=ctx)
    await write_audit_event(ctx, "triage:event", request.event_id, result.model_dump())
    return result
```

### Event bus

```python
from pydantic import BaseModel
from datetime import datetime

class LiveEventMessage(BaseModel):
    event_id: str
    source_id: str
    event_type: str
    event_time: datetime
    payload_ref: str
    classification: str
    compartments: list[str]
    source_hash: str

async def handle_live_event(message: LiveEventMessage) -> None:
    normalized = await normalize_event(message)
    await foundry_write_dataset("normalized_event", normalized)
    ontology_event = await upsert_ontology_event(normalized)
    await publish("artemis.event.normalized", ontology_event)
```

### Search and retrieval

```sql
SELECT
  e.event_id,
  e.event_type,
  e.event_time,
  e.confidence,
  rel.to_entity_id,
  rel.association_type,
  rel.strength
FROM ontology_event e
JOIN ontology_relationship rel ON rel.from_event_id = e.event_id
WHERE e.mission_id = :mission_id
  AND e.event_time BETWEEN :start_time AND :end_time
  AND e.classification_level <= :classification_ceiling
  AND rel.compartments <@ :user_compartments
ORDER BY rel.strength DESC, e.event_time DESC
LIMIT 100;
```

### Workflow state machine

```python
from enum import StrEnum
from pydantic import BaseModel

class TriageState(StrEnum):
    RECEIVED = "received"
    NORMALIZED = "normalized"
    ENRICHED = "enriched"
    CORRELATED = "correlated"
    RECOMMENDED = "recommended"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLOSED = "closed"

class WorkflowTransition(BaseModel):
    from_state: TriageState
    to_state: TriageState
    required_action: str
    requires_human: bool = False

TRIAGE_TRANSITIONS = [
    WorkflowTransition(from_state=TriageState.RECEIVED, to_state=TriageState.NORMALIZED, required_action="normalize:event"),
    WorkflowTransition(from_state=TriageState.NORMALIZED, to_state=TriageState.ENRICHED, required_action="enrich:event"),
    WorkflowTransition(from_state=TriageState.ENRICHED, to_state=TriageState.CORRELATED, required_action="correlate:event"),
    WorkflowTransition(from_state=TriageState.CORRELATED, to_state=TriageState.RECOMMENDED, required_action="recommend:action"),
    WorkflowTransition(from_state=TriageState.RECOMMENDED, to_state=TriageState.PENDING_APPROVAL, required_action="submit:approval", requires_human=True),
]
```

### Apollo deployment rings

```yaml
apollo_package: clearglassinc-artemis
artifact_type: aip-workflow-bundle
version: 2026.07.14-001
rings:
  - name: lab
    auto_promote: false
    health_checks:
      - eval_suite_passed
      - policy_regression_passed
  - name: shadow
    traffic_mode: mirror
    duration: 24h
  - name: canary
    traffic_percent: 5
    rollback_on:
      hallucination_rate_gt: 0.01
      p95_latency_ms_gt: 3000
      policy_denial_spike_gt: 0.05
  - name: production
    approval_required: true
rollback:
  target_version: 2026.07.13-004
  max_time_to_restore_seconds: 300
```

---

## Security and Governance

### Zero-trust execution

- Every service authenticates with workload identity and mTLS.
- Every request carries a signed mission context envelope.
- Every data access is policy-checked and audited.
- Tools run with least privilege and scoped credentials.
- Agents receive short-lived tool grants, not standing credentials.
- Sensitive fields are redacted before entering logs, prompts, eval stores, or analytics.

### Policy-as-code

```rego
package artemis.authz

default allow := false

allow if {
  input.user.active == true
  input.action in input.user.allowed_actions
  input.resource.mission_id in input.user.mission_ids
  classification_allowed
  compartments_allowed
  coalition_allowed
}

classification_allowed if {
  levels := {"unclassified": 1, "controlled": 2, "confidential": 3, "secret": 4, "top_secret": 5}
  levels[input.resource.classification] <= levels[input.user.classification_ceiling]
}

compartments_allowed if {
  required := {c | c := input.resource.compartments[_]}
  held := {c | c := input.user.compartments[_]}
  required - held == set()
}

coalition_allowed if {
  input.user.coalition in input.resource.releasable_to
}
```

### Governance records

```yaml
model_card:
  model_id: aip.reasoning-large.2026-07
  approved_tasks:
    - commander_recommendation
    - prompt_proposal
  prohibited_tasks:
    - autonomous_operational_action
    - cross_coalition_release
  eval_thresholds:
    factuality: 0.97
    citation_coverage: 0.95
    policy_compliance: 1.0

prompt_card:
  prompt_id: alert_triage.v17
  owner: artemis-ai-governance
  approved_tools:
    - ontology.search
    - case.open_draft
    - intel_product.create_draft
  required_output_fields:
    - recommendation
    - confidence
    - evidence_refs
    - uncertainty
    - approval_required
```

### Immutable audit trail

Audit events are append-only and tamper-evident. Each record includes previous hash chaining.

```python
import hashlib
import json
from pydantic import BaseModel
from datetime import datetime

class AuditEvent(BaseModel):
    event_id: str
    previous_hash: str
    actor_id: str
    actor_type: str
    action: str
    resource_id: str
    policy_decision_id: str
    prompt_version: str | None = None
    model_version: str | None = None
    evidence_refs: list[str] = []
    created_at: datetime

    def canonical_hash(self) -> str:
        encoded = json.dumps(self.model_dump(mode="json"), sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
```

---

## Code Examples

### Policy-aware ontology query client

```python
from typing import Any

class OntologyClient:
    def __init__(self, foundry_client: Any, policy_client: Any):
        self.foundry = foundry_client
        self.policy = policy_client

    async def query_events(self, ctx: RequestContext, filters: dict) -> list[dict]:
        decision = await self.policy.authorize(
            subject=ctx.user_id,
            action="ontology:event:query",
            resource={"mission_id": ctx.mission_id, "filters": filters},
            context=ctx.model_dump(),
        )
        if not decision.allowed:
            return []

        safe_filters = {
            **filters,
            "mission_id": ctx.mission_id,
            "classification_ceiling": ctx.classification_ceiling,
            "compartments": ctx.compartments,
            "coalition": ctx.coalition,
        }
        return await self.foundry.query("ontology.events.policy_filtered", safe_filters)
```

### AIP tool definition

```python
from pydantic import BaseModel, Field

class EntitySearchInput(BaseModel):
    query: str = Field(min_length=3, max_length=256)
    mission_id: str
    max_results: int = Field(default=20, ge=1, le=100)

class EntitySearchResult(BaseModel):
    entity_id: str
    entity_type: str
    display_name: str
    confidence: float
    evidence_refs: list[str]

async def ontology_entity_search_tool(args: EntitySearchInput, ctx: RequestContext) -> list[EntitySearchResult]:
    await authorize(ctx, "ontology:entity:search", args.mission_id)
    rows = await ontology_client.search_entities(ctx, args.model_dump())
    await write_audit_event(ctx, "tool:ontology_entity_search", args.mission_id, {"result_count": len(rows)})
    return [EntitySearchResult(**row) for row in rows]
```

### Agent orchestration skeleton

```python
class ArtemisAgentRuntime:
    def __init__(self, model_router, tool_registry, audit, policy):
        self.model_router = model_router
        self.tool_registry = tool_registry
        self.audit = audit
        self.policy = policy

    async def run_recommendation_agent(self, ctx: RequestContext, alert_id: str) -> dict:
        await authorize(ctx, "recommendation:create", alert_id)
        prompt = await load_prompt("recommendation_agent", version="production")
        model = await self.model_router.select(
            task="commander_recommendation",
            classification_ceiling=ctx.classification_ceiling,
            latency_budget_ms=2500,
        )
        tools = self.tool_registry.scoped_tools(ctx, names=["ontology.search", "case.get", "intel_product.draft"])
        response = await model.run(
            prompt=prompt,
            input={"alert_id": alert_id, "mission_id": ctx.mission_id},
            tools=tools,
            required_output_schema="RecommendationOutput",
        )
        await self.audit.record_model_call(ctx, model.id, prompt.id, response.evidence_refs)
        return response.output
```

### Feedback to eval conversion

```python
class OperatorFeedback(BaseModel):
    feedback_id: str
    recommendation_id: str
    operator_id: str
    outcome: str
    edited_text: str | None = None
    rationale_code: str
    trust_score: int

class EvalExample(BaseModel):
    eval_id: str
    task: str
    input_ref: str
    expected_behavior: dict
    source_feedback_id: str
    sensitivity: str

async def convert_feedback_to_eval(feedback: OperatorFeedback) -> EvalExample | None:
    recommendation = await get_recommendation(feedback.recommendation_id)
    if feedback.outcome not in {"approved", "rejected", "edited"}:
        return None
    expected = {
        "operator_outcome": feedback.outcome,
        "rationale_code": feedback.rationale_code,
        "minimum_evidence_refs": len(recommendation.evidence_refs),
    }
    if feedback.edited_text:
        expected["preferred_summary_style"] = await redact_sensitive_text(feedback.edited_text)
    return EvalExample(
        eval_id=f"eval_{feedback.feedback_id}",
        task=recommendation.recommendation_type,
        input_ref=recommendation.source_alert_id,
        expected_behavior=expected,
        source_feedback_id=feedback.feedback_id,
        sensitivity=recommendation.classification,
    )
```

### Eval harness

```python
class EvalResult(BaseModel):
    eval_id: str
    prompt_version: str
    model_version: str
    passed: bool
    scores: dict[str, float]
    failure_reasons: list[str]

async def run_eval_suite(candidate_prompt: str, examples: list[EvalExample]) -> list[EvalResult]:
    results: list[EvalResult] = []
    for example in examples:
        output = await run_shadow_model(candidate_prompt, example.input_ref)
        scores = {
            "factuality": await score_factuality(output, example),
            "policy_compliance": await score_policy_compliance(output, example),
            "citation_coverage": await score_citation_coverage(output),
            "operator_alignment": await score_operator_alignment(output, example),
        }
        passed = (
            scores["factuality"] >= 0.97
            and scores["policy_compliance"] == 1.0
            and scores["citation_coverage"] >= 0.95
            and scores["operator_alignment"] >= 0.90
        )
        results.append(EvalResult(
            eval_id=example.eval_id,
            prompt_version="candidate",
            model_version="shadow",
            passed=passed,
            scores=scores,
            failure_reasons=[] if passed else [k for k, v in scores.items() if v < 0.90],
        ))
    return results
```

### Self-improvement proposal generation

```python
class ImprovementProposal(BaseModel):
    proposal_id: str
    artifact_type: str
    current_version: str
    candidate_version: str
    change_summary: str
    eval_delta: dict[str, float]
    risk_assessment: str
    rollback_target: str
    requires_approval_from: list[str]

async def propose_prompt_update(task: str, failed_examples: list[EvalExample]) -> ImprovementProposal:
    current_prompt = await load_prompt(task, version="production")
    candidate = await aip_generate_prompt_candidate(
        current_prompt=current_prompt,
        failed_examples=failed_examples,
        constraints=[
            "Do not add new authorities",
            "Do not remove evidence citation requirements",
            "Do not weaken approval gates",
            "Do not include sensitive raw fields in output",
        ],
    )
    eval_results = await run_eval_suite(candidate.text, await load_regression_suite(task))
    delta = summarize_eval_delta(eval_results)
    return ImprovementProposal(
        proposal_id=new_nanoid(),
        artifact_type="prompt",
        current_version=current_prompt.version,
        candidate_version=candidate.version,
        change_summary=candidate.summary,
        eval_delta=delta,
        risk_assessment=assess_change_risk(delta),
        rollback_target=current_prompt.version,
        requires_approval_from=["mission_owner", "ai_governance", "security"],
    )
```

---

## Scenario Walkthrough

### 1. Live intel event enters the system

A coalition partner stream emits a time-sensitive event with source markings and mission context. The ingestion-control service validates the schema, hashes the raw payload, stores the raw record in Foundry, normalizes it, and creates an `Event` ontology object with classification, compartments, lineage, and confidence.

```text
partner_report.raw
  → normalized_event
  → ontology.Event(event_id=evt_9Y2..., confidence=0.74)
  → artemis.event.normalized
```

### 2. Platform triages the event

The `TriageAgent` receives the normalized event. It retrieves related entities, prior alerts, mission objectives, and open cases through policy-filtered tools. It identifies that the event is relevant to an active mission, but evidence is incomplete.

Output:

```json
{
  "severity": 0.82,
  "mission_relevance": 0.91,
  "confidence": 0.76,
  "uncertainty": "Source is reliable, but entity match has two plausible candidates.",
  "evidence_refs": ["foundry://dataset/normalized_event/row/evt_9Y2", "ontology://entity/asset_71K"],
  "approval_required": true
}
```

### 3. Agent recommends a response

The `RecommendationAgent` drafts an action package: link the event to an existing case, request an additional collection task through a draft-only workflow, and notify the mission watch team. The `PolicyAgent` marks the collection request as operationally significant, so it must remain pending until a cleared operator approves it.

### 4. Operator approves or rejects

The analyst reviews the evidence graph in Gotham, checks lineage in Foundry, edits the summary, rejects one weak entity link, and approves a watch-team notification. The collection request remains pending commander approval.

The system captures:

```json
{
  "recommendation_id": "rec_A1P9",
  "operator_outcome": "edited",
  "rejected_link": "asset_71K ASSOCIATED_WITH org_44F",
  "rationale_code": "insufficient_entity_resolution",
  "trust_score": 4,
  "time_to_decision_seconds": 91
}
```

### 5. System learns from the outcome

The feedback service converts the rejected link into an eval example for entity resolution and correlation. The self-improvement service discovers a repeated pattern: the correlation workflow overweights one source type during low-visibility conditions. It proposes a scoring heuristic change and a prompt clarification requiring agents to surface competing candidates when entity resolution confidence is below `0.80`.

The proposal runs through offline evals and shadow traffic:

```text
entity_resolution_precision: 0.89 → 0.94
entity_resolution_recall:    0.86 → 0.85
citation_coverage:           0.96 → 0.97
p95_latency_ms:              1840 → 1910
policy_compliance:           1.00 → 1.00
```

Because recall drops slightly, the proposal is routed to human review instead of auto-promoting. The review board approves the prompt clarification but rejects the heuristic change. Apollo deploys only the approved prompt to the lab ring, then shadow, then canary. If hallucination rate, latency, or operator trust degrades, Apollo rolls back to the previous prompt version.

### 6. Future behavior improves safely

On the next similar event, Artemis does not assert a single weak link. It presents two candidate entities with evidence, confidence, and uncertainty. The analyst makes a faster decision, and the system records improved trust and lower correction rate without changing mission goals, authorities, or approval gates.

---

## Remaining implementation risks

- **Data availability**: degraded partner feeds can reduce correlation quality; mitigation is source health scoring and abstention thresholds.
- **Latency pressure**: large-context reasoning can exceed mission latency budgets; mitigation is routing, caching, and summarized evidence packs.
- **Overfitting to operator preference**: feedback may encode local habits; mitigation is cross-mission evals, governance review, and holdout suites.
- **Coalition release complexity**: releasability rules can be nuanced; mitigation is policy-as-code plus originator-control review queues.
- **Automation bias**: operators may over-trust fluent AI; mitigation is uncertainty display, evidence-first UX, and mandatory dissenting-hypothesis generation for high-impact recommendations.
