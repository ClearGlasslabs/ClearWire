from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Timeline(StrEnum):
    IMMEDIATE = "0-30 days"
    NEAR_TERM = "30-90 days"
    LATER = "90+ days"
    UNKNOWN = "unknown"


class Concern(StrEnum):
    SECURITY_VISIBILITY = "security_visibility"
    MICROSOFT_365 = "microsoft_365_security"
    PHIPA = "phipa_readiness"
    AUTOMATION = "process_automation"
    COMPLIANCE = "compliance_requirements"
    INCIDENT = "recent_security_incident"
    OTHER = "other"


class LeadInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    organization_name: str = Field(min_length=2, max_length=200)
    contact_name: str | None = Field(default=None, max_length=160)
    contact_email: EmailStr | None = None
    industry: str = Field(min_length=2, max_length=120)
    location: str = Field(default="Ontario, Canada", max_length=160)
    employee_count: int | None = Field(default=None, ge=1, le=1_000_000)
    microsoft_365_users: int | None = Field(default=None, ge=0, le=1_000_000)
    decision_role: Literal["decision_maker", "influencer", "researcher", "unknown"] = "unknown"
    primary_concern: Concern
    timeline: Timeline = Timeline.UNKNOWN
    budget_cad: int | None = Field(default=None, ge=0, le=100_000_000)
    current_security_tools: list[str] = Field(default_factory=list, max_length=50)
    cyber_insurance: bool | None = None
    active_incident: bool = False
    government_entity: bool = False
    regulated_data: bool = False
    notes: str | None = Field(default=None, max_length=4000)
    consent_to_contact: bool = False

    @field_validator("location")
    @classmethod
    def require_canadian_context(cls, value: str) -> str:
        if not any(token in value.lower() for token in ("ontario", "canada", "on,")):
            raise ValueError("ARTEMIS is currently scoped to Ontario/Canadian engagements")
        return value


class ServiceOffering(BaseModel):
    service_id: str
    title: str
    price_cad: int | None = Field(default=None, ge=0)
    price_display: str
    positioning: str
    benefits: list[str] = Field(min_length=2, max_length=6)
    allowed_concerns: list[Concern]
    regulated_fit: bool = False
    requires_human_review: bool = False


class ScoreBreakdown(BaseModel):
    budget_fit: int = Field(ge=0, le=25)
    authority: int = Field(ge=0, le=25)
    timeline: int = Field(ge=0, le=25)
    risk_and_fit: int = Field(ge=0, le=25)
    total: int = Field(ge=0, le=100)
    band: Literal["hot", "qualified", "nurture", "disqualify"]


class HandoffData(BaseModel):
    lead_type: str
    recommended_service: str
    key_qualification_notes: list[str]
    proposed_next_action: str
    human_review_required: bool


class QualificationResult(BaseModel):
    acknowledgment: str
    qualification_summary: list[str]
    recommended_offering: ServiceOffering
    recommendation_reason: str
    next_step: str
    score: ScoreBreakdown
    escalation_reasons: list[str]
    handoff: HandoffData
    casl_contact_permitted: bool
    engagement_requires_written_authorization: bool = True
