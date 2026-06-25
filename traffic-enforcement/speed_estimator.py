"""Bird's-eye-view speed estimation.

Each carriageway has its own homography mapping camera pixels to a rectified
top-down view where 1 metre == ``BEV_SCALE`` pixels. A vehicle's ground-contact
point (bottom-centre of its bounding box) is projected into the BEV, and the
distance travelled between frames is divided by the elapsed time to give speed.
"""

from __future__ import annotations

import cv2
import numpy as np

import config


class CarriagewayBEV:
    """Homography for a single carriageway between camera and BEV space."""

    def __init__(self, src_quad: np.ndarray, road_width_m: float):
        self.road_width_m = road_width_m
        self.src_quad = src_quad
        self.dst_quad = config.dst_quad(road_width_m)
        self.H = cv2.getPerspectiveTransform(self.src_quad, self.dst_quad)
        self._poly = src_quad.astype(np.int32)

    def contains(self, x: float, y: float) -> bool:
        """True if a camera-space point lies inside this carriageway region."""
        return cv2.pointPolygonTest(self._poly, (float(x), float(y)), False) >= 0

    def to_bev_metres(self, x: float, y: float) -> tuple[float, float]:
        """Project a camera point to BEV coordinates expressed in metres."""
        pt = np.array([[[x, y]]], dtype=np.float32)
        bx, by = cv2.perspectiveTransform(pt, self.H)[0][0]
        return bx / config.BEV_SCALE, by / config.BEV_SCALE


class SpeedEstimator:
    """Routes vehicle ground points to the correct carriageway and measures speed."""

    def __init__(self, fps: float):
        self.fps = max(fps, 1e-6)
        self.left = CarriagewayBEV(config.SRC_ROAD_L, config.ROAD_WIDTH_L_M)
        self.right = CarriagewayBEV(config.SRC_ROAD_R, config.ROAD_WIDTH_R_M)

    def _carriageway(self, x: float, y: float) -> CarriagewayBEV | None:
        if self.left.contains(x, y):
            return self.left
        if self.right.contains(x, y):
            return self.right
        return None

    def ground_point_metres(self, bbox: tuple[float, float, float, float]):
        """Map a bbox (x1,y1,x2,y2) bottom-centre to BEV metres, or None if off-road."""
        x1, y1, x2, y2 = bbox
        gx, gy = (x1 + x2) / 2.0, y2
        cw = self._carriageway(gx, gy)
        if cw is None:
            return None
        return cw.to_bev_metres(gx, gy)

    def speed_kmh(self, p_prev, p_curr, frames_elapsed: int) -> float:
        """Speed in km/h between two BEV points (metres) separated by N frames."""
        if frames_elapsed <= 0:
            return 0.0
        dist_m = float(np.hypot(p_curr[0] - p_prev[0], p_curr[1] - p_prev[1]))
        dt_s = frames_elapsed / self.fps
        return (dist_m / dt_s) * 3.6


def speed_color(speed_kmh: float):
    """Return the BGR colour for a speed according to the legend."""
    if speed_kmh < config.SLOW_KMH:
        return config.COLOR_SLOW
    if speed_kmh <= config.FAST_KMH:
        return config.COLOR_MID
    return config.COLOR_FAST
