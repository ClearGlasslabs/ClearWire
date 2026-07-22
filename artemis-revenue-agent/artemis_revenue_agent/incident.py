from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class LifecycleStage(StrEnum):
    DETECT = "detect"
    VALIDATE = "validate"
    CORRELATE = "correlate"
    CLASSIFY = "classify"
    CONTAIN = "contain"
    PLAN = "plan"
    AUTHORIZE = "authorize"
    EXECUTE = "execute"
    VERIFY = "verify"
    MONITOR = "monitor"
    CLOSE = "close"
    ROLLBACK = "rollback"
    ESCALATE = "escalate"


class SignalSeverity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionImpact(StrEnum):
    READ_ONLY = "read_only"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Evidence(BaseModel):
    source: str = Field(min_length=2, max_length=120)
    reference: str = Field(min_length=2, max_length=240)
    observed_at: datetime
    summary: str = Field(min_length=3, max_length=1000)
    confidence: float = Field(ge=0, le=1)


class SignalInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    tenant_id: str = Field(min_length=3, max_length=80)
    signal_id: str = Field(min_length=3, max_length=120)
    source: str = Field(min_length=2, max_length=120)
    summary: str = Field(min_length=5, max_length=1000)
    severity: SignalSeverity
    asset_ids: list[str] = Field(default_factory=list, max_length=50)
    dependency_ids: list[str] = Field(default_factory=list, max_length=50)
    evidence: list[Evidence] = Field(min_length=1, max_length=25)
    received_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PolicyContext(BaseModel):
    actor_id: str = Field(min_length=2, max_length=120)
    tenant_id: str = Field(min_length=3, max_length=80)
    roles: list[str] = Field(default_factory=list, max_length=20)
    automation_kill_switch_enabled: bool = False
    high_impact_approval: bool = False
    max_blast_radius: int = Field(default=10, ge=0, le=10_000)


class RecoveryAction(BaseModel):
    action_id: str
    title: str
    impact: ActionImpact
    scope: list[str]
    idempotency_key: str
    timeout_seconds: int = Field(ge=1, le=3600)
    max_retries: int = Field(ge=0, le=5)
    rollback_strategy: str
    requires_human_approval: bool


class IncidentDecision(BaseModel):
    incident_id: str
    tenant_id: str
    current_stage: LifecycleStage
    classification: Literal[
        "noise",
        "availability_degradation",
        "security_suspicious",
        "security_incident",
        "data_integrity",
        "revenue_risk",
    ]
    severity: SignalSeverity
    confidence: float = Field(ge=0, le=1)
    blast_radius: int = Field(ge=0)
    correlated_assets: list[str]
    dependency_graph: dict[str, list[str]]
    recommended_actions: list[RecoveryAction]
    policy_denials: list[str]
    audit_receipt: str
    ai_assistance_used: bool = False
    lifecycle: list[LifecycleStage]


_SECRET = b"artemis-local-audit-receipt-v1"


def _receipt(payload: dict) -> str:
    body = json.dumps(
        payload, default=str, sort_keys=True, separators=(",", ":")
    ).encode()
    return hmac.new(_SECRET, body, hashlib.sha256).hexdigest()


def _classification(signal: SignalInput) -> tuple[str, float]:
    text = f"{signal.source} {signal.summary}".lower()
    if any(
        token in text
        for token in ("exfil", "ransom", "malware", "credential", "unauthorized")
    ):
        return "security_incident", 0.9
    if any(
        token in text
        for token in ("failed payment", "checkout", "revenue", "conversion")
    ):
        return "revenue_risk", 0.82
    if any(
        token in text for token in ("latency", "timeout", "5xx", "down", "unavailable")
    ):
        return "availability_degradation", 0.84
    if any(token in text for token in ("checksum", "corrupt", "mismatch")):
        return "data_integrity", 0.86
    if signal.severity in {SignalSeverity.HIGH, SignalSeverity.CRITICAL}:
        return "security_suspicious", 0.7
    return "noise", 0.64


