from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

from .feature_flags import FeatureFlag


class JobLifecycle(StrEnum):
    LOADING = "loading"
    RETRYING = "retrying"
    DELAYED = "delayed"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"
    DISABLED = "disabled"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    READY = "ready"


@dataclass(frozen=True)
class RetryPolicy:
    maximum_attempts: int
    backoff_seconds: tuple[int, ...]


@dataclass(frozen=True)
class JobDefinition:
    name: str
    purpose: str
    owner: str
    trigger: str
    lifecycle: JobLifecycle
    feature_flag: FeatureFlag | None
    timeout_seconds: int
    retry: RetryPolicy
    idempotency: str
    retention: str
    audit_required: bool
    rollback: str


_JOBS = {
    "incident.evaluate": JobDefinition(
        name="incident.evaluate",
        purpose="Create a policy-constrained incident decision package.",
        owner="ClearGlassInc Artemis incident operations owner",
        trigger="POST /v1/incidents/evaluate",
        lifecycle=JobLifecycle.READY,
        feature_flag=None,
        timeout_seconds=5,
        retry=RetryPolicy(1, ()),
        idempotency="Deterministic incident ID derived from tenant and signal ID.",
        retention="Audit sink policy; no local persistence.",
        audit_required=True,
        rollback="Revert the operations module and API registry endpoint; no data migration is involved.",
    ),
    "lead.qualify": JobDefinition(
        name="lead.qualify",
        purpose="Produce a deterministic, fixed-catalog lead qualification.",
        owner="ClearGlassInc Artemis revenue operations owner",
        trigger="POST /v1/qualify",
        lifecycle=JobLifecycle.READY,
        feature_flag=None,
        timeout_seconds=5,
        retry=RetryPolicy(1, ()),
        idempotency="Idempotency-Key required and cached for duplicate submissions.",
        retention="In-process results expire after 15 minutes; durable retention belongs at the authorized edge.",
        audit_required=True,
        rollback="Remove the idempotency dependency and restore the prior route signature.",
    ),
    "lead.external_handoff": JobDefinition(
        name="lead.external_handoff",
        purpose="Deliver an eligible lead to an operator-controlled HTTPS endpoint.",
        owner="ClearGlassInc Artemis revenue operations owner",
        trigger="Eligible lead qualification with recorded consent.",
        lifecycle=JobLifecycle.DISABLED,
        feature_flag=FeatureFlag.EXTERNAL_WEBHOOKS,
        timeout_seconds=5,
        retry=RetryPolicy(1, ()),
        idempotency="Upstream lead qualification Idempotency-Key.",
        retention="No local payload persistence.",
        audit_required=True,
        rollback="Unset ARTEMIS_EXTERNAL_WEBHOOKS_ENABLED and ARTEMIS_EXTERNAL_WEBHOOKS_OWNER_APPROVED.",
    ),
}

JOB_REGISTRY: Mapping[str, JobDefinition] = MappingProxyType(_JOBS)


def public_registry() -> list[dict[str, object]]:
    return [
        {
            "name": job.name,
            "owner": job.owner,
            "trigger": job.trigger,
            "lifecycle": job.lifecycle,
            "feature_flag": job.feature_flag,
            "timeout_seconds": job.timeout_seconds,
            "maximum_attempts": job.retry.maximum_attempts,
            "idempotency": job.idempotency,
            "retention": job.retention,
            "audit_required": job.audit_required,
            "rollback": job.rollback,
        }
        for job in JOB_REGISTRY.values()
    ]
