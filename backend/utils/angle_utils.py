from __future__ import annotations

import math
from typing import Iterable

import numpy as np


def safe_angle(a: Iterable[float], b: Iterable[float], c: Iterable[float]) -> float:
    a_np = np.array(list(a), dtype=float)
    b_np = np.array(list(b), dtype=float)
    c_np = np.array(list(c), dtype=float)
    ba = a_np - b_np
    bc = c_np - b_np
    denom = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denom == 0:
        return 0.0
    cos_theta = np.clip(np.dot(ba, bc) / denom, -1.0, 1.0)
    return float(math.degrees(math.acos(cos_theta)))


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))

