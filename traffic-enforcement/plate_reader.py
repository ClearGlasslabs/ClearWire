"""License-plate reading from a vehicle crop.

Uses EasyOCR when available. The OCR engine and its models are loaded lazily so
the package stays importable without the dependency; ``read_plate`` degrades to
returning ``None`` rather than raising when OCR is unavailable.
"""

from __future__ import annotations

import re

_PLATE_RE = re.compile(r"[A-Z0-9]{4,8}")


class PlateReader:
    def __init__(self, languages=("en",)):
        self._reader = None
        self._languages = list(languages)
        self._unavailable = False

    def _ensure(self):
        if self._reader is None and not self._unavailable:
            try:
                import easyocr  # deferred heavy import
                self._reader = easyocr.Reader(self._languages, gpu=False)
            except Exception:
                self._unavailable = True

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"[^A-Z0-9]", "", text.upper())

    def read_plate(self, vehicle_crop):
        """Return (plate_text, confidence) for the best candidate, or None."""
        self._ensure()
        if self._reader is None or vehicle_crop is None or vehicle_crop.size == 0:
            return None

        best = None
        for _, text, conf in self._reader.readtext(vehicle_crop):
            cleaned = self._normalize(text)
            for match in _PLATE_RE.findall(cleaned):
                if best is None or conf > best[1]:
                    best = (match, float(conf))
        return best
