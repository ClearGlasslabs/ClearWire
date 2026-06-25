"""Tests for the traffic enforcement core (no YOLO/EasyOCR weights required).

Covers BEV speed estimation accuracy, the IoU tracker association and speed
smoothing, the speed-to-colour legend mapping, OCR-tolerant owner lookup, and a
synthetic end-to-end run through the pipeline with a stubbed detector and plate
reader.
"""

from __future__ import annotations

import json
import os
import tempfile

import cv2
import numpy as np

import config
from detector import Detection
from enforcement import EnforcementSystem
from owner_lookup import OwnerRegistry
from plate_reader import PlateReader
from speed_estimator import SpeedEstimator, speed_color
from tracker import VehicleTracker


def test_speed_color_bands():
    assert speed_color(40) == config.COLOR_SLOW
    assert speed_color(59.9) == config.COLOR_SLOW
    assert speed_color(60) == config.COLOR_MID
    assert speed_color(100) == config.COLOR_MID
    assert speed_color(100.1) == config.COLOR_FAST
    assert speed_color(130) == config.COLOR_FAST


def test_bev_known_speed_within_tolerance():
    # A vehicle moving along the left carriageway centre line at a known speed
    # should be recovered to within a few km/h by the BEV estimator.
    fps = 30.0
    est = SpeedEstimator(fps)
    cw = est.left

    # Pick two BEV ground points 1 metre apart along the road, project them back
    # into camera space, then run them through the estimator.
    inv = np.linalg.inv(cw.H)

    def bev_m_to_camera(mx, my):
        bx, by = mx * config.BEV_SCALE, my * config.BEV_SCALE
        pt = np.array([[[bx, by]]], dtype=np.float32)
        return cv2.perspectiveTransform(pt, inv)[0][0]

    road_w = config.ROAD_WIDTH_L_M
    p0_cam = bev_m_to_camera(road_w / 2, 30.0)
    p1_cam = bev_m_to_camera(road_w / 2, 30.0 + 1.0)  # 1 m further along

    m0 = est.ground_point_metres((p0_cam[0] - 5, p0_cam[1] - 10, p0_cam[0] + 5, p0_cam[1]))
    m1 = est.ground_point_metres((p1_cam[0] - 5, p1_cam[1] - 10, p1_cam[0] + 5, p1_cam[1]))
    assert m0 is not None and m1 is not None

    # 1 m in 1 frame at 30 fps == 30 m/s == 108 km/h.
    speed = est.speed_kmh(m0, m1, 1)
    assert abs(speed - 108.0) < 3.0


def test_off_road_point_returns_none():
    est = SpeedEstimator(30.0)
    assert est.ground_point_metres((-500, -500, -480, -490)) is None


def test_owner_lookup_exact_and_ocr_confusion():
    reg = OwnerRegistry(os.path.join(os.path.dirname(__file__), "owners.json"))
    assert reg.lookup("HK1234")["name"] == "Chan Tai Man"
    # OCR misreads 0 as O, 1 as I, 8 as B -> still resolves.
    assert reg.lookup("HKI234")["name"] == "Chan Tai Man"
    assert reg.lookup("LMB0B0")["name"] == "Wong Siu Ling"
    assert reg.lookup("UNKNOWN") is None
    assert reg.lookup("") is None


def test_plate_reader_degrades_without_ocr():
    reader = PlateReader()
    reader._unavailable = True  # simulate easyocr not installed
    assert reader.read_plate(np.zeros((10, 10, 3), dtype=np.uint8)) is None


def test_tracker_associates_and_smooths_speed():
    est = SpeedEstimator(30.0)
    tracker = VehicleTracker(est)
    # A box moving downward (towards the camera) inside the left carriageway.
    x = 300
    for i in range(6):
        det = Detection((x, 600 + i * 15, x + 80, 700 + i * 15), 0.9, 2)
        active = tracker.update([det], i)
    assert len(tracker.tracks) == 1
    track = active[0]
    assert track.speed_kmh > 0
    assert track.max_speed_kmh >= track.speed_kmh


def _synthetic_video(path, frames=40, w=1280, h=720, fps=30):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, fps, (w, h))
    for _ in range(frames):
        writer.write(np.full((h, w, 3), 30, dtype=np.uint8))
    writer.release()


class _StubDetector:
    """Emits one fast vehicle accelerating down the left carriageway."""

    def detect(self, frame):
        self.t = getattr(self, "t", -1) + 1
        y = 500 + self.t * 22
        return [Detection((300.0, float(y), 380.0, float(y + 90)), 0.95, 2)]


class _StubPlateReader:
    def read_plate(self, crop):
        return ("HK1234", 0.97)


def test_end_to_end_records_violation():
    with tempfile.TemporaryDirectory() as tmp:
        video = os.path.join(tmp, "in.mp4")
        out = os.path.join(tmp, "out.mp4")
        _synthetic_video(video)

        old_dir = config.VIOLATION_DIR
        config.VIOLATION_DIR = os.path.join(tmp, "violations")
        try:
            system = EnforcementSystem(
                detector=_StubDetector(),
                plate_reader=_StubPlateReader(),
                owner_registry=OwnerRegistry(
                    os.path.join(os.path.dirname(__file__), "owners.json")),
            )
            violations = system.process_video(video, output_path=out)
        finally:
            config.VIOLATION_DIR = old_dir

        assert os.path.exists(out)
        assert len(violations) >= 1
        v = violations[0]
        assert v["speed_kmh"] > config.SPEED_LIMIT_KMH
        assert v["license_plate"] == "HK1234"
        assert v["owner"]["name"] == "Chan Tai Man"
        clip = os.path.join(config.VIOLATION_DIR if os.path.isdir(config.VIOLATION_DIR)
                            else os.path.join(tmp, "violations"), v["clip"])
        # the recorded report references a clip file that was written
        report_dir = os.path.join(tmp, "violations")
        assert os.path.exists(os.path.join(report_dir, v["clip"]))


if __name__ == "__main__":
    import sys
    funcs = [g for n, g in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for fn in funcs:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
    print(f"\n{len(funcs) - failed}/{len(funcs)} passed")
    sys.exit(1 if failed else 0)
