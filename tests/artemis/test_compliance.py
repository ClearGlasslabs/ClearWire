from datetime import datetime, timezone

import pytest

from lib.artemis.compliance import (
    BehaviorCandidate,
    CompliancePolicy,
    ControlFinding,
    ControlResult,
    EvaluationMetrics,
    EvidenceArtifact,
    EvidenceVault,
    MissionContext,
    PromotionPolicy,
    append_ledger_event,
    canonical_payload_hash,
)


NOW = datetime(2026, 8, 10, tzinfo=timezone.utc)


def evidence(**overrides: object) -> EvidenceArtifact:
    values = {
        "evidence_id": "ev-1",
        "source_system": "entra-id",
        "source_locator": "tenant/groups/admins",
        "collected_at": NOW,
        "valid_at": NOW,
        "payload_hash": canonical_payload_hash({"mfa": True}),
        "control_ids": ("IAM-01",),
        "compartments": frozenset({"CAN-ENERGY"}),
        "classification": 2,
        "collector_version": "entra-1.0.0",
    }
    values.update(overrides)
    return EvidenceArtifact(**values)


def context(**overrides: object) -> MissionContext:
    values = {
        "actor_id": "operator-7",
        "tenant_id": "tenant-1",
        "coalition": "CAN",
        "compartments": frozenset({"CAN-ENERGY"}),
        "purpose": "assessment",
        "classification_ceiling": 2,
        "trace_id": "trace-1",
    }
    values.update(overrides)
    return MissionContext(**values)


def metrics(**overrides: object) -> EvaluationMetrics:
    values = {
        "precision": 0.94,
        "recall": 0.91,
        "false_negative_rate": 0.09,
        "operator_acceptance": 0.88,
        "citation_coverage": 1.0,
        "policy_violations": 0,
        "latency_p95_ms": 800.0,
    }
    values.update(overrides)
    return EvaluationMetrics(**values)


def test_policy_enforces_compartments_classification_and_two_person_control() -> None:
    policy = CompliancePolicy()

    assert not policy.decide("read_evidence", context(compartments=frozenset()), frozenset({"CAN-ENERGY"}), 2).allowed
    assert not policy.decide("read_evidence", context(classification_ceiling=1), frozenset({"CAN-ENERGY"}), 2).allowed
    assert not policy.decide("notify_regulator", context(), frozenset({"CAN-ENERGY"}), 2, ("approver-1",)).allowed
    assert policy.decide(
        "notify_regulator", context(), frozenset({"CAN-ENERGY"}), 2, ("approver-1", "approver-2")
    ).allowed


def test_evidence_vault_deduplicates_payloads_and_filters_reads() -> None:
    vault = EvidenceVault()

    assert vault.ingest(evidence())
    assert not vault.ingest(evidence(evidence_id="ev-2"))
    assert vault.authorized(context(), CompliancePolicy()) == (evidence(),)
    assert vault.authorized(context(compartments=frozenset()), CompliancePolicy()) == ()


def test_evidence_rejects_non_hexadecimal_digest() -> None:
    with pytest.raises(ValueError, match="SHA-256"):
        evidence(payload_hash="z" * 64)


def test_evidence_vault_rejects_reused_identifier_with_different_payload() -> None:
    vault = EvidenceVault()
    vault.ingest(evidence())

    with pytest.raises(ValueError, match="evidence_id"):
        vault.ingest(evidence(payload_hash=canonical_payload_hash({"mfa": False})))


def test_determinate_finding_requires_evidence() -> None:
    with pytest.raises(ValueError, match="requires evidence"):
        ControlFinding("finding-1", "IAM-01", ControlResult.FAIL, NOW, (), "control-1.0.0", "MFA missing", 0.98)


def test_candidate_promotion_requires_non_regression_and_distinct_approvals() -> None:
    candidate = BehaviorCandidate(
        "candidate-1",
        "prompt",
        "triage-4",
        "triage-5",
        (NOW, NOW),
        canonical_payload_hash({"eval": "2026-08"}),
        metrics(precision=0.95),
        approvals=("risk-owner", "model-owner"),
    )
    allowed, failures = PromotionPolicy().evaluate(candidate, metrics())

    assert allowed
    assert failures == ()


def test_candidate_rollout_is_blocked_on_policy_or_quality_regression() -> None:
    candidate = BehaviorCandidate(
        "candidate-2",
        "route",
        "router-2",
        "router-3",
        (NOW, NOW),
        canonical_payload_hash({"eval": "2026-08"}),
        metrics(recall=0.80, policy_violations=1),
        approvals=("risk-owner", "model-owner"),
    )
    allowed, failures = PromotionPolicy().evaluate(candidate, metrics())

    assert not allowed
    assert "candidate produced policy violations" in failures
    assert "recall regressed" in failures


def test_candidate_rollout_is_blocked_when_operator_acceptance_regresses() -> None:
    candidate = BehaviorCandidate(
        "candidate-3",
        "workflow",
        "workflow-2",
        "workflow-3",
        (NOW, NOW),
        canonical_payload_hash({"eval": "2026-08"}),
        metrics(operator_acceptance=0.70),
        approvals=("risk-owner", "model-owner"),
    )
    allowed, failures = PromotionPolicy().evaluate(candidate, metrics())

    assert not allowed
    assert "operator acceptance regressed" in failures


def test_metrics_reject_values_outside_probability_range() -> None:
    with pytest.raises(ValueError, match="precision"):
        metrics(precision=1.01)


def test_ledger_hash_changes_when_event_is_tampered_with() -> None:
    entry = append_ledger_event("genesis", {"action": "control_evaluated"}, NOW)
    tampered = {**entry, "event": {"action": "finding_closed"}}

    original_hash = canonical_payload_hash({key: value for key, value in entry.items() if key != "event_hash"})
    tampered_hash = canonical_payload_hash({key: value for key, value in tampered.items() if key != "event_hash"})
    assert entry["event_hash"] == original_hash
    assert entry["event_hash"] != tampered_hash
