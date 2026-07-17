from __future__ import annotations

import json
import os
from pathlib import Path

from .schemas import (
    Concern,
    HandoffData,
    LeadInput,
    QualificationResult,
    ScoreBreakdown,
    ServiceOffering,
    Timeline,
)

EXPECTED_SERVICE_IDS = {
    "security-quick-audit",
    "m365-windows-hardening-sprint",
    "phipa-readiness-assessment",
    "automation-as-a-service",
}

DEFAULT_CATALOG = [
    ServiceOffering(
        service_id="security-quick-audit",
        title="Security Quick-Audit",
        price_cad=None,
        price_display="Approved fixed price required",
        positioning=(
            "A read-only posture review that establishes an evidence-backed "
            "security baseline and prioritized remediation path."
        ),
        benefits=[
            "Read-only posture review",
            "Prioritized findings and remediation plan",
            "Written, decision-ready output",
        ],
        allowed_concerns=[Concern.SECURITY_VISIBILITY, Concern.COMPLIANCE, Concern.OTHER],
    ),
    ServiceOffering(
        service_id="m365-windows-hardening-sprint",
        title="Microsoft 365 + Windows Hardening Sprint",
        price_cad=None,
        price_display="Approved fixed price required",
        positioning=(
            "A fixed-scope hardening engagement aligned to Microsoft 365, "
            "Entra ID, Windows controls, privilege reduction, and defensible "
            "configuration baselines."
        ),
        benefits=[
            "Microsoft 365 and Entra ID hardening priorities",
            "Privilege and configuration-risk reduction",
            "Documented implementation and remediation record",
        ],
        allowed_concerns=[Concern.MICROSOFT_365, Concern.INCIDENT],
        requires_human_review=True,
    ),
    ServiceOffering(
        service_id="phipa-readiness-assessment",
        title="PHIPA Readiness Assessment",
        price_cad=None,
        price_display="Approved fixed price required",
        positioning=(
            "An Ontario-focused readiness assessment for organizations "
            "responsible for personal health information and regulated "
            "health-sector workflows."
        ),
        benefits=[
            "PHIPA-focused control and evidence review",
            "Gap register with prioritized remediation actions",
            "Audit-ready findings and implementation roadmap",
        ],
        allowed_concerns=[Concern.PHIPA, Concern.COMPLIANCE],
        regulated_fit=True,
        requires_human_review=True,
    ),
    ServiceOffering(
        service_id="automation-as-a-service",
        title="Automation-as-a-Service",
        price_cad=None,
        price_display="Approved fixed price required",
        positioning=(
            "Human-governed automation for repeatable operational workflows, "
            "evidence capture, monitoring, and structured handoff."
        ),
        benefits=[
            "Human-in-the-loop workflow design",
            "Structured automation and monitoring plan",
            "Implementation roadmap with control boundaries",
        ],
        allowed_concerns=[Concern.AUTOMATION],
        requires_human_review=True,
    ),
]


class CatalogError(RuntimeError):
    pass


def _validate_catalog(catalog: list[ServiceOffering]) -> list[ServiceOffering]:
    service_ids = [item.service_id for item in catalog]
    if len(service_ids) != len(EXPECTED_SERVICE_IDS):
        raise CatalogError("ARTEMIS requires exactly four approved fixed-scope offerings")
    if len(set(service_ids)) != len(service_ids):
        raise CatalogError("ARTEMIS service identifiers must be unique")
    if set(service_ids) != EXPECTED_SERVICE_IDS:
        missing = sorted(EXPECTED_SERVICE_IDS - set(service_ids))
        unexpected = sorted(set(service_ids) - EXPECTED_SERVICE_IDS)
        raise CatalogError(
            f"ARTEMIS catalog identifiers are invalid; missing={missing}, unexpected={unexpected}"
        )
    return catalog


