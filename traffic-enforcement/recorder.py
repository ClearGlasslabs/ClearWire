"""Violation recording: writes an annotated clip, a plate crop and a JSON report
for each over-limit vehicle.

Clips are recorded in a deferred, streaming fashion. When a violation is
confirmed the recorder emits the rolling buffer of recent annotated frames (the
pre-event context), then keeps appending each subsequent frame the main loop
produces until the post-event window is filled. This avoids reading ahead on the
capture device inside the detection loop, which would desynchronise frame
indexing and the tracker's speed estimation.
"""

from __future__ import annotations

import json
import os
from collections import deque
from datetime import datetime, timezone

import cv2

import config


class _PendingClip:
    __slots__ = ("writer", "frames_left", "report", "report_path")

    def __init__(self, writer, frames_left, report, report_path):
        self.writer = writer
        self.frames_left = frames_left
        self.report = report
        self.report_path = report_path


class ViolationRecorder:
    def __init__(self, out_dir: str, fps: float, frame_size: tuple[int, int]):
        self.out_dir = out_dir
        self.fps = fps
        self.frame_size = frame_size
        os.makedirs(out_dir, exist_ok=True)
        self._buffer: deque = deque(maxlen=config.CLIP_PADDING_FRAMES)
        self._recorded_tracks: set[int] = set()
        self._pending: list[_PendingClip] = []

    def push_frame(self, frame):
        """Feed one annotated frame: buffer it and advance any open clips."""
        self._buffer.append(frame)
        still_open = []
        for clip in self._pending:
            clip.writer.write(frame)
            clip.frames_left -= 1
            if clip.frames_left <= 0:
                self._finalize(clip)
            else:
                still_open.append(clip)
        self._pending = still_open

    def already_recorded(self, track_id: int) -> bool:
        return track_id in self._recorded_tracks

    def record(self, track, raw_frame, frame_idx, plate, owner):
        """Open a violation clip and report. ``raw_frame`` is the un-annotated
        frame, used for the vehicle/plate crop so detection overlays don't bleed
        into the OCR image. Returns the report immediately; the clip and report
        file are finalised once the post-event window fills (or on close)."""
        self._recorded_tracks.add(track.id)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        stem = f"violation_{ts}_track{track.id}"

        clip_path = os.path.join(self.out_dir, f"{stem}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(clip_path, fourcc, self.fps, self.frame_size)
        for f in self._buffer:
            writer.write(f)

        vehicle_image = None
        x1, y1, x2, y2 = (int(v) for v in track.bbox)
        crop = raw_frame[max(0, y1):max(0, y2), max(0, x1):max(0, x2)]
        if crop.size:
            vehicle_image = f"{stem}_vehicle.jpg"
            cv2.imwrite(os.path.join(self.out_dir, vehicle_image), crop)

        report = {
            "track_id": track.id,
            "recorded_at": ts,
            "frame_index": frame_idx,
            "speed_kmh": round(track.speed_kmh, 1),
            "max_speed_kmh": round(track.max_speed_kmh, 1),
            "speed_limit_kmh": config.SPEED_LIMIT_KMH,
            "over_limit_kmh": round(track.speed_kmh - config.SPEED_LIMIT_KMH, 1),
            "license_plate": plate[0] if plate else None,
            "plate_confidence": round(plate[1], 3) if plate else None,
            "owner": owner,
            "clip": os.path.basename(clip_path),
            "vehicle_image": vehicle_image,
        }
        report_path = os.path.join(self.out_dir, f"{stem}.json")
        self._pending.append(
            _PendingClip(writer, config.CLIP_PADDING_FRAMES, report, report_path))
        return report

    def _finalize(self, clip: _PendingClip):
        clip.writer.release()
        with open(clip.report_path, "w", encoding="utf-8") as fh:
            json.dump(clip.report, fh, indent=2, ensure_ascii=False)

    def close(self):
        """Finalise any clips still open when the stream ends."""
        for clip in self._pending:
            self._finalize(clip)
        self._pending = []
