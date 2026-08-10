from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
import json
from typing import Mapping, Sequence


PROTECTED_CONFIGURATION = frozenset(
    {
        "approval_gates",
        "coalition_policy",
        "mission_goal",
        "retention_policy",
        "safety_policy",
        "source_hierarchy",
    }
)
REQUIRED_APPROVAL_ROLES = frozenset({"product_owner", "security_steward"})


class CandidateKind(StrEnum):
    PROMPT = "prompt"
    WORKFLOW = "workflow"
    ROUTE = "route"
    HEURISTIC = "heuristic"


class ReleaseStage(StrEnum):
    PROPOSED = "proposed"
    OFFLINE_EVALUATED = "offline_evaluated"
    APPROVED = "approved"
    SHADOW = "shadow"
    CANARY_5 = "canary_5"
    CANARY_25 = "canary_25"
    PRODUCTION = "production"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True)
class ArtifactVersions:
    prompt: str
    workflow: str
    model_route: str
    ontology: str
    policy: str
    dataset_snapshot: str


@dataclass(frozen=True)
class FeedbackSignal:
    interaction_id: str
    actor_id: str
    versions: ArtifactVersions
    disposition: str
    reason_code: str
    correction: str | None = None
    alert_outcome: str | None = None
    mission_result: str | None = None

    def training_label(self) -> str:
        if self.mission_result:
            return f"mission:{self.mission_result}"
        if self.alert_outcome:
            return f"alert:{self.alert_outcome}"
        return f"operator:{self.disposition}:{self.reason_code}"


@dataclass(frozen=True)
class EvaluationReport:
    dataset_hash: str
    sample_size: int
    precision: float
    recall: float
    unsupported_claim_rate: float
    policy_violations: int
    cross_compartment_leaks: int
    latency_p95_ms: float
    operator_acceptance: float


@dataclass
class UpgradeCandidate:
    candidate_id: str
    kind: CandidateKind
    base_version: str
    candidate_version: str
    changed_fields: frozenset[str]
    rationale: str
    stage: ReleaseStage = ReleaseStage.PROPOSED
    evaluation: EvaluationReport | None = None
    approvals: dict[str, str] = field(default_factory=dict)

    def validate_scope(self) -> None:
        protected = self.changed_fields & PROTECTED_CONFIGURATION
        if protected:
            raise ValueError(f"candidate changes protected configuration: {', '.join(sorted(protected))}")


class EvolutionController:
    _TRANSITIONS: Mapping[ReleaseStage, frozenset[ReleaseStage]] = {
        ReleaseStage.PROPOSED: frozenset({ReleaseStage.OFFLINE_EVALUATED, ReleaseStage.ROLLED_BACK}),
        ReleaseStage.OFFLINE_EVALUATED: frozenset({ReleaseStage.APPROVED, ReleaseStage.ROLLED_BACK}),
        ReleaseStage.APPROVED: frozenset({ReleaseStage.SHADOW, ReleaseStage.ROLLED_BACK}),
        ReleaseStage.SHADOW: frozenset({ReleaseStage.CANARY_5, ReleaseStage.ROLLED_BACK}),
        ReleaseStage.CANARY_5: frozenset({ReleaseStage.CANARY_25, ReleaseStage.ROLLED_BACK}),
        ReleaseStage.CANARY_25: frozenset({ReleaseStage.PRODUCTION, ReleaseStage.ROLLED_BACK}),
        ReleaseStage.PRODUCTION: frozenset({ReleaseStage.ROLLED_BACK}),
        ReleaseStage.ROLLED_BACK: frozenset(),
    }

    def attach_evaluation(self, candidate: UpgradeCandidate, report: EvaluationReport) -> None:
        candidate.validate_scope()
        if candidate.stage != ReleaseStage.PROPOSED:
            raise ValueError("only a proposed candidate can receive an evaluation")
        candidate.evaluation = report
        self._transition(candidate, ReleaseStage.OFFLINE_EVALUATED)

    def approve(self, candidate: UpgradeCandidate, role: str, actor_id: str) -> None:
        if candidate.stage not in {ReleaseStage.OFFLINE_EVALUATED, ReleaseStage.APPROVED}:
            raise ValueError("candidate is not ready for approval")
        if role not in REQUIRED_APPROVAL_ROLES:
            raise ValueError("approval role is not authorized")
        if actor_id in candidate.approvals.values():
            raise ValueError("approvers must be distinct people")
        candidate.approvals[role] = actor_id
        if REQUIRED_APPROVAL_ROLES.issubset(candidate.approvals):
            candidate.stage = ReleaseStage.APPROVED

    def promote(self, candidate: UpgradeCandidate, target: ReleaseStage) -> None:
        if candidate.evaluation is None:
            raise ValueError("evaluation is required before promotion")
        if candidate.evaluation.policy_violations or candidate.evaluation.cross_compartment_leaks:
            raise ValueError("a candidate with safety violations cannot be promoted")
        self._transition(candidate, target)

    def rollback(self, candidate: UpgradeCandidate) -> None:
        self._transition(candidate, ReleaseStage.ROLLED_BACK)

    def _transition(self, candidate: UpgradeCandidate, target: ReleaseStage) -> None:
        if target not in self._TRANSITIONS[candidate.stage]:
            raise ValueError(f"invalid release transition: {candidate.stage} -> {target}")
        candidate.stage = target


def deterministic_variant(subject_id: str, experiment_id: str, canary_percentage: int) -> str:
    if not 0 <= canary_percentage <= 100:
        raise ValueError("canary_percentage must be from 0 to 100")
    bucket = int(sha256(f"{experiment_id}:{subject_id}".encode()).hexdigest()[:8], 16) % 100
    return "candidate" if bucket < canary_percentage else "incumbent"


def feedback_dataset_hash(signals: Sequence[FeedbackSignal]) -> str:
    records = [
        {
            "interaction_id": signal.interaction_id,
            "versions": signal.versions.__dict__,
            "label": signal.training_label(),
        }
        for signal in sorted(signals, key=lambda item: item.interaction_id)
    ]
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode()).hexdigest()
