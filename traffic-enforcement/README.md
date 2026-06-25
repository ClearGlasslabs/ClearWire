# AI traffic speed enforcement

Real-time camera-based speed enforcement, built from the reference design: detect
vehicles, estimate each one's speed from a bird's-eye-view projection, colour-code
by speed band, and — when a vehicle exceeds the limit — record a video clip, read
the license plate, and identify the registered owner.

![legend](https://img.shields.io/badge/%3C60-green)
![legend](https://img.shields.io/badge/60--100-yellow)
![legend](https://img.shields.io/badge/%3E100-red)

## How it works

```
frame ─▶ detector ─▶ tracker ─▶ speed estimator ─▶ annotate ─▶ output
                          │                              │
                          └─ over limit? ─▶ plate OCR ─▶ owner lookup ─▶ record clip + report
```

1. **Detection** (`detector.py`) — Ultralytics YOLO finds vehicles (car, bus,
   truck, motorcycle, bicycle) each frame.
2. **Speed estimation** (`speed_estimator.py`) — each carriageway has its own
   homography mapping camera pixels to a rectified top-down view where
   `1 m == BEV_SCALE px`. A vehicle's ground-contact point is projected into this
   bird's-eye view, and distance over time gives speed. Calibration points
   (`SRC_ROAD_L`, `SRC_ROAD_R`, `BEV_SCALE`, `VISIBLE_LENGTH_M`, lane widths) live
   in `config.py`.
3. **Tracking** (`tracker.py`) — a lightweight IoU tracker associates detections
   across frames and smooths speed over several samples to kill jitter.
4. **Classification** (`config.py` / `enforcement.py`) — speed bands match the
   legend: green `< 60`, yellow `60–100`, red `> 100 km/h`.
5. **Enforcement** (`enforcement.py` + `recorder.py`) — vehicles over
   `SPEED_LIMIT_KMH` trigger a clip (with pre-event padding), a plate crop, a
   plate read (`plate_reader.py`, EasyOCR), an owner lookup (`owner_lookup.py`),
   and a JSON violation report under `violations/`.

## Install

```bash
pip install -r requirements.txt
```

YOLO weights download automatically on first run. EasyOCR models download on
first plate read. The package imports and the core test suite run without either
(plate reading degrades gracefully to `None`).

## Run

```bash
# annotate a video file
python main.py --source traffic.mp4 --output annotated.mp4

# live camera, on-screen
python main.py --source 0 --show

# override the speed limit (km/h)
python main.py --source traffic.mp4 --limit 80
```

Each violation writes three files to `violations/`:

- `violation_<ts>_track<id>.mp4` — the clip
- `violation_<ts>_track<id>_vehicle.jpg` — the vehicle/plate crop
- `violation_<ts>_track<id>.json` — speed, plate, owner, over-limit amount

## Calibration

The default `SRC_ROAD_L` / `SRC_ROAD_R` quads are the reference camera's. For a new
camera, set the four points (far-left, far-right, near-right, near-left) along each
carriageway's kerb/divider in pixel coordinates, set `LANE_WIDTH_M` and the lane
counts, and the homography follows. Accuracy depends almost entirely on this.

## Tests

```bash
python test_system.py     # or: pytest test_system.py
```

Covers BEV speed accuracy, tracking + smoothing, the colour bands, OCR-tolerant
owner lookup, and a synthetic end-to-end run that records a violation.

## Notes

This is enforcement infrastructure: deploy it only where you are authorised to,
and handle plate/owner data under the applicable privacy law. The bundled
`owners.json` is sample data standing in for a registration authority lookup.
