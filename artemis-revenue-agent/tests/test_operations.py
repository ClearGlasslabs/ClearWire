from fastapi import HTTPException, Response

from artemis_revenue_agent.api import jobs, qualify, readyz
from artemis_revenue_agent.feature_flags import FeatureFlag, FeatureFlags
from artemis_revenue_agent.idempotency import IdempotencyConflict, IdempotencyStore
from artemis_revenue_agent.operations import JOB_REGISTRY, JobLifecycle
from artemis_revenue_agent.observability import start_correlation
from artemis_revenue_agent.schemas import LeadInput


def lead_payload() -> dict[str, object]:
    return {
        "organization_name": "Ontario Example Manufacturing",
        "industry": "Manufacturing",
        "location": "Toronto, Ontario, Canada",
        "primary_concern": "security_visibility",
        "consent_to_contact": True,
    }


def test_registry_defines_operational_controls_for_every_job():
    assert set(JOB_REGISTRY) == {
        "incident.evaluate",
        "lead.external_handoff",
        "lead.qualify",
    }
    for job in JOB_REGISTRY.values():
        assert job.owner.startswith("ClearGlassInc Artemis")
        assert job.timeout_seconds > 0
        assert job.retry.maximum_attempts >= 1
        assert job.idempotency
        assert job.retention
        assert job.audit_required is True
        assert job.rollback
    assert JOB_REGISTRY["lead.external_handoff"].lifecycle == JobLifecycle.DISABLED


def test_sensitive_flags_fail_closed_without_explicit_owner_approval():
    assert FeatureFlags({}).enabled(FeatureFlag.AI) is False
    assert FeatureFlags(
        {"ARTEMIS_EXTERNAL_WEBHOOKS_ENABLED": "true"}
    ).decision(FeatureFlag.EXTERNAL_WEBHOOKS).reason == (
        "explicit owner approval is required"
    )
    assert FeatureFlags(
        {
            "ARTEMIS_EXTERNAL_WEBHOOKS_ENABLED": "true",
            "ARTEMIS_EXTERNAL_WEBHOOKS_OWNER_APPROVED": "true",
        }
    ).enabled(FeatureFlag.EXTERNAL_WEBHOOKS) is True


def test_idempotency_store_replays_matching_payload_and_rejects_conflicts():
    store: IdempotencyStore[str] = IdempotencyStore()
    first_payload = LeadInput(**lead_payload())
    second_payload = first_payload.model_copy(update={"organization_name": "Different Example"})
    calls = 0

    def operation() -> str:
        nonlocal calls
        calls += 1
        return "qualified"

    assert store.execute("request-123", first_payload, operation).replayed is False
    assert store.execute("request-123", first_payload, operation).replayed is True
    assert calls == 1
    try:
        store.execute("request-123", second_payload, operation)
    except IdempotencyConflict:
        pass
    else:
        raise AssertionError("conflicting duplicate submission was accepted")


def test_qualification_requires_idempotency_and_propagates_correlation(monkeypatch):
    monkeypatch.delenv("ARTEMIS_EXTERNAL_WEBHOOKS_ENABLED", raising=False)
    lead = LeadInput(**lead_payload())
    try:
        qualify(lead, Response(), None)
    except HTTPException as error:
        assert error.status_code == 400
    else:
        raise AssertionError("qualification accepted a missing idempotency key")

    assert start_correlation("correlation-123") == "correlation-123"
    first_response = Response()
    replay_response = Response()
    first = qualify(lead, first_response, "qualification-123")
    replay = qualify(lead, replay_response, "qualification-123")
    assert first_response.headers["idempotency-replayed"] == "false"
    assert replay_response.headers["idempotency-replayed"] == "true"
    assert replay == first
    assert first.handoff is None


def test_readiness_and_job_monitoring_report_registered_jobs(monkeypatch):
    assert readyz() == {"status": "ready", "registered_jobs": 3}
    response = Response()
    monkeypatch.delenv("ARTEMIS_OPERATOR_MONITORING_KEY", raising=False)
    try:
        jobs(response, None)
    except HTTPException as error:
        assert error.status_code == 503
    else:
        raise AssertionError("monitoring route was enabled without configuration")

    monkeypatch.setenv("ARTEMIS_OPERATOR_MONITORING_KEY", "synthetic-operator-key")
    try:
        jobs(response, "incorrect-key")
    except HTTPException as error:
        assert error.status_code == 403
    else:
        raise AssertionError("monitoring route accepted an unauthorized operator")
    assert {job["name"] for job in jobs(response, "synthetic-operator-key")} == set(
        JOB_REGISTRY
    )
    assert response.headers["x-robots-tag"] == "noindex, nofollow"
