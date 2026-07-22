from __future__ import annotations

import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from .engine import RevenueAgent
from .handoff import HandoffReceipt, deliver_handoff
from .incident import IncidentDecision, PolicyContext, SignalInput, evaluate_signal
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


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "artemis-revenue-agent"}


@app.post("/v1/incidents/evaluate", response_model=IncidentDecision)
def evaluate_incident(signal: SignalInput, policy: PolicyContext) -> IncidentDecision:
    return evaluate_signal(signal, policy)


@app.post("/v1/qualify", response_model=QualificationEnvelope)
def qualify(lead: LeadInput) -> QualificationEnvelope:
    result = agent.qualify(lead)
    receipt = (
        deliver_handoff(result) if result.score.band in {"hot", "qualified"} else None
    )
    return QualificationEnvelope(result=result, handoff=receipt)


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
