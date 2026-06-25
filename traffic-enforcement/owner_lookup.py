"""Vehicle-owner identification from a plate registry.

In a production deployment this would query the vehicle-registration authority's
database. Here it reads a local JSON registry so the enforcement pipeline can be
demonstrated end to end. Lookups are normalised and tolerant of common OCR
confusions (O/0, I/1, B/8) so a slightly misread plate can still resolve.
"""

from __future__ import annotations

import json
import os

_OCR_CONFUSIONS = str.maketrans({"O": "0", "I": "1", "B": "8", "Z": "2", "S": "5"})


class OwnerRegistry:
    def __init__(self, path: str):
        self.path = path
        self._by_plate: dict[str, dict] = {}
        self._by_canonical: dict[str, dict] = {}
        if os.path.exists(path):
            self._load()

    @staticmethod
    def _canonical(plate: str) -> str:
        return plate.upper().replace(" ", "").translate(_OCR_CONFUSIONS)

    def _load(self):
        with open(self.path, encoding="utf-8") as fh:
            data = json.load(fh)
        for plate, owner in data.items():
            key = plate.upper().replace(" ", "")
            self._by_plate[key] = owner
            self._by_canonical[self._canonical(plate)] = owner

    def lookup(self, plate: str):
        """Return the owner record for a plate, tolerating OCR confusions."""
        if not plate:
            return None
        key = plate.upper().replace(" ", "")
        if key in self._by_plate:
            return self._by_plate[key]
        return self._by_canonical.get(self._canonical(plate))
