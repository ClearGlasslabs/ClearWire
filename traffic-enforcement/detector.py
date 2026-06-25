"""Vehicle detection wrapper around Ultralytics YOLO.

The heavy import and model load are deferred so the rest of the package can be
imported (and unit-tested) on machines without the weights or a GPU.
"""

from __future__ import annotations

from dataclasses import dataclass

import config


@dataclass
class Detection:
    bbox: tuple[float, float, float, float]   # x1, y1, x2, y2
    confidence: float
    cls: int


class VehicleDetector:
    def __init__(self, weights: str = config.MODEL_WEIGHTS,
                 conf: float = config.CONF_THRESHOLD):
        from ultralytics import YOLO  # deferred heavy import

        self.model = YOLO(weights)
        self.conf = conf

    def detect(self, frame) -> list[Detection]:
        results = self.model(frame, conf=self.conf, verbose=False)[0]
        detections: list[Detection] = []
        for box in results.boxes:
            cls = int(box.cls[0])
            if cls not in config.VEHICLE_CLASSES:
                continue
            x1, y1, x2, y2 = (float(v) for v in box.xyxy[0])
            detections.append(Detection((x1, y1, x2, y2), float(box.conf[0]), cls))
        return detections
