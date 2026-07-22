from artemis_revenue_agent import LeadInput, RevenueAgent
from artemis_revenue_agent.schemas import Concern, Timeline


def test_quick_audit_is_default_for_visibility_gap():
    result = RevenueAgent().qualify(
        LeadInput(
            organization_name="Ontario Sample Manufacturing",
            industry="Manufacturing",
            location="Burlington, Ontario, Canada",
            employee_count=45,
            microsoft_365_users=38,
            decision_role="decision_maker",
            primary_concern=Concern.SECURITY_VISIBILITY,
            timeline=Timeline.NEAR_TERM,
            budget_cad=5000,
            consent_to_contact=True,
        )
    )
    assert result.recommended_offering.service_id == "security-quick-audit"
    assert result.score.total >= 60
    assert result.casl_contact_permitted is True
    assert result.engagement_requires_written_authorization is True


def test_healthcare_is_routed_to_phipa_and_human_review():
    result = RevenueAgent().qualify(
        LeadInput(
            organization_name="Ontario Sample Clinic",
            industry="Healthcare clinic",
            location="Hamilton, Ontario, Canada",
            employee_count=80,
            microsoft_365_users=72,
            decision_role="influencer",
            primary_concern=Concern.COMPLIANCE,
            regulated_data=True,
            timeline=Timeline.IMMEDIATE,
        )
    )
    assert result.recommended_offering.service_id == "phipa-readiness-assessment"
    assert result.handoff.human_review_required is True
    assert result.escalation_reasons


def test_m365_concern_routes_to_hardening_sprint():
    result = RevenueAgent().qualify(
        LeadInput(
            organization_name="Ontario Sample Legal",
            industry="Legal services",
            location="Toronto, Ontario, Canada",
            employee_count=25,
            microsoft_365_users=25,
            decision_role="decision_maker",
            primary_concern=Concern.MICROSOFT_365,
            timeline=Timeline.IMMEDIATE,
            budget_cad=7000,
        )
    )
    assert result.recommended_offering.service_id == "m365-windows-hardening-sprint"
    assert result.next_step.startswith("Deploy a hardening sprint")


def test_agent_never_invents_price():
    result = RevenueAgent().qualify(
        LeadInput(
            organization_name="Ontario Sample Non-Profit",
            industry="Non-profit",
            location="Ottawa, Ontario, Canada",
            primary_concern=Concern.OTHER,
        )
    )
    assert result.recommended_offering.price_cad is None
    assert "approved" in result.recommended_offering.price_display.lower()


from datetime import UTC, datetime

from artemis_revenue_agent.incident import (
    Evidence,
    PolicyContext,
    SignalInput,
    SignalSeverity,
    evaluate_signal,
)


def test_incident_evaluation_denies_high_impact_without_approval():
    signal = SignalInput(
        tenant_id="tenant-alpha",
        signal_id="sig-001",
        source="edr",
        summary="Credential theft and unauthorized access suspected on checkout admin host",
        severity=SignalSeverity.CRITICAL,
        asset_ids=["checkout-admin-1"],
        dependency_ids=["payments-api"],
        evidence=[
            Evidence(
                source="edr",
                reference="evt-1",
                observed_at=datetime.now(UTC),
                summary="Credential alert",
                confidence=0.91,
            )
        ],
    )
    decision = evaluate_signal(
        signal, PolicyContext(actor_id="analyst-1", tenant_id="tenant-alpha", roles=[])
    )
    assert decision.classification == "security_incident"
    assert decision.recommended_actions[0].requires_human_approval is True
    assert (
        "Human approval token is required before execution" in decision.policy_denials
    )
    assert decision.current_stage == "escalate"
    assert len(decision.audit_receipt) == 64


def test_incident_evaluation_executes_bounded_path_with_approval():
    signal = SignalInput(
        tenant_id="tenant-alpha",
        signal_id="sig-002",
        source="synthetic-monitor",
        summary="Checkout latency timeout rate breached revenue SLO",
        severity=SignalSeverity.HIGH,
        asset_ids=["checkout-web"],
        dependency_ids=["payments-api", "postgres-primary"],
        evidence=[
            Evidence(
                source="apm",
                reference="trace-1",
                observed_at=datetime.now(UTC),
                summary="Timeout spike",
                confidence=0.88,
            )
        ],
    )
    policy = PolicyContext(
        actor_id="incident-commander",
        tenant_id="tenant-alpha",
        roles=["incident_operator"],
        high_impact_approval=True,
        max_blast_radius=5,
    )
    decision = evaluate_signal(signal, policy)
    assert decision.classification == "revenue_risk"
    assert decision.policy_denials == []
    assert decision.current_stage == "close"
    assert decision.recommended_actions[0].max_retries == 2
    assert decision.dependency_graph == {
        "checkout-web": ["payments-api", "postgres-primary"]
    }
