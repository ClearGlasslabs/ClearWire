from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .schemas import QualificationResult


@dataclass(frozen=True)
class HandoffReceipt:
    delivered: bool
    status_code: int | None
    reason: str


def _validated_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1"}:
        raise ValueError("ARTEMIS handoff webhook must use HTTPS")
    if not parsed.netloc:
        raise ValueError("ARTEMIS handoff webhook URL is invalid")
    return value


def deliver_handoff(result: QualificationResult) -> HandoffReceipt:
    """Deliver a qualified lead to an operator-controlled endpoint.

    Delivery is disabled unless a webhook URL is configured and CASL consent is
    recorded. Payloads are signed when ARTEMIS_HANDOFF_SECRET is set.
    """
    endpoint = os.getenv("ARTEMIS_HANDOFF_WEBHOOK_URL")
    if not endpoint:
        return HandoffReceipt(False, None, "handoff webhook not configured")
    if not result.casl_contact_permitted:
        return HandoffReceipt(False, None, "CASL contact consent not recorded")

    endpoint = _validated_url(endpoint)
    body = result.model_dump_json().encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "ClearGlass-ARTEMIS/1.0"}

    secret = os.getenv("ARTEMIS_HANDOFF_SECRET")
    if secret:
        signature = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        headers["X-ARTEMIS-Signature-SHA256"] = signature

    request = Request(endpoint, data=body, headers=headers, method="POST")
    try:
        with urlopen(request, timeout=5) as response:  # noqa: S310 - URL is admin-configured and validated
            status = int(response.status)
        return HandoffReceipt(200 <= status < 300, status, "delivered" if status < 300 else "remote endpoint rejected payload")
    except Exception as exc:  # network failures must not break qualification
        return HandoffReceipt(False, None, f"handoff failed: {type(exc).__name__}")
