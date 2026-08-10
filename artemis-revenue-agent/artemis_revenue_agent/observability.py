from __future__ import annotations

import json
import logging
from collections import Counter, deque
from contextvars import ContextVar
from uuid import uuid4

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="unassigned")
metrics: Counter[tuple[str, str]] = Counter()
audit_events: deque[dict[str, object]] = deque(maxlen=10_000)
logger = logging.getLogger("artemis.operations")


def start_correlation(requested: str | None) -> str:
    value = requested if requested and 8 <= len(requested) <= 128 else uuid4().hex
    correlation_id.set(value)
    return value


def record(job: str, outcome: str, **fields: object) -> None:
    metrics[(job, outcome)] += 1
    event = {
        "event": "job.completed",
        "job": job,
        "outcome": outcome,
        "correlation_id": correlation_id.get(),
        **fields,
    }
    audit_events.append(event)
    logger.info(json.dumps(event, sort_keys=True, default=str))
