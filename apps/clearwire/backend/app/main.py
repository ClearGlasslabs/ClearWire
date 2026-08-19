from __future__ import annotations

import hashlib
import hmac
import os
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

SECRET = os.getenv("PSEUDONYMIZATION_SECRET", "development-secret").encode()
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "30"))
ALLOW_PRECISE_LOCATION = os.getenv("ALLOW_PRECISE_LOCATION", "false").lower() == "true"

app = FastAPI(title="Clearwire API", version="1.0.0", docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])

class Technology(str, Enum):
    wifi = "wifi"
    ble = "ble"
    cellular = "cellular"
    iot = "iot"

class AuthorizationScope(BaseModel):
    scope_id: str = Field(min_length=8, max_length=128)
    label: str = Field(min_length=1, max_length=160)
    expires_at: datetime
    precise_location: bool = False

class Observation(BaseModel):
    observation_id: str
    technology: Technology
    identifier: str
    label: str
    signal_dbm: int = Field(ge=-120, le=0)
    channel: int | None = Field(default=None, ge=1, le=233)
    risk_score: int = Field(ge=0, le=100)
    observed_at: datetime
    lat: float | None = None
    lon: float | None = None
    scope_id: str

class ScanRequest(BaseModel):
    authorization: AuthorizationScope

class Provider(Protocol):
    def observe(self, scope: AuthorizationScope) -> list[Observation]: ...


def pseudonymize(value: str) -> str:
    return hmac.new(SECRET, value.encode(), hashlib.sha256).hexdigest()[:16]


def privacy_round(value: float | None, digits: int = 3) -> float | None:
    return None if value is None else round(value, digits)

class SensorSimulatorProvider:
    def observe(self, scope: AuthorizationScope) -> list[Observation]:
        now = datetime.now(timezone.utc)
        seed = [
            ("wifi", "corp-ap-01", "Authorized AP", -48, 36, 18),
            ("wifi", "lab-ap-02", "Lab AP", -67, 149, 31),
            ("ble", "sensor-therm-07", "Temperature Sensor", -61, None, 14),
            ("ble", "beacon-04", "Asset Beacon", -78, None, 42),
            ("iot", "camera-03", "Authorized IoT", -58, 6, 55),
        ]
        result: list[Observation] = []
        for idx, (tech, raw_id, label, signal, channel, risk) in enumerate(seed):
            precise = scope.precise_location and ALLOW_PRECISE_LOCATION
            lat = privacy_round(43.6828 + idx * 0.0008, 5 if precise else 3)
            lon = privacy_round(-79.4140 - idx * 0.0007, 5 if precise else 3)
            result.append(Observation(
                observation_id=f"sim-{idx+1:03d}", technology=Technology(tech),
                identifier=pseudonymize(raw_id), label=label, signal_dbm=signal,
                channel=channel, risk_score=risk, observed_at=now, lat=lat, lon=lon,
                scope_id=scope.scope_id))
        return result

provider: Provider = SensorSimulatorProvider()

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "clearwire-api", "time": datetime.now(timezone.utc).isoformat()}

@app.get("/api/v1/capabilities")
def capabilities() -> dict:
    return {"passive_only": True, "packet_content_capture": False, "credential_interception": False, "precise_location_enabled": ALLOW_PRECISE_LOCATION, "retention_days": RETENTION_DAYS}

@app.post("/api/v1/scans")
def scan(request: ScanRequest, http_request: Request, x_authorization_scope: str | None = Header(default=None)) -> dict:
    scope = request.authorization
    if x_authorization_scope != scope.scope_id:
        raise HTTPException(status_code=403, detail="Authorization scope header does not match request scope")
    if scope.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="Authorization scope has expired")
    observations = provider.observe(scope)
    return {"authorized_monitoring": True, "scope_id": scope.scope_id, "started_at": datetime.now(timezone.utc).isoformat(), "observation_count": len(observations), "observations": observations, "audit_event": {"action": "scan", "scope_id": scope.scope_id, "client": http_request.client.host if http_request.client else "unknown", "timestamp": time.time()}}

@app.get("/api/v1/observations")
def observations(scope_id: str) -> dict:
    scope = AuthorizationScope(scope_id=scope_id, label="API query", expires_at=datetime.now(timezone.utc).replace(year=datetime.now(timezone.utc).year + 1))
    return {"scope_id": scope_id, "authorized_monitoring": True, "observations": provider.observe(scope)}
