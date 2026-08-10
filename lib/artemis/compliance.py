from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence


class EvidenceStatus(StrEnum):
    FRESH = "fresh"
    STALE = "stale"
    FAILED = "failed"


class ActionRisk(StrEnum):
    ANALYTICAL = "analytical"
    OPERATIONAL = "operational"
    REGULATORY = "regulatory"


@dataclass(frozen=True)
class Provenance:
    source_system: str
    source_object_id: str
    collected_at: datetime
    content_hash: str
    connector_version: str

    def __post_init__(self) -> None:
        if self.collected_at.tzinfo is None:
            raise ValueError("collected_at must be timezone-aware")
        if len(self.content_hash) != 64:
            raise ValueError("content_hash must be a SHA-256 digest")


@dataclass(frozen=True)
class EvidenceArtifact:
    artifact_id: str
    tenant_id: str
    control_id: str
    observed_at: datetime
    expires_at: datetime
    provenance: Provenance
    policy_labels: frozenset[str]
    payload: Mapping[str, Any] = field(repr=False)

    def __post_init__(self) -> None:
        if self.observed_at.tzinfo is None or self.expires_at.tzinfo is None:
            raise ValueError("evidence timestamps must be timezone-aware")
        if self.expires_at <= self.observed_at:
            raise ValueError("evidence expiry must follow observation")

    def status_at(self, now: datetime) -> EvidenceStatus:
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        return EvidenceStatus.FRESH if now < self.expires_at else EvidenceStatus.STALE


@dataclass(frozen=True)
class ControlDefinition:
    control_id: str
    title: str
    obligation_ids: tuple[str, ...]
    evidence_types: tuple[str, ...]
    test_version: str
    owner_id: str


@dataclass(frozen=True)
class ControlResult:
    control_id: str
    passed: bool
    tested_at: datetime
    test_version: str
    evidence_ids: tuple[str, ...]
    finding: str | None


class ContinuousControlMonitor:
    def evaluate(
        self,
        control: ControlDefinition,
        evidence: Sequence[EvidenceArtifact],
        now: datetime,
    ) -> ControlResult:
        applicable = tuple(
            artifact
            for artifact in evidence
            if artifact.control_id == control.control_id and artifact.status_at(now) is EvidenceStatus.FRESH
        )
        passed = bool(applicable)
        return ControlResult(
            control_id=control.control_id,
            passed=passed,
            tested_at=now,
            test_version=control.test_version,
            evidence_ids=tuple(item.artifact_id for item in applicable),
            finding=None if passed else "No current evidence satisfies the control",
        )


@dataclass(frozen=True)
class RiskNode:
    node_id: str
    node_type: str
    name: str
    criticality: int

    def __post_init__(self) -> None:
        if not 1 <= self.criticality <= 5:
            raise ValueError("criticality must be from 1 to 5")


@dataclass(frozen=True)
class RiskEdge:
    source_id: str
    target_id: str
    relationship: str


class SupplyChainRiskGraph:
    def __init__(self, nodes: Sequence[RiskNode], edges: Sequence[RiskEdge]) -> None:
        self.nodes = {node.node_id: node for node in nodes}
        self.edges = tuple(edges)
        if any(edge.source_id not in self.nodes or edge.target_id not in self.nodes for edge in edges):
            raise ValueError("risk edges must reference known nodes")

    def impacted_assets(self, start_id: str) -> tuple[RiskNode, ...]:
        visited = {start_id}
        frontier = [start_id]
        while frontier:
            current = frontier.pop()
            for edge in self.edges:
                if edge.source_id == current and edge.target_id not in visited:
                    visited.add(edge.target_id)
                    frontier.append(edge.target_id)
        return tuple(self.nodes[node_id] for node_id in visited if node_id != start_id)

    def exposure_score(self, start_id: str) -> int:
        return sum(node.criticality for node in self.impacted_assets(start_id))


@dataclass(frozen=True)
class IncidentEvent:
    event_id: str
    occurred_at: datetime
    recorded_at: datetime
    actor_id: str
    action: str
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.occurred_at.tzinfo is None or self.recorded_at.tzinfo is None:
            raise ValueError("incident timestamps must be timezone-aware")


class IncidentEvidenceEngine:
    def chronology(self, events: Sequence[IncidentEvent]) -> tuple[IncidentEvent, ...]:
        identifiers = [event.event_id for event in events]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("incident event IDs must be unique")
        return tuple(sorted(events, key=lambda event: (event.occurred_at, event.recorded_at, event.event_id)))


@dataclass(frozen=True)
class PolicyContext:
    actor_id: str
    tenant_id: str
    compartments: frozenset[str]
    purpose: str
    approved_action_hash: str | None = None


class CompliancePolicyEngine:
    def authorize(
        self,
        action: str,
        risk: ActionRisk,
        context: PolicyContext,
        resource_tenant_id: str,
        resource_labels: frozenset[str],
        action_payload: Mapping[str, Any],
    ) -> bool:
        if context.tenant_id != resource_tenant_id:
            return False
        if not resource_labels.issubset(context.compartments):
            return False
        if context.purpose not in {"assessment", "operations", "audit", "regulatory_reporting"}:
            return False
        if risk is ActionRisk.ANALYTICAL:
            return True
        return context.approved_action_hash == action_digest(action, action_payload)


@dataclass(frozen=True)
class EvidencePackage:
    package_id: str
    audience: str
    as_of: datetime
    artifact_ids: tuple[str, ...]
    control_result_ids: tuple[str, ...]
    manifest_hash: str


class ExecutiveEvidenceVault:
    def build_package(
        self,
        package_id: str,
        audience: str,
        as_of: datetime,
        artifacts: Sequence[EvidenceArtifact],
        control_results: Sequence[ControlResult],
    ) -> EvidencePackage:
        if any(artifact.status_at(as_of) is not EvidenceStatus.FRESH for artifact in artifacts):
            raise ValueError("evidence packages cannot contain stale evidence")
        artifact_ids = tuple(sorted(artifact.artifact_id for artifact in artifacts))
        result_ids = tuple(sorted(f"{result.control_id}:{result.test_version}" for result in control_results))
        manifest = json.dumps(
            {"audience": audience, "as_of": as_of.isoformat(), "artifacts": artifact_ids, "results": result_ids},
            sort_keys=True,
            separators=(",", ":"),
        )
        return EvidencePackage(
            package_id,
            audience,
            as_of,
            artifact_ids,
            result_ids,
            sha256(manifest.encode()).hexdigest(),
        )


def action_digest(action: str, payload: Mapping[str, Any]) -> str:
    canonical = json.dumps({"action": action, "payload": payload}, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(canonical.encode()).hexdigest()
