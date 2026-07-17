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
