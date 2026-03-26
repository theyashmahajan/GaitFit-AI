from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

from utils.angle_utils import safe_angle

SKELETON_EDGES = [
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),
    ("left_ankle", "left_heel"),
    ("left_ankle", "left_foot_index"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
    ("right_ankle", "right_heel"),
    ("right_ankle", "right_foot_index"),
    ("left_hip", "right_hip"),
]

KEY_LABELS = [
    ("initial_contact", "Initial Contact"),
    ("mid_stance", "Mid Stance"),
    ("toe_off", "Toe Off"),
]


def render_evidence_frame(
    job_id: str,
    frames: list[np.ndarray],
    poses: list[dict[str, Any]],
    out_dir: Path,
    gait_events: dict[str, list[int]] | None = None,
) -> dict[str, Any]:
    if not frames or not poses:
        return {}
    side = _dominant_side(poses)
    key_indices = _pick_key_frames(poses, side, gait_events=gait_events)
    hero_idx = key_indices.get("mid_stance", _pick_best_frame(poses))

    hero = _render_single(job_id, "evidence", hero_idx, side, frames, poses, out_dir, "Visual Evidence")
    if not hero:
        return {}

    key_frames: list[dict[str, Any]] = []
    used = set()
    for key, label in KEY_LABELS:
        idx = key_indices.get(key, hero_idx)
        if idx in used:
            idx = _nearest_unused(idx, used, len(poses))
        used.add(idx)
        rendered = _render_single(job_id, key, idx, side, frames, poses, out_dir, label, event_key=key)
        if rendered:
            key_frames.append(rendered)

    hero["key_frames"] = key_frames
    hero["aspect_ratio"] = round(hero["width"] / hero["height"], 4) if hero["height"] else 1.0
    hero["quality_trend"] = _quality_trend(poses, side)
    hero["timeline_frames"] = _build_timeline_frames(job_id, frames, poses, out_dir, side)
    hero["event_markers"] = key_indices
    return hero


def _render_single(
    job_id: str,
    suffix: str,
    idx: int,
    side: str,
    frames: list[np.ndarray],
    poses: list[dict[str, Any]],
    out_dir: Path,
    title: str,
    event_key: str | None = None,
) -> dict[str, Any] | None:
    if idx < 0 or idx >= len(poses) or idx >= len(frames):
        return None
    lm = poses[idx].get("landmarks", {})
    if not lm:
        return None
    canvas = frames[idx].copy()
    h, w = canvas.shape[:2]

    for a, b in SKELETON_EDGES:
        if a in lm and b in lm:
            cv2.line(canvas, _to_px(lm[a], w, h), _to_px(lm[b], w, h), (232, 128, 40), 3, cv2.LINE_AA)
    for name, point in lm.items():
        color = (30, 220, 120) if "left_" in name else (80, 140, 255)
        cv2.circle(canvas, _to_px(point, w, h), 6, color, -1, cv2.LINE_AA)

    metrics = _angles_for_side(lm, side)
    if not metrics:
        return None
    quality_score = _quality_score(lm, side)
    caption = _event_caption(event_key, metrics, quality_score)
    _draw_label(canvas, _to_px(lm[f"{side}_knee"], w, h), f"knee {metrics['knee_deg']:.0f} deg")
    _draw_label(canvas, _to_px(lm[f"{side}_ankle"], w, h), f"ankle {metrics['ankle_deg']:.0f} deg")
    _draw_top_banner(canvas, title)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{job_id}_{suffix}.jpg"
    cv2.imwrite(str(out_path), canvas)

    return {
        "id": suffix,
        "label": title,
        "image_url": f"/assets/{out_path.name}",
        "frame_index": int(idx),
        "angles": {"knee_deg": round(metrics["knee_deg"], 1), "ankle_deg": round(metrics["ankle_deg"], 1)},
        "side": side,
        "width": w,
        "height": h,
        "quality_score": round(quality_score, 2),
        "caption": caption,
    }


def _pick_key_frames(
    poses: list[dict[str, Any]],
    side: str,
    gait_events: dict[str, list[int]] | None = None,
) -> dict[str, int]:
    if gait_events:
        hs = gait_events.get("heel_strike") or []
        ms = gait_events.get("mid_stance") or []
        to = gait_events.get("toe_off") or []
        if hs and ms and to:
            return {"initial_contact": int(hs[0]), "mid_stance": int(ms[0]), "toe_off": int(to[0])}

    candidates = []
    for i, p in enumerate(poses):
        lm = p.get("landmarks", {})
        m = _angles_for_side(lm, side)
        if not m:
            continue
        heel_y = lm[f"{side}_heel"][1]
        toe_y = lm[f"{side}_foot_index"][1]
        hip_x = lm[f"{side}_hip"][0]
        ankle_x = lm[f"{side}_ankle"][0]
        vis = _visibility_score(lm, side)
        candidates.append(
            {
                "idx": i,
                "heel_y": heel_y,
                "toe_y": toe_y,
                "align": abs(hip_x - ankle_x),
                "vis": vis,
            }
        )

    if not candidates:
        base = _pick_best_frame(poses)
        return {"initial_contact": base, "mid_stance": min(base + 1, len(poses) - 1), "toe_off": min(base + 2, len(poses) - 1)}

    initial = max(candidates, key=lambda c: (c["heel_y"] - c["toe_y"], c["vis"]))["idx"]
    mid = min(candidates, key=lambda c: (c["align"], -c["vis"]))["idx"]
    toe = max(candidates, key=lambda c: (c["toe_y"] - c["heel_y"], c["vis"]))["idx"]
    return {"initial_contact": initial, "mid_stance": mid, "toe_off": toe}


