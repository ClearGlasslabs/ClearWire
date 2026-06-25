"""Calibration and runtime configuration for the traffic speed enforcement system.

The geometry below mirrors the on-screen source code from the reference build: a
bird's-eye-view (BEV) homography is calibrated separately for the left and right
carriageways so that pixel motion in the camera frame can be converted into real
distances in metres, and from there into speed.

All four source points per carriageway are given in *camera pixel* coordinates and
map onto a rectified top-down rectangle whose width is the carriageway width in
metres and whose height is the visible road length in metres, both scaled by
``BEV_SCALE`` pixels per metre.
"""

from __future__ import annotations

import numpy as np

# --- Road geometry ----------------------------------------------------------
LANE_WIDTH_M = 3.75               # standard motorway lane width (m)
NUM_LANES_LEFT = 3                # lanes on the left carriageway
NUM_LANES_RIGHT = 3              # lanes on the right carriageway

ROAD_WIDTH_L_M = LANE_WIDTH_M * NUM_LANES_LEFT     # = 11.25 m
ROAD_WIDTH_R_M = LANE_WIDTH_M * NUM_LANES_RIGHT    # = 11.25 m

BEV_SCALE = 18                    # pixels per metre in the rectified BEV image
VISIBLE_LENGTH_M = 70             # length of road covered by the BEV (m)

# --- Source quadrilaterals (camera pixel coordinates) -----------------------
# Order: far-left, far-right, near-right, near-left.
SRC_ROAD_L = np.float32([
    [155, 415],     # far-left   (distant, left kerb)
    [600, 395],     # far-right  (distant, centre divider)
    [845, 1079],    # near-right (close, centre divider)
    [0, 1079],      # near-left  (close, left kerb)
])

SRC_ROAD_R = np.float32([
    [845, 395],     # far-left   (distant, centre divider)
    [1140, 395],    # far-right  (distant, right kerb)
    [2230, 1079],   # near-right (close, right kerb)
    [900, 1079],    # near-left  (close, centre divider)
])

# --- Speed classification ---------------------------------------------------
# Thresholds match the on-screen legend: green < 60, yellow 60-100, red > 100.
SPEED_LIMIT_KMH = 100             # enforcement threshold; over this is a violation
SLOW_KMH = 60
FAST_KMH = 100

# BGR colours (OpenCV) for each band.
COLOR_SLOW = (0, 200, 0)          # green  (< 60 km/h)
COLOR_MID = (0, 200, 255)         # yellow (60-100 km/h)
COLOR_FAST = (0, 0, 255)          # red    (> 100 km/h)

# --- Detection / tracking ---------------------------------------------------
MODEL_WEIGHTS = "yolov8n.pt"      # ultralytics weights (auto-downloaded on first run)
CONF_THRESHOLD = 0.35             # minimum detection confidence
VEHICLE_CLASSES = {1, 2, 3, 5, 7} # COCO: bicycle, car, motorcycle, bus, truck

MAX_TRACK_AGE = 15                # frames a track survives without a match
IOU_MATCH_THRESHOLD = 0.3         # IoU needed to associate a detection to a track
SPEED_SMOOTHING = 5               # number of recent samples averaged for speed

# --- Enforcement ------------------------------------------------------------
VIOLATION_DIR = "violations"      # where clips, plate crops and reports are written
CLIP_PADDING_FRAMES = 30          # frames recorded before/after a violation
OWNER_REGISTRY = "owners.json"    # plate -> owner lookup table


def bev_size(road_width_m: float) -> tuple[int, int]:
    """Return the (width, height) in pixels of the rectified BEV image."""
    return (
        int(round(road_width_m * BEV_SCALE)),
        int(round(VISIBLE_LENGTH_M * BEV_SCALE)),
    )


def dst_quad(road_width_m: float) -> np.ndarray:
    """Destination rectangle for the BEV homography, in BEV pixel coordinates."""
    w, h = bev_size(road_width_m)
    return np.float32([
        [0, 0],         # far-left
        [w, 0],         # far-right
        [w, h],         # near-right
        [0, h],         # near-left
    ])
