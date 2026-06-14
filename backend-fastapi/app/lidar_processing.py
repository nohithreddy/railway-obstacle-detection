import math
from dataclasses import dataclass
from typing import Iterable


@dataclass
class LidarPoint:
    x: float
    y: float
    z: float
    intensity: float = 1.0


def nearest_track_cluster(points: Iterable[LidarPoint], track_half_width_m: float = 0.85) -> dict | None:
    candidates = [p for p in points if abs(p.x) <= track_half_width_m and p.y > 0]
    if not candidates:
        return None

    nearest = min(candidates, key=lambda p: math.sqrt(p.x * p.x + p.y * p.y + p.z * p.z))
    distance = math.sqrt(nearest.x * nearest.x + nearest.y * nearest.y + nearest.z * nearest.z)
    return {
        "distance_m": round(distance, 2),
        "track_position": "center" if abs(nearest.x) < 0.35 else "rail_edge",
        "height_m": round(max(p.z for p in candidates) - min(p.z for p in candidates), 2),
        "width_m": round(max(p.x for p in candidates) - min(p.x for p in candidates), 2),
    }