def _action_for(
    signal: SignalInput, classification: str, policy: PolicyContext
) -> RecoveryAction:
    scope = sorted(set(signal.asset_ids or [signal.signal_id]))[
        : policy.max_blast_radius
    ]
    impact = (
        ActionImpact.HIGH
        if classification == "security_incident"
        else ActionImpact.MEDIUM
    )
    if classification in {"noise", "security_suspicious"}:
        impact = ActionImpact.READ_ONLY
    key_source = (
        f"{signal.tenant_id}:{signal.signal_id}:{classification}:{','.join(scope)}"
    )
    return RecoveryAction(
        action_id=f"act_{uuid4().hex[:12]}",
        title=(
            "Contain affected scope before remediation"
            if impact == ActionImpact.HIGH
            else "Open verified investigation package"
        ),
        impact=impact,
        scope=scope,
        idempotency_key=hashlib.sha256(key_source.encode()).hexdigest(),
        timeout_seconds=300,
        max_retries=2,
        rollback_strategy="Release containment lease and restore previous routing policy after independent verification.",
        requires_human_approval=impact in {ActionImpact.MEDIUM, ActionImpact.HIGH},
    )


def evaluate_signal(signal: SignalInput, policy: PolicyContext) -> IncidentDecision:
    if signal.tenant_id != policy.tenant_id:
        raise ValueError("policy tenant must match signal tenant")
    classification, confidence = _classification(signal)
    blast_radius = len(set(signal.asset_ids + signal.dependency_ids))
    action = _action_for(signal, classification, policy)
    denials: list[str] = []
    if policy.automation_kill_switch_enabled:
        denials.append("Automation kill switch is enabled")
    if blast_radius > policy.max_blast_radius:
        denials.append("Blast radius exceeds policy ceiling")
    if action.requires_human_approval and not policy.high_impact_approval:
        denials.append("Human approval token is required before execution")
    if (
        "incident_operator" not in policy.roles
        and action.impact != ActionImpact.READ_ONLY
    ):
        denials.append("Actor lacks incident_operator role for non-read-only action")

    lifecycle = [
        LifecycleStage.DETECT,
        LifecycleStage.VALIDATE,
        LifecycleStage.CORRELATE,
        LifecycleStage.CLASSIFY,
        LifecycleStage.CONTAIN,
        LifecycleStage.PLAN,
        LifecycleStage.AUTHORIZE,
    ]
    if denials:
        lifecycle.append(LifecycleStage.ESCALATE)
    else:
        lifecycle.extend(
            [
                LifecycleStage.EXECUTE,
                LifecycleStage.VERIFY,
                LifecycleStage.MONITOR,
                LifecycleStage.CLOSE,
            ]
        )

    incident_id = f"inc_{hashlib.sha256(f'{signal.tenant_id}:{signal.signal_id}'.encode()).hexdigest()[:16]}"
    graph = {
        asset: sorted(set(signal.dependency_ids))
        for asset in sorted(set(signal.asset_ids))
    }
    receipt_payload = {
        "incident_id": incident_id,
        "tenant_id": signal.tenant_id,
        "signal_id": signal.signal_id,
        "classification": classification,
        "actor_id": policy.actor_id,
        "denials": denials,
        "evidence": [item.model_dump(mode="json") for item in signal.evidence],
    }
    return IncidentDecision(
        incident_id=incident_id,
        tenant_id=signal.tenant_id,
        current_stage=lifecycle[-1],
        classification=classification,
        severity=signal.severity,
        confidence=confidence,
        blast_radius=blast_radius,
        correlated_assets=sorted(set(signal.asset_ids)),
        dependency_graph=graph,
        recommended_actions=[action],
        policy_denials=denials,
        audit_receipt=_receipt(receipt_payload),
        lifecycle=lifecycle,
    )
