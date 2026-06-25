"""Lightweight IoU tracker with per-track BEV speed estimation.

Detections are associated to existing tracks greedily by IoU. Each track keeps a
short history of BEV ground points so speed can be smoothed over several frames,
which suppresses the per-frame jitter that a single-frame delta would produce.
"""

from __future__ import annotations

from collections import deque

import config
from detector import Detection
from speed_estimator import SpeedEstimator


def _iou(a, b) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return inter / (area_a + area_b - inter)


class Track:
    __slots__ = ("id", "bbox", "cls", "age", "frame", "speed_kmh",
                 "_pts", "_frames", "max_speed_kmh")

    def __init__(self, track_id: int, det: Detection, frame_idx: int):
        self.id = track_id
        self.bbox = det.bbox
        self.cls = det.cls
        self.age = 0
        self.frame = frame_idx
        self.speed_kmh = 0.0
        self.max_speed_kmh = 0.0
        self._pts: deque = deque(maxlen=config.SPEED_SMOOTHING + 1)
        self._frames: deque = deque(maxlen=config.SPEED_SMOOTHING + 1)

    def update(self, det: Detection, frame_idx: int, estimator: SpeedEstimator):
        self.bbox = det.bbox
        self.cls = det.cls
        self.age = 0
        self.frame = frame_idx

        point = estimator.ground_point_metres(det.bbox)
        if point is not None:
            self._pts.append(point)
            self._frames.append(frame_idx)
            if len(self._pts) >= 2:
                samples = [
                    estimator.speed_kmh(self._pts[i - 1], self._pts[i],
                                        self._frames[i] - self._frames[i - 1])
                    for i in range(1, len(self._pts))
                ]
                self.speed_kmh = sum(samples) / len(samples)
                self.max_speed_kmh = max(self.max_speed_kmh, self.speed_kmh)


class VehicleTracker:
    def __init__(self, estimator: SpeedEstimator):
        self.estimator = estimator
        self.tracks: dict[int, Track] = {}
        self._next_id = 1

    def update(self, detections: list[Detection], frame_idx: int) -> list[Track]:
        for t in self.tracks.values():
            t.age += 1

        unmatched = set(self.tracks.keys())
        pairs = []
        for di, det in enumerate(detections):
            for tid, track in self.tracks.items():
                iou = _iou(det.bbox, track.bbox)
                if iou >= config.IOU_MATCH_THRESHOLD:
                    pairs.append((iou, di, tid))
        pairs.sort(reverse=True)

        used_dets: set[int] = set()
        for _, di, tid in pairs:
            if di in used_dets or tid not in unmatched:
                continue
            self.tracks[tid].update(detections[di], frame_idx, self.estimator)
            used_dets.add(di)
            unmatched.discard(tid)

        for di, det in enumerate(detections):
            if di in used_dets:
                continue
            track = Track(self._next_id, det, frame_idx)
            track.update(det, frame_idx, self.estimator)
            self.tracks[self._next_id] = track
            self._next_id += 1

        for tid in [t for t, tr in self.tracks.items()
                    if tr.age > config.MAX_TRACK_AGE]:
            del self.tracks[tid]

        return [t for t in self.tracks.values() if t.age == 0]
