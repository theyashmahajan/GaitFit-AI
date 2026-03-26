from __future__ import annotations

from statistics import median
from typing import Any

from utils.angle_utils import clamp


DEFAULT_SHANK_CM = 42.0


def estimate_shoe_size(
    poses: list[dict[str, Any]],
    input_type: str = "video",
) -> dict[str, Any]:
    ratios: list[float] = []
    side_used = "right"
    for p in poses:
        lm = p.get("landmarks", {})
        right = _ratio_for_side(lm, "right")
        left = _ratio_for_side(lm, "left")
        if right is None and left is None:
            continue
        if left is None or (right is not None and _side_vis(lm, "right") >= _side_vis(lm, "left")):
            ratios.append(right)  # type: ignore[arg-type]
            side_used = "right"
        else:
            ratios.append(left)  # type: ignore[arg-type]
            side_used = "left"

    if not ratios:
        return {
            "estimated": False,
            "message": "Could not estimate shoe size from the uploaded media.",
            "disclaimer": _disclaimer(),
        }

    base_ratio = float(median(ratios))
    foot_len_cm = clamp(base_ratio * DEFAULT_SHANK_CM, 21.0, 32.0)
    uk = _cm_to_uk(foot_len_cm)
    spread = _spread(ratios)
    uncertainty = _size_uncertainty(spread, len(ratios), input_type)

    return {
        "estimated": True,
        "side": side_used,
        "foot_length_cm": round(foot_len_cm, 1),
        "uk_size": _size_range_str(uk, uncertainty),
        "us_men_size": _size_range_str(uk + 1, uncertainty),
        "us_women_size": _size_range_str(uk + 2, uncertainty),
        "eu_size": _size_range_str(uk + 33, uncertainty),
        "confidence": _confidence_label(uncertainty),
        "method": "Pose proportion estimate (heel-to-toe vs lower-leg length proxy).",
        "disclaimer": _disclaimer(),
    }


def _ratio_for_side(lm: dict[str, list[float]], side: str) -> float | None:
    req = [f"{side}_heel", f"{side}_foot_index", f"{side}_knee", f"{side}_ankle"]
    if any(k not in lm for k in req):
        return None
    heel = lm[f"{side}_heel"]
    toe = lm[f"{side}_foot_index"]
    knee = lm[f"{side}_knee"]
    ankle = lm[f"{side}_ankle"]
    foot = _dist2d(heel, toe)
    shank = _dist2d(knee, ankle)
    if shank <= 1e-4:
        return None
    ratio = foot / shank
    if ratio < 0.35 or ratio > 0.9:
        return None
    return float(ratio)


def _dist2d(a: list[float], b: list[float]) -> float:
    dx = float(a[0]) - float(b[0])
    dy = float(a[1]) - float(b[1])
    return (dx * dx + dy * dy) ** 0.5


def _side_vis(lm: dict[str, list[float]], side: str) -> float:
    keys = [f"{side}_knee", f"{side}_ankle", f"{side}_heel", f"{side}_foot_index"]
    vals = [float(lm[k][3]) for k in keys if k in lm and len(lm[k]) > 3]
    return sum(vals)


def _cm_to_uk(cm: float) -> int:
    # Approx conversion suitable for rough product estimate in V1.
    return int(round((cm - 22.8) / 0.85 + 4))


def _size_uncertainty(spread: float, frames: int, input_type: str) -> int:
    points = 1
    if spread > 0.06:
        points += 1
    if frames < 8:
        points += 1
    if input_type == "image":
        points += 1
    return max(1, min(2, points))


def _confidence_label(uncertainty: int) -> str:
    return "low" if uncertainty >= 2 else "medium"


def _size_range_str(center: int, uncertainty: int) -> str:
    lo = max(1, center - uncertainty)
    hi = center + uncertainty
    return f"{lo}-{hi}" if lo != hi else str(center)


def _spread(values: list[float]) -> float:
    if len(values) < 3:
        return 0.08
    v = sorted(values)
    return float(v[-1] - v[0])


def _disclaimer() -> str:
    return (
        "Estimated size only. Camera angle, distance, pose visibility, and perspective can affect accuracy."
    )
