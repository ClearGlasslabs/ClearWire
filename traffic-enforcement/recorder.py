"""Violation recording: writes an annotated clip, a plate crop and a JSON report
for each over-limit vehicle.

A rolling buffer of recent frames means the clip can include context from *before*
the violation was confirmed, not just the frames after it.
"""

from __future__ import annotations

import json
import os
from collections import deque
from datetime import datetime, timezone

import cv2

import config


class ViolationRecorder:
    def __init__(self, out_dir: str, fps: float, frame_size: tuple[int, int]):
        self.out_dir = out_dir
        self.fps = fps
        self.frame_size = frame_size
        os.makedirs(out_dir, exist_ok=True)
        self._buffer: deque = deque(maxlen=config.CLIP_PADDING_FRAMES)
        self._recorded_tracks: set[int] = set()

    def push_frame(self, frame):
        self._buffer.append(frame.copy())

    def already_recorded(self, track_id: int) -> bool:
        return track_id in self._recorded_tracks

    def record(self, track, frame, frame_idx, plate, owner, after_frames):
        """Persist a violation. ``after_frames`` are frames following the event."""
        self._recorded_tracks.add(track.id)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        stem = f"violation_{ts}_track{track.id}"

        clip_path = os.path.join(self.out_dir, f"{stem}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(clip_path, fourcc, self.fps, self.frame_size)
        for f in list(self._buffer) + list(after_frames):
            writer.write(f)
        writer.release()

        plate_path = None
        x1, y1, x2, y2 = (int(v) for v in track.bbox)
        crop = frame[max(0, y1):y2, max(0, x1):x2]
        if crop.size:
            plate_path = os.path.join(self.out_dir, f"{stem}_vehicle.jpg")
            cv2.imwrite(plate_path, crop)

        report = {
            "track_id": track.id,
            "recorded_at": ts,
            "frame_index": frame_idx,
            "speed_kmh": round(track.speed_kmh, 1),
            "max_speed_kmh": round(track.max_speed_kmh, 1),
            "speed_limit_kmh": config.SPEED_LIMIT_KMH,
            "over_limit_kmh": round(track.max_speed_kmh - config.SPEED_LIMIT_KMH, 1),
            "license_plate": plate[0] if plate else None,
            "plate_confidence": round(plate[1], 3) if plate else None,
            "owner": owner,
            "clip": os.path.basename(clip_path),
            "vehicle_image": os.path.basename(plate_path) if plate_path else None,
        }
        report_path = os.path.join(self.out_dir, f"{stem}.json")
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        return report
