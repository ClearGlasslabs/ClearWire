from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence


SHA256_HEX_LENGTH = 64
MAX_CONFIDENCE = 1.0
MAX_LATENCY_REGRESSION_RATIO = 1.10


class EvidenceState(StrEnum):
    OBSERVED = "observed"
    VALIDATED = "validated"
    SUPERSEDED = "superseded"
    REVOKED = "revoked"


class ControlResult(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


class ProposalState(StrEnum):
    DRAFT = "draft"
    EVALUATING = "evaluating"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    CANARY = "canary"
    PROMOTED = "promoted"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True)
class MissionContext:
    actor_id: str
    tenant_id: str
    coalition: str
    compartments: frozenset[str]
    purpose: str
    classification_ceiling: int
    trace_id: str


@dataclass(frozen=True)
class EvidenceArtifact:
    evidence_id: str
    source_system: str
    source_locator: str
    collected_at: datetime
    valid_at: datetime
    payload_hash: str
    control_ids: tuple[str, ...]
    compartments: frozenset[str]
    classification: int
    collector_version: str
    state: EvidenceState = EvidenceState.OBSERVED

    def __post_init__(self) -> None:
        if self.collected_at.tzinfo is None or self.valid_at.tzinfo is None:
            raise ValueError("evidence timestamps must be timezone-aware")
        if not self.control_ids:
            raise ValueError("evidence must map to at least one control")
        if len(self.payload_hash) != SHA256_HEX_LENGTH or any(character not in "0123456789abcdef" for character in self.payload_hash):
            raise ValueError("payload_hash must be a SHA-256 hexadecimal digest")


@dataclass(frozen=True)
class ControlDefinition:
    control_id: str
    title: str
    framework_refs: tuple[str, ...]
    test_type: str
    required_evidence_types: tuple[str, ...]
    owner_id: str
    review_interval_seconds: int


@dataclass(frozen=True)
class ControlFinding:
    finding_id: str
    control_id: str
    result: ControlResult
    evaluated_at: datetime
    evidence_ids: tuple[str, ...]
    evaluator_version: str
    rationale: str
    confidence: float

    def __post_init__(self) -> None:
        if self.evaluated_at.tzinfo is None:
            raise ValueError("evaluated_at must be timezone-aware")
        if not 0 <= self.confidence <= MAX_CONFIDENCE:
            raise ValueError("confidence must be between zero and one")
        if self.result is not ControlResult.UNKNOWN and not self.evidence_ids:
            raise ValueError("a determinate result requires evidence")


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    obligations: tuple[str, ...] = ()


class CompliancePolicy:
    READ_PURPOSES = frozenset({"assessment", "audit", "incident", "remediation"})
    SIGNIFICANT_ACTIONS = frozenset({"close_finding", "export_regulatory_package", "notify_regulator", "promote_candidate"})

    def decide(
        self,
        action: str,
        context: MissionContext,
        resource_compartments: frozenset[str],
        resource_classification: int,
        approval_ids: Sequence[str] = (),
    ) -> PolicyDecision:
        if context.purpose not in self.READ_PURPOSES:
            return PolicyDecision(False, "purpose is not authorized")
        if not resource_compartments.issubset(context.compartments):
            return PolicyDecision(False, "need-to-know compartments are missing")
        if resource_classification > context.classification_ceiling:
            return PolicyDecision(False, "classification ceiling exceeded")
        if action in self.SIGNIFICANT_ACTIONS and len(set(approval_ids)) < 2:
            return PolicyDecision(False, "two distinct approvals are required")
        return PolicyDecision(True, "authorized", ("append_audit_event", "preserve_lineage"))