def _build_timeline_frames(
    job_id: str,
    frames: list[np.ndarray],
    poses: list[dict[str, Any]],
    out_dir: Path,
    side: str,
) -> list[dict[str, Any]]:
    if len(frames) <= 3:
        return []
    slots = min(12, len(frames))
    picks = sorted(set(np.linspace(0, len(frames) - 1, num=slots, dtype=int).tolist()))
    items: list[dict[str, Any]] = []
    for idx in picks:
        rendered = _render_single(job_id, f"timeline_{idx}", idx, side, frames, poses, out_dir, f"Frame {idx}")
        if not rendered:
            continue
        items.append(rendered)
    return items


def _nearest_unused(seed: int, used: set[int], total: int) -> int:
    if seed not in used:
        return seed
    for offset in range(1, total):
        right = seed + offset
        left = seed - offset
        if right < total and right not in used:
            return right
        if left >= 0 and left not in used:
            return left
    return seed


def _dominant_side(poses: list[dict[str, Any]]) -> str:
    left_sum = 0.0
    right_sum = 0.0
    for p in poses:
        lm = p.get("landmarks", {})
        left_sum += _visibility_score(lm, "left")
        right_sum += _visibility_score(lm, "right")
    return "left" if left_sum >= right_sum else "right"


def _visibility_score(lm: dict[str, list[float]], side: str) -> float:
    keys = [f"{side}_hip", f"{side}_knee", f"{side}_ankle", f"{side}_heel", f"{side}_foot_index"]
    return float(sum(lm[k][3] for k in keys if k in lm and len(lm[k]) > 3))


def _quality_score(lm: dict[str, list[float]], side: str) -> float:
    vis = _visibility_score(lm, side) / 5.0
    jitter = 0.0
    keys = [f"{side}_hip", f"{side}_knee", f"{side}_ankle", f"{side}_heel", f"{side}_foot_index"]
    points = [lm[k] for k in keys if k in lm]
    if len(points) >= 3:
        xs = np.array([p[0] for p in points])
        ys = np.array([p[1] for p in points])
        spread = float(np.std(xs) + np.std(ys))
        jitter = min(0.25, spread)
    return float(max(0.0, min(1.0, 0.78 * vis + 0.22 * (1 - jitter))))


def _event_caption(event_key: str | None, metrics: dict[str, float], quality: float) -> str:
    knee = round(metrics["knee_deg"])
    ankle = round(metrics["ankle_deg"])
    quality_text = "high" if quality >= 0.8 else "medium" if quality >= 0.6 else "low"
    if event_key == "initial_contact":
        return f"Heel contact phase captured with ankle at {ankle} deg. Detection confidence is {quality_text}."
    if event_key == "mid_stance":
        return f"Mid stance frame with knee around {knee} deg, useful for stability assessment ({quality_text} confidence)."
    if event_key == "toe_off":
        return f"Toe-off phase shows propulsion angle near {ankle} deg with {quality_text} confidence."
    return f"Representative gait frame with knee {knee} deg and ankle {ankle} deg ({quality_text} confidence)."


def _quality_trend(poses: list[dict[str, Any]], side: str) -> list[dict[str, float]]:
    trend: list[dict[str, float]] = []
    for idx, p in enumerate(poses):
        lm = p.get("landmarks", {})
        if not lm:
            continue
        score = _quality_score(lm, side)
        trend.append({"frame": float(idx), "score": round(score, 3)})
    return trend


def _angles_for_side(lm: dict[str, list[float]], side: str) -> dict[str, float] | None:
    required = [f"{side}_hip", f"{side}_knee", f"{side}_ankle", f"{side}_heel", f"{side}_foot_index"]
    if any(k not in lm for k in required):
        return None
    hip, knee, ankle = lm[f"{side}_hip"][:3], lm[f"{side}_knee"][:3], lm[f"{side}_ankle"][:3]
    heel, toe = lm[f"{side}_heel"][:3], lm[f"{side}_foot_index"][:3]
    return {"knee_deg": float(safe_angle(hip, knee, ankle)), "ankle_deg": float(safe_angle(heel, ankle, toe))}


def _pick_best_frame(poses: list[dict[str, Any]]) -> int:
    best_idx = 0
    best_score = -1.0
    for i, p in enumerate(poses):
        lm = p.get("landmarks", {})
        if not lm:
            continue
        score = float(sum(v[3] for v in lm.values() if len(v) > 3))
        if score > best_score:
            best_score = score
            best_idx = i
    return best_idx


def _to_px(point: list[float], width: int, height: int) -> tuple[int, int]:
    return int(point[0] * width), int(point[1] * height)


def _draw_label(img: np.ndarray, anchor: tuple[int, int], text: str) -> None:
    x, y = anchor
    tx, ty = x + 12, y - 12
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.62, 2)
    cv2.rectangle(img, (tx - 6, ty - th - 8), (tx + tw + 6, ty + 6), (30, 30, 30), -1)
    cv2.rectangle(img, (tx - 6, ty - th - 8), (tx + tw + 6, ty + 6), (70, 70, 70), 1)
    cv2.putText(img, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)


def _draw_top_banner(img: np.ndarray, title: str) -> None:
    h, w = img.shape[:2]
    cv2.rectangle(img, (0, 0), (w, 58), (10, 10, 10), -1)
    cv2.putText(img, f"GaitFit AI {title}", (16, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.82, (255, 255, 255), 2)
