"""End-to-end traffic speed enforcement pipeline.

Frame loop:
  1. detect vehicles                       (detector)
  2. associate to tracks, estimate speed   (tracker + BEV speed_estimator)
  3. classify speed and annotate frame     (colour-coded boxes + labels + legend)
  4. on over-limit: read plate, look up owner, record clip + report  (recorder)
"""

from __future__ import annotations

import cv2

import config
from detector import VehicleDetector
from owner_lookup import OwnerRegistry
from plate_reader import PlateReader
from recorder import ViolationRecorder
from speed_estimator import SpeedEstimator, speed_color
from tracker import VehicleTracker

_LEGEND = [
    ("< 60 km/h", config.COLOR_SLOW),
    ("60-100 km/h", config.COLOR_MID),
    ("> 100 km/h", config.COLOR_FAST),
]


def _draw_legend(frame):
    x, y = 12, 30
    for i, (text, color) in enumerate(_LEGEND):
        top = y + i * 26
        cv2.rectangle(frame, (x, top), (x + 18, top + 18), color, -1)
        cv2.putText(frame, text, (x + 26, top + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)


def _draw_track(frame, track):
    x1, y1, x2, y2 = (int(v) for v in track.bbox)
    color = speed_color(track.speed_kmh)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    label = f"Car ({track.speed_kmh:.0f} km/h)"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 6, y1), color, -1)
    cv2.putText(frame, label, (x1 + 3, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA)


class EnforcementSystem:
    def __init__(self, detector=None, plate_reader=None, owner_registry=None):
        self.detector = detector or VehicleDetector()
        self.plate_reader = plate_reader or PlateReader()
        self.owners = owner_registry or OwnerRegistry(config.OWNER_REGISTRY)

    def process_video(self, source, output_path=None, show=False):
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError(f"could not open video source: {source}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        estimator = SpeedEstimator(fps)
        tracker = VehicleTracker(estimator)
        recorder = ViolationRecorder(config.VIOLATION_DIR, fps, (w, h))

        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        violations = []
        frame_idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            raw = frame.copy()

            detections = self.detector.detect(raw)
            active = tracker.update(detections, frame_idx)

            violators = [
                t for t in active
                if t.speed_kmh > config.SPEED_LIMIT_KMH
                and not recorder.already_recorded(t.id)
            ]

            for track in active:
                _draw_track(frame, track)
            _draw_legend(frame)

            for track in violators:
                violations.append(self._handle_violation(
                    recorder, raw, track, frame_idx))

            recorder.push_frame(frame)
            if writer is not None:
                writer.write(frame)
            if show:
                cv2.imshow("enforcement", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            frame_idx += 1

        recorder.close()
        cap.release()
        if writer is not None:
            writer.release()
        if show:
            cv2.destroyAllWindows()
        return violations

    def _handle_violation(self, recorder, raw_frame, track, frame_idx):
        x1, y1, x2, y2 = (int(v) for v in track.bbox)
        crop = raw_frame[max(0, y1):max(0, y2), max(0, x1):max(0, x2)]
        plate = self.plate_reader.read_plate(crop)
        owner = self.owners.lookup(plate[0]) if plate else None
        return recorder.record(track, raw_frame, frame_idx, plate, owner)