@dataclass(frozen=True)
class EvaluationMetrics:
    precision: float
    recall: float
    false_negative_rate: float
    operator_acceptance: float
    citation_coverage: float
    policy_violations: int
    latency_p95_ms: float

    def __post_init__(self) -> None:
        rates = {
            "precision": self.precision,
            "recall": self.recall,
            "false_negative_rate": self.false_negative_rate,
            "operator_acceptance": self.operator_acceptance,
            "citation_coverage": self.citation_coverage,
        }
        for name, value in rates.items():
            if not 0 <= value <= MAX_CONFIDENCE:
                raise ValueError(f"{name} must be between zero and one")
        if self.policy_violations < 0:
            raise ValueError("policy_violations cannot be negative")
        if self.latency_p95_ms <= 0:
            raise ValueError("latency_p95_ms must be positive")


@dataclass(frozen=True)
class BehaviorCandidate:
    candidate_id: str
    artifact_type: str
    base_version: str
    candidate_version: str
    training_window: tuple[datetime, datetime]
    evaluation_dataset_hash: str
    metrics: EvaluationMetrics
    state: ProposalState = ProposalState.DRAFT
    approvals: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        start, end = self.training_window
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("training window timestamps must be timezone-aware")
        if start > end:
            raise ValueError("training window start cannot follow its end")
        if self.base_version == self.candidate_version:
            raise ValueError("candidate version must differ from the base version")
        if len(self.evaluation_dataset_hash) != SHA256_HEX_LENGTH or any(
            character not in "0123456789abcdef" for character in self.evaluation_dataset_hash
        ):
            raise ValueError("evaluation_dataset_hash must be a SHA-256 hexadecimal digest")


class PromotionPolicy:
    def evaluate(self, candidate: BehaviorCandidate, incumbent: EvaluationMetrics) -> tuple[bool, tuple[str, ...]]:
        failures: list[str] = []
        if candidate.metrics.policy_violations:
            failures.append("candidate produced policy violations")
        if candidate.metrics.precision < incumbent.precision:
            failures.append("precision regressed")
        if candidate.metrics.recall < incumbent.recall:
            failures.append("recall regressed")
        if candidate.metrics.false_negative_rate > incumbent.false_negative_rate:
            failures.append("false-negative rate regressed")
        if candidate.metrics.operator_acceptance < incumbent.operator_acceptance:
            failures.append("operator acceptance regressed")
        if candidate.metrics.citation_coverage < incumbent.citation_coverage:
            failures.append("citation coverage regressed")
        if candidate.metrics.latency_p95_ms > incumbent.latency_p95_ms * MAX_LATENCY_REGRESSION_RATIO:
            failures.append("p95 latency exceeded the ten-percent budget")
        if len(set(candidate.approvals)) < 2:
            failures.append("two distinct human approvals are required")
        return not failures, tuple(failures)


class EvidenceVault:
    def __init__(self) -> None:
        self._artifacts: dict[str, EvidenceArtifact] = {}
        self._payload_hashes: set[str] = set()

    def ingest(self, artifact: EvidenceArtifact) -> bool:
        if artifact.evidence_id in self._artifacts:
            raise ValueError("evidence_id already exists")
        if artifact.payload_hash in self._payload_hashes:
            return False
        self._artifacts[artifact.evidence_id] = artifact
        self._payload_hashes.add(artifact.payload_hash)
        return True

    def authorized(self, context: MissionContext, policy: CompliancePolicy) -> tuple[EvidenceArtifact, ...]:
        return tuple(
            artifact
            for artifact in self._artifacts.values()
            if policy.decide("read_evidence", context, artifact.compartments, artifact.classification).allowed
        )


def canonical_payload_hash(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(canonical.encode()).hexdigest()


def append_ledger_event(previous_hash: str, event: Mapping[str, Any], recorded_at: datetime | None = None) -> dict[str, Any]:
    timestamp = recorded_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise ValueError("recorded_at must be timezone-aware")
    envelope = {"previous_hash": previous_hash, "recorded_at": timestamp.isoformat(), "event": event}
    return {**envelope, "event_hash": canonical_payload_hash(envelope)}