def load_catalog(path: str | Path | None = None) -> list[ServiceOffering]:
    configured = path or os.getenv("ARTEMIS_SERVICE_CATALOG")
    if not configured:
        return _validate_catalog(DEFAULT_CATALOG)

    selected = Path(configured)
    if not selected.is_file():
        raise CatalogError(f"service catalog not found: {selected}")

    payload = json.loads(selected.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise CatalogError("ARTEMIS service catalog must be a JSON array")
    return _validate_catalog([ServiceOffering.model_validate(item) for item in payload])


def _band(total: int) -> str:
    if total >= 80:
        return "hot"
    if total >= 60:
        return "qualified"
    if total >= 40:
        return "nurture"
    return "disqualify"


def _score(lead: LeadInput) -> ScoreBreakdown:
    if lead.budget_cad is None:
        budget = 10
    elif lead.budget_cad >= 5_000:
        budget = 25
    elif lead.budget_cad >= 2_000:
        budget = 18
    elif lead.budget_cad >= 1_000:
        budget = 10
    else:
        budget = 0

    authority = {
        "decision_maker": 25,
        "influencer": 15,
        "researcher": 5,
        "unknown": 10,
    }[lead.decision_role]

    timeline = {
        Timeline.IMMEDIATE: 25,
        Timeline.NEAR_TERM: 15,
        Timeline.LATER: 5,
        Timeline.UNKNOWN: 10,
    }[lead.timeline]

    risk = 5
    if lead.microsoft_365_users and lead.microsoft_365_users > 0:
        risk += 5
    if lead.primary_concern in {
        Concern.MICROSOFT_365,
        Concern.COMPLIANCE,
        Concern.PHIPA,
    }:
        risk += 5
    if lead.regulated_data or lead.government_entity:
        risk += 5
    if lead.active_incident:
        risk += 5
    risk = min(risk, 25)

    total = min(budget + authority + timeline + risk, 100)
    return ScoreBreakdown(
        budget_fit=budget,
        authority=authority,
        timeline=timeline,
        risk_and_fit=risk,
        total=total,
        band=_band(total),
    )


def _escalation_reasons(lead: LeadInput) -> list[str]:
    reasons: list[str] = []
    industry = lead.industry.lower()
    if lead.active_incident:
        reasons.append("Active security incident")
    if lead.government_entity or any(
        term in industry for term in ("government", "municipal", "public sector")
    ):
        reasons.append("Government or public-sector entity")
    if lead.regulated_data or any(
        term in industry
        for term in ("health", "hospital", "clinic", "finance", "bank", "insurance")
    ):
        reasons.append("Regulated or high-risk data environment")
    if lead.employee_count and lead.employee_count > 500:
        reasons.append("Enterprise-scale environment above 500 employees")
    return reasons


def _choose_service(lead: LeadInput, catalog: list[ServiceOffering]) -> ServiceOffering:
    by_id = {item.service_id: item for item in catalog}
    industry = lead.industry.lower()
    if (
        lead.primary_concern == Concern.PHIPA
        or lead.regulated_data
        or any(term in industry for term in ("health", "hospital", "clinic"))
    ):
        return by_id["phipa-readiness-assessment"]
    if lead.primary_concern == Concern.AUTOMATION:
        return by_id["automation-as-a-service"]
    if lead.primary_concern in {Concern.MICROSOFT_365, Concern.INCIDENT}:
        return by_id["m365-windows-hardening-sprint"]
    return by_id["security-quick-audit"]


def _next_step(service: ServiceOffering, escalations: list[str]) -> str:
    if escalations:
        return "Request a security briefing and human review before scope or pricing is issued."
    if service.service_id == "security-quick-audit":
        return "Start with a read-only posture review."
    if service.service_id == "m365-windows-hardening-sprint":
        return "Deploy a hardening sprint after written scope authorization."
    if service.service_id == "phipa-readiness-assessment":
        return "Book a fixed-scope PHIPA readiness assessment."
    return "Request a security briefing for a human-governed automation assessment."


class RevenueAgent:
    def __init__(self, catalog_path: str | Path | None = None):
        self.catalog = load_catalog(catalog_path)

    def qualify(self, lead: LeadInput) -> QualificationResult:
        service = _choose_service(lead, self.catalog)
        score = _score(lead)
        escalations = _escalation_reasons(lead)
        human_review = bool(escalations) or service.requires_human_review
        next_step = _next_step(service, escalations)

        summary = [
            f"Current pain: {lead.primary_concern.value}",
            (
                "Environment: "
                f"{lead.employee_count or 'unknown'} employees; "
                f"{lead.microsoft_365_users if lead.microsoft_365_users is not None else 'unknown'} "
                "Microsoft 365 users"
            ),
            f"Timeline: {lead.timeline.value}",
            (
                "Budget: not shared"
                if lead.budget_cad is None
                else f"Budget: CAD ${lead.budget_cad:,}"
            ),
            f"Decision role: {lead.decision_role}",
        ]

        notes = [
            *summary,
            f"Lead score: {score.total}/100 ({score.band})",
            f"CASL consent recorded: {'yes' if lead.consent_to_contact else 'no'}",
        ]
        if escalations:
            notes.append("Escalation: " + "; ".join(escalations))

        return QualificationResult(
            acknowledgment=(
                "ClearGlass Inc. provides mission-defined, evidence-driven "
                "cybersecurity engagements for Ontario organizations through "
                "fixed scope, written deliverables, and explicit authorization."
            ),
            qualification_summary=summary,
            recommended_offering=service,
            recommendation_reason=(
                f"{service.title} is the closest approved fixed-scope match for "
                "the stated concern. Final scope and any price require the "
                "approved service catalog and written authorization."
            ),
            next_step=next_step,
            score=score,
            escalation_reasons=escalations,
            handoff=HandoffData(
                lead_type=score.band,
                recommended_service=service.title,
                key_qualification_notes=notes,
                proposed_next_action=next_step,
                human_review_required=human_review,
            ),
            casl_contact_permitted=lead.consent_to_contact,
        )
