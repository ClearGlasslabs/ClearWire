from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


class FeatureFlag(StrEnum):
    AI = "ai"
    EMAIL = "email"
    BILLING = "billing"
    LIVE_DATA = "live_data"
    BLUE_TEAM_ADAPTERS = "blue_team_adapters"
    EXTERNAL_WEBHOOKS = "external_webhooks"


@dataclass(frozen=True)
class FeatureDecision:
    flag: FeatureFlag
    enabled: bool
    reason: str


class FeatureFlags:
    def __init__(self, environment: Mapping[str, str] | None = None) -> None:
        self._environment = environment if environment is not None else os.environ

    def decision(self, flag: FeatureFlag) -> FeatureDecision:
        prefix = f"ARTEMIS_{flag.value.upper()}"
        requested = self._environment.get(f"{prefix}_ENABLED") == "true"
        approved = self._environment.get(f"{prefix}_OWNER_APPROVED") == "true"
        if not requested:
            return FeatureDecision(flag, False, "disabled by default")
        if not approved:
            return FeatureDecision(flag, False, "explicit owner approval is required")
        return FeatureDecision(flag, True, "enabled with explicit owner approval")

    def enabled(self, flag: FeatureFlag) -> bool:
        return self.decision(flag).enabled
