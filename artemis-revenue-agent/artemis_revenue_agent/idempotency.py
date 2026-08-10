from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from threading import Lock
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class IdempotencyConflict(ValueError):
    pass


@dataclass(frozen=True)
class CachedResult(Generic[T]):
    value: T
    replayed: bool


class IdempotencyStore(Generic[T]):
    def __init__(self, ttl_seconds: int = 900, maximum_entries: int = 10_000) -> None:
        self._ttl_seconds = ttl_seconds
        self._maximum_entries = maximum_entries
        self._entries: dict[str, tuple[float, str, T]] = {}
        self._lock = Lock()

    def execute(self, key: str, payload: BaseModel, operation) -> CachedResult[T]:
        if not 8 <= len(key) <= 128:
            raise ValueError("Idempotency-Key must contain between 8 and 128 characters")
        digest = hashlib.sha256(
            json.dumps(payload.model_dump(mode="json"), sort_keys=True).encode()
        ).hexdigest()
        now = time.monotonic()
        with self._lock:
            self._entries = {
                entry_key: entry
                for entry_key, entry in self._entries.items()
                if now - entry[0] < self._ttl_seconds
            }
            existing = self._entries.get(key)
            if existing:
                if existing[1] != digest:
                    raise IdempotencyConflict("Idempotency-Key was reused with a different payload")
                return CachedResult(existing[2], True)
            value = operation()
            if len(self._entries) >= self._maximum_entries:
                oldest = min(self._entries, key=lambda item: self._entries[item][0])
                del self._entries[oldest]
            self._entries[key] = (now, digest, value)
            return CachedResult(value, False)
