from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence


SCORE_MIN = 0
SCORE_MAX = 5
REVENUE_INDEPENDENCE_DENOMINATOR = 45
BEAR_CASE_MAXIMUM = SCORE_MAX**4


class LifecycleStage(StrEnum):
    MENTIONED = "MENTIONED"
    ANNOUNCED = "ANNOUNCED"
    FUNDED = "FUNDED"
    PROCURED = "PROCURED"
    PILOTED = "PILOTED"
    DEPLOYED = "DEPLOYED"
    SCALED = "SCALED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    DELAYED = "DELAYED"
    UNCERTAIN = "UNCERTAIN"


class Decision(StrEnum):
    RESEARCH = "research_only"
    EARLY_HYPOTHESIS = "early_hypothesis"
    VALIDATE = "validate"
    CONTROLLED_PILOT = "controlled_pilot"
    PRODUCTIZE = "productize"


@dataclass(frozen=True)
class Evidence:
    source_name: str
    source_url: str
    published_at: datetime
    observed_at: datetime
    source_type: str
    excerpt: str
    reliability: int
    primary: bool
    independent: bool

    def __post_init__(self) -> None:
        _validate_score("reliability", self.reliability)
        if self.observed_at.tzinfo is None or self.published_at.tzinfo is None:
            raise ValueError("evidence timestamps must be timezone-aware")
        if not self.source_url.startswith("https://"):
            raise ValueError("source_url must use HTTPS")
        if not self.excerpt.strip():
            raise ValueError("an exact evidence excerpt is required")


@dataclass(frozen=True)
class Signal:
    signal_id: str
    title: str
    evidence: Evidence
    geography: tuple[str, ...]
    organizations: tuple[str, ...]
    domain: str
    signal_type: str
    lifecycle_stage: LifecycleStage
    strategic_relevance: str
    commercial_relevance: str
    credibility_relevance: str
    urgency: int
    confidence: int
    potential_customer_types: tuple[str, ...]
    potential_capabilities: tuple[str, ...]
    likely_budget_path: str | None
    dependencies: tuple[str, ...]
    next_validation_action: str
    owner: str
    review_date: datetime

    def __post_init__(self) -> None:
        _validate_score("urgency", self.urgency)
        _validate_score("confidence", self.confidence)
        if self.review_date.tzinfo is None:
            raise ValueError("review_date must be timezone-aware")

    @property
    def evidence_fingerprint(self) -> str:
        normalized = f"{self.evidence.source_url}|{self.evidence.published_at.isoformat()}|{self.evidence.excerpt.strip()}"
        return sha256(normalized.encode()).hexdigest()


@dataclass(frozen=True)
class RevenueIndependence:
    civilian_applicability: int
    customer_diversification: int
    geographic_diversification: int
    productization: int
    recurring_revenue: int
    supply_chain_resilience: int
    reusable_ip: int
    buyer_clarity: int
    pilot_feasibility: int

    def score(self) -> float:
        values = tuple(asdict(self).values())
        for name, value in asdict(self).items():
            _validate_score(name, value)
        return round(sum(values) / REVENUE_INDEPENDENCE_DENOMINATOR, 4)

    def decision(self) -> Decision:
        score = self.score()
        if score < 0.30:
            return Decision.RESEARCH
        if score < 0.50:
            return Decision.EARLY_HYPOTHESIS
        if score < 0.70:
            return Decision.VALIDATE
        if score < 0.85:
            return Decision.CONTROLLED_PILOT
        return Decision.PRODUCTIZE


@dataclass(frozen=True)
class BearCase:
    revenue_at_risk: int
    disruption_probability: int
    replacement_difficulty: int
    recovery_duration: int
    assumptions: tuple[str, ...]

    def exposure(self) -> int:
        values = asdict(self)
        for name in ("revenue_at_risk", "disruption_probability", "replacement_difficulty", "recovery_duration"):
            _validate_score(name, values[name])
        if not self.assumptions:
            raise ValueError("bear-case assumptions are required")
        return self.revenue_at_risk * self.disruption_probability * self.replacement_difficulty * self.recovery_duration

    def normalized_exposure(self) -> float:
        return round(self.exposure() / BEAR_CASE_MAXIMUM, 4)


@dataclass(frozen=True)
class ChangeProposal:
    proposal_id: str
    artifact_type: str
    base_version: str
    candidate_version: str
    rationale: str
    evidence_ids: tuple[str, ...]
    offline_metrics: Mapping[str, float]
    risk_level: str
    requested_by: str
    approvals: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PolicyContext:
    actor_id: str
    compartments: frozenset[str]
    coalition: str
    purpose: str
    human_approved: bool


class PolicyEngine:
    OPERATIONAL_ACTIONS = frozenset({"publish", "external_outreach", "open_case", "prepare_action_package", "deploy_candidate"})

    def authorize(self, action: str, context: PolicyContext, required_compartments: frozenset[str]) -> bool:
        if not required_compartments.issubset(context.compartments):
            return False
        if context.purpose not in {"analysis", "validation", "operations", "administration"}:
            return False
        if action in self.OPERATIONAL_ACTIONS and not context.human_approved:
            return False
        return True


class PromotionGate:
    REQUIRED_METRICS = frozenset({"precision", "recall", "latency_p95_ms", "operator_acceptance"})

    def evaluate(self, proposal: ChangeProposal, incumbent_metrics: Mapping[str, float]) -> tuple[bool, tuple[str, ...]]:
        reasons: list[str] = []
        missing = self.REQUIRED_METRICS - proposal.offline_metrics.keys()
        if missing:
            reasons.append(f"missing metrics: {', '.join(sorted(missing))}")
        if len(set(proposal.approvals)) < 2:
            reasons.append("two-person approval is required")
        for quality_metric in ("precision", "recall", "operator_acceptance"):
            if proposal.offline_metrics.get(quality_metric, -1) < incumbent_metrics.get(quality_metric, 0):
                reasons.append(f"{quality_metric} regressed")
        candidate_latency = proposal.offline_metrics.get("latency_p95_ms", float("inf"))
        if candidate_latency > incumbent_metrics.get("latency_p95_ms", 0) * 1.10:
            reasons.append("latency exceeds the 10% regression budget")
        if proposal.risk_level == "high":
            reasons.append("high-risk changes require a controlled shadow evaluation")
        return not reasons, tuple(reasons)


def append_audit_event(previous_hash: str, event: Mapping[str, Any]) -> dict[str, Any]:
    recorded_at = datetime.now(timezone.utc).isoformat()
    payload = {"previous_hash": previous_hash, "recorded_at": recorded_at, "event": event}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return {**payload, "event_hash": sha256(canonical.encode()).hexdigest()}


def deduplicate_signals(signals: Sequence[Signal]) -> tuple[Signal, ...]:
    by_fingerprint: dict[str, Signal] = {}
    for signal in signals:
        current = by_fingerprint.get(signal.evidence_fingerprint)
        if current is None or signal.confidence > current.confidence:
            by_fingerprint[signal.evidence_fingerprint] = signal
    return tuple(by_fingerprint.values())


def _validate_score(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not SCORE_MIN <= value <= SCORE_MAX:
        raise ValueError(f"{name} must be an integer from {SCORE_MIN} to {SCORE_MAX}")
