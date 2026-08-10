from __future__ import annotations

import os
import secrets

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request, Response
from pydantic import BaseModel

from .engine import RevenueAgent
from .feature_flags import FeatureFlag, FeatureFlags
from .handoff import HandoffReceipt, deliver_handoff
from .idempotency import IdempotencyConflict, IdempotencyStore
from .incident import IncidentDecision, PolicyContext, SignalInput, evaluate_signal
from .observability import record, start_correlation
from .operations import public_registry
from .schemas import LeadInput, QualificationResult

app = FastAPI(
    title="ClearGlass ARTEMIS Revenue Agent",
    version="1.0.0",
    description="Ontario-focused fixed-scope cybersecurity qualification, lead scoring, and human handoff.",
)
agent = RevenueAgent()


class QualificationEnvelope(BaseModel):
    result: QualificationResult
    handoff: HandoffReceipt | None = None


idempotency_store: IdempotencyStore[QualificationEnvelope] = IdempotencyStore()


@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    correlation_id = start_correlation(request.headers.get("X-Correlation-ID"))
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "artemis-revenue-agent"}


@app.get("/readyz")
def readyz() -> dict[str, object]:
    return {"status": "ready", "registered_jobs": len(public_registry())}


@app.get("/v1/operations/jobs")
def jobs(
    response: Response,
    operator_key: str | None = Header(default=None, alias="X-Operator-Key"),
) -> list[dict[str, object]]:
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    configured_key = os.getenv("ARTEMIS_OPERATOR_MONITORING_KEY")
    if configured_key is None:
        record("operations.monitor", "disabled")
        raise HTTPException(status_code=503, detail="operator monitoring is disabled")
    if operator_key is None or not secrets.compare_digest(operator_key, configured_key):
        record("operations.monitor", "denied")
        raise HTTPException(status_code=403, detail="operator authorization failed")
    record("operations.monitor", "succeeded")
    return public_registry()


@app.post("/v1/incidents/evaluate", response_model=IncidentDecision)
def evaluate_incident(signal: SignalInput, policy: PolicyContext) -> IncidentDecision:
    decision = evaluate_signal(signal, policy)
    record("incident.evaluate", "succeeded", incident_id=decision.incident_id)
    return decision


@app.post("/v1/qualify", response_model=QualificationEnvelope)
def qualify(
    lead: LeadInput,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> QualificationEnvelope:
    if idempotency_key is None:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")

    def operation() -> QualificationEnvelope:
        result = agent.qualify(lead)
        flags = FeatureFlags()
        handoff_allowed = flags.enabled(FeatureFlag.EXTERNAL_WEBHOOKS)
        receipt = (
            deliver_handoff(result)
            if handoff_allowed and result.score.band in {"hot", "qualified"}
            else None
        )
        record(
            "lead.qualify",
            "succeeded",
            external_handoff_enabled=handoff_allowed,
            score_band=result.score.band,
        )
        return QualificationEnvelope(result=result, handoff=receipt)

    try:
        cached = idempotency_store.execute(idempotency_key, lead, operation)
    except (ValueError, IdempotencyConflict) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    response.headers["Idempotency-Replayed"] = str(cached.replayed).lower()
    if cached.replayed:
        record("lead.qualify", "replayed")
    return cached.value


def run() -> None:
    uvicorn.run(
        "artemis_revenue_agent.api:app",
        host=os.getenv("ARTEMIS_HOST", "127.0.0.1"),
        port=int(os.getenv("ARTEMIS_PORT", "8080")),
        reload=False,
        proxy_headers=False,
    )


if __name__ == "__main__":
    run()
