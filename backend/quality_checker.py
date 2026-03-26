from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import cv2
import numpy as np

try:
    import mediapipe as mp
except Exception:  # pragma: no cover
    mp = None


@dataclass
class QualityReport:
    passed: bool
    score: int
    issues: list[str] = field(default_factory=list)


def check(video_path: str) -> dict[str, Any]:
    cap = cv2.VideoCapture(video_path)
    frames: list[np.ndarray] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    cap.release()
    if not frames:
        return asdict(QualityReport(passed=False, score=10, issues=["Could not decode video frames."]))

    issues: list[str] = []
    score = 100
    brightness = _avg_brightness(frames)
    if brightness < 80:
        issues.append("Lighting is too dark. Record in brighter light.")
        score -= 22
    elif brightness > 220:
        issues.append("Video is overexposed. Reduce strong backlight or glare.")
        score -= 18

    stability = _camera_stability(frames)
    if stability < 0.35:
        issues.append("Camera appears shaky. Keep phone steady at knee height.")
        score -= 20

    if mp is None:
        issues.append("Pose pre-check unavailable because MediaPipe is not installed.")
        score -= 5
    else:
        body_ok, body_conf, side_conf = _pose_visibility_and_side_confidence(frames)
        if not body_ok:
            issues.append("Body not fully visible. Keep full lower body and feet in frame.")
            score -= 28
        if side_conf < 0.5:
            issues.append("Side-view confidence is low. Record from true side profile.")
            score -= 22
        if body_conf < 0.6:
            score -= 8

    score = int(max(0, min(100, score)))
    passed = score >= 55 and len(issues) <= 2
    return asdict(QualityReport(passed=passed, score=score, issues=issues))


def _avg_brightness(frames: list[np.ndarray]) -> float:
    sampled = frames[:: max(1, len(frames) // 12)]
    vals = [float(np.mean(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))) for f in sampled]
    return float(np.mean(vals)) if vals else 0.0


def _camera_stability(frames: list[np.ndarray]) -> float:
    if len(frames) < 2:
        return 0.3
    diffs = []
    step = max(1, len(frames) // 25)
    prev = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
    for i in range(step, len(frames), step):
        cur = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev, cur)
        diffs.append(float(np.mean(diff)))
        prev = cur
    if not diffs:
        return 0.3
    mean_diff = float(np.mean(diffs))
    var_diff = float(np.var(diffs))
    # Lower motion variance and moderate mean frame difference indicate steadier capture.
    stability = 1.0 - min(1.0, (mean_diff / 42.0) * 0.5 + (var_diff / 120.0) * 0.5)
    return float(max(0.0, min(1.0, stability)))


def _pose_visibility_and_side_confidence(frames: list[np.ndarray]) -> tuple[bool, float, float]:
    idxs = [0, min(4, len(frames) - 1), min(9, len(frames) - 1)]
    pose = mp.solutions.pose.Pose(
        static_image_mode=True,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    vis_scores: list[float] = []
    side_scores: list[float] = []
    success = 0
    try:
        for idx in idxs:
            rgb = cv2.cvtColor(frames[idx], cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)
            if not result.pose_landmarks:
                continue
            lm = result.pose_landmarks.landmark
            points = [11, 12, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
            vis = float(np.mean([lm[p].visibility for p in points]))
            vis_scores.append(vis)
            side_scores.append(_side_view_confidence(lm))
            if vis >= 0.6:
                success += 1
    finally:
        pose.close()
    body_ok = success >= 2
    body_conf = float(np.mean(vis_scores)) if vis_scores else 0.0
    side_conf = float(np.mean(side_scores)) if side_scores else 0.0
    return body_ok, body_conf, side_conf


def _side_view_confidence(lm) -> float:
    l_sh, r_sh = lm[11], lm[12]
    l_hip, r_hip = lm[23], lm[24]
    shoulder_w = abs(float(l_sh.x) - float(r_sh.x))
    hip_w = abs(float(l_hip.x) - float(r_hip.x))
    depth_gap = (abs(float(l_sh.z) - float(r_sh.z)) + abs(float(l_hip.z) - float(r_hip.z))) / 2.0
    width_ratio = shoulder_w / max(hip_w, 1e-4)
    score = 0.5
    if depth_gap > 0.08:
        score += 0.25
    if 0.35 <= width_ratio <= 1.4:
        score += 0.2
    if width_ratio < 0.25:
        score -= 0.2
    return float(max(0.0, min(1.0, score)))
