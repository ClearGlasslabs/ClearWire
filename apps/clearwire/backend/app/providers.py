from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Sequence

from .main import AuthorizationScope, Observation

class WiFiTelemetryProvider(Protocol):
    def observe(self, scope: AuthorizationScope) -> Sequence[Observation]: ...
class BluetoothTelemetryProvider(Protocol):
    def observe(self, scope: AuthorizationScope) -> Sequence[Observation]: ...
class CellularMetadataProvider(Protocol):
    def observe(self, scope: AuthorizationScope) -> Sequence[Observation]: ...
class IoTInventoryProvider(Protocol):
    def observe(self, scope: AuthorizationScope) -> Sequence[Observation]: ...
class PublicMapProvider(Protocol):
    def resolve(self, scope: AuthorizationScope) -> Sequence[dict]: ...
class CredentialExposureAuditProvider(Protocol):
    def aggregate(self, scope: AuthorizationScope, k: int) -> dict: ...
class SensorSimulatorProvider(Protocol):
    def observe(self, scope: AuthorizationScope) -> Sequence[Observation]: ...

@dataclass(frozen=True)
class DisabledProvider:
    name: str
    reason: str = 'No authorized integration configured'
    def observe(self, scope: AuthorizationScope) -> Sequence[Observation]:
        return []
