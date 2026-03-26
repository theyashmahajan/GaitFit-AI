from __future__ import annotations

from typing import Any

import numpy as np
from scipy.signal import savgol_filter

from models import GaitFeatures, GaitProfile
from utils.angle_utils import clamp, safe_angle

try:
    from sklearn.linear_model import LogisticRegression
except Exception:  # pragma: no cover
    LogisticRegression = None


class HybridGaitClassifier:
    def __init__(self) -> None:
        self.model = None
        if LogisticRegression is not None:
            self.model = self._train_bootstrap_model()

    def _train_bootstrap_model(self):
        rng = np.random.default_rng(7)
        # [ankle_tilt, knee_angle, hip_drop, symmetry, cadence, strike_bias]
        neutral = rng.normal([0, 175, 0.05, 0.92, 160, 0.0], [3, 3, 0.02, 0.03, 8, 0.3], (80, 6))
        overpronation = rng.normal([13, 167, 0.09, 0.84, 150, -0.2], [4, 4, 0.03, 0.05, 8, 0.4], (80, 6))
        supination = rng.normal([-11, 176, 0.04, 0.9, 158, 0.2], [4, 3, 0.02, 0.04, 8, 0.3], (80, 6))
        x = np.vstack([neutral, overpronation, supination])
        y = np.array(["neutral"] * 80 + ["overpronation"] * 80 + ["supination"] * 80)
        model = LogisticRegression(max_iter=1200, solver="liblinear")
        model.fit(x, y)
        return model

    def predict(self, f: GaitFeatures) -> tuple[str, float]:
        vector = np.array(
            [[f.ankle_tilt_deg, f.knee_angle_deg, f.hip_drop_ratio, f.stride_symmetry, f.cadence_spm, f.strike_bias]]
        )
        rule_scores = _rule_scores(f)
        if self.model is None:
            label = max(rule_scores, key=rule_scores.get)
            top2 = sorted(rule_scores.values(), reverse=True)[:2]
            confidence = clamp(0.42 + (top2[0] - top2[1]) * 0.5, 0.35, 0.88)
            return label, confidence

        probs = self.model.predict_proba(vector)[0]
        labels = [str(l) for l in self.model.classes_]
        ml_scores = {label: float(probs[idx]) for idx, label in enumerate(labels)}
        merged = {}
        for label in ("neutral", "overpronation", "supination"):
            merged[label] = 0.58 * ml_scores.get(label, 0.0) + 0.42 * rule_scores.get(label, 0.0)
        label = max(merged, key=merged.get)
        top2 = sorted(merged.values(), reverse=True)[:2]
        confidence = clamp(0.4 + (top2[0] - top2[1]) * 0.9, 0.32, 0.9)
        return label, confidence


def _pronation_from_rules(ankle_tilt_deg: float) -> str:
    if ankle_tilt_deg >= 8:
        return "overpronation"
    if ankle_tilt_deg <= -8:
        return "supination"
    return "neutral"


def _rule_confidence(ankle_tilt_deg: float) -> float:
    return clamp(abs(ankle_tilt_deg) / 18.0, 0.35, 0.95)


def _rule_scores(f: GaitFeatures) -> dict[str, float]:
    scores = {"neutral": 0.35, "overpronation": 0.35, "supination": 0.35}
    if f.ankle_tilt_deg >= 7:
        scores["overpronation"] += min(0.45, (f.ankle_tilt_deg - 7) / 14.0)
    elif f.ankle_tilt_deg <= -7:
        scores["supination"] += min(0.45, (abs(f.ankle_tilt_deg) - 7) / 14.0)
    else:
        scores["neutral"] += 0.25

    if f.knee_angle_deg < 169:
        scores["overpronation"] += 0.15
    if f.knee_angle_deg > 180:
        scores["supination"] += 0.12
    if f.stride_symmetry >= 0.88:
        scores["neutral"] += 0.08
    return scores


def analyze_gait(frame_poses: list[dict[str, Any]], sampled_fps: float = 10.0) -> tuple[GaitProfile, GaitFeatures]:
    if not frame_poses:
        raise ValueError("No pose data extracted from video.")
    cleaned = [p for p in frame_poses if p.get("landmarks")]
    if len(cleaned) < 1:
        raise ValueError("No detectable body frame. Please upload a clearer side-view image/video.")

    ankle_tilts: list[float] = []
    knee_angles: list[float] = []
    hip_drops: list[float] = []
    strikes: list[float] = []

    for frame in cleaned:
        lm = frame["landmarks"]
        l_hip = lm["left_hip"][:3]
        r_hip = lm["right_hip"][:3]
        l_knee = lm["left_knee"][:3]
        r_knee = lm["right_knee"][:3]
        l_ankle = lm["left_ankle"][:3]
        r_ankle = lm["right_ankle"][:3]
        l_heel = lm["left_heel"][:3]
        r_heel = lm["right_heel"][:3]
        l_toe = lm["left_foot_index"][:3]
        r_toe = lm["right_foot_index"][:3]

        left_ankle = safe_angle(l_heel, l_ankle, l_toe) - 170.0
        right_ankle = safe_angle(r_heel, r_ankle, r_toe) - 170.0
        ankle_tilts.append(float((left_ankle + right_ankle) / 2.0))

        left_knee = safe_angle(l_hip, l_knee, l_ankle)
        right_knee = safe_angle(r_hip, r_knee, r_ankle)
        knee_angles.append(float((left_knee + right_knee) / 2.0))

        hip_drops.append(abs(l_hip[1] - r_hip[1]))

        heel_toe_bias = ((l_toe[1] - l_heel[1]) + (r_toe[1] - r_heel[1])) / 2.0
        strikes.append(float(heel_toe_bias))

    ankle_sm = _smooth(ankle_tilts) if len(ankle_tilts) >= 7 else np.array(ankle_tilts, dtype=float)
    knee_sm = _smooth(knee_angles) if len(knee_angles) >= 7 else np.array(knee_angles, dtype=float)
    hip_sm = _smooth(hip_drops) if len(hip_drops) >= 7 else np.array(hip_drops, dtype=float)

    cadence = _estimate_cadence(ankle_sm, sampled_fps) if len(cleaned) >= 8 else 120
    symmetry = clamp(1.0 - float(np.std(hip_sm) * 4), 0.0, 1.0)
    strike_bias = float(np.mean(strikes)) if strikes else 0.0
    strike_pattern = "heel" if strike_bias > 0.005 else "forefoot" if strike_bias < -0.005 else "midfoot"

    avg_knee = float(np.mean(knee_sm))
    if avg_knee < 169:
        knee_alignment = "valgus"
    elif avg_knee > 181:
        knee_alignment = "varus"
    else:
        knee_alignment = "normal"

    avg_ankle_tilt = float(np.mean(ankle_sm))
    avg_hip_drop = float(np.mean(hip_sm))
    arch_type = "flat" if avg_ankle_tilt > 8 else "high" if avg_ankle_tilt < -8 else "normal"

    features = GaitFeatures(
        ankle_tilt_deg=avg_ankle_tilt,
        knee_angle_deg=avg_knee,
        hip_drop_ratio=avg_hip_drop,
        stride_symmetry=symmetry,
        cadence_spm=int(cadence),
        strike_bias=strike_bias,
    )

    classifier = HybridGaitClassifier()
    pronation_type, confidence = classifier.predict(features)
    confidence = _adjust_confidence_for_signal_quality(
        base_confidence=confidence,
        frame_count=len(cleaned),
        ankle_series=ankle_sm,
        knee_series=knee_sm,
    )

    insight = _gait_insight(features, pronation_type, knee_alignment)
    profile = GaitProfile(
        pronation_type=pronation_type,
        strike_pattern=strike_pattern,
        knee_alignment=knee_alignment,
        arch_type=arch_type,
        pelvic_symmetry=symmetry,
        cadence_spm=int(cadence),
        confidence=confidence,
        gait_insight=insight,
        raw_features={
            "ankle_tilt_deg": round(avg_ankle_tilt, 2),
            "knee_angle_deg": round(avg_knee, 2),
            "hip_drop_ratio": round(avg_hip_drop, 4),
            "strike_bias": round(strike_bias, 4),
        },
    )
    return profile, features


def _adjust_confidence_for_signal_quality(
    base_confidence: float,
    frame_count: int,
    ankle_series: np.ndarray,
    knee_series: np.ndarray,
) -> float:
    if frame_count <= 2:
        frame_factor = 0.65
    elif frame_count < 8:
        frame_factor = 0.78
    elif frame_count < 18:
        frame_factor = 0.9
    else:
        frame_factor = 1.0

    ankle_var = float(np.std(ankle_series)) if len(ankle_series) else 0.0
    knee_var = float(np.std(knee_series)) if len(knee_series) else 0.0
    variation_factor = 0.9 + min(0.12, (ankle_var + knee_var * 0.02) * 0.04)
    adjusted = base_confidence * frame_factor * variation_factor
    low, high = (0.25, 0.72) if frame_count < 8 else (0.3, 0.92)
    return clamp(adjusted, low, high)


def _smooth(values: list[float]) -> np.ndarray:
    arr = np.array(values, dtype=float)
    if len(arr) < 7:
        return arr
    window = 7 if len(arr) >= 7 else len(arr) - (1 - len(arr) % 2)
    return savgol_filter(arr, window_length=window, polyorder=2)


def _estimate_cadence(ankle_tilts: np.ndarray, fps: float) -> int:
    centered = ankle_tilts - np.mean(ankle_tilts)
    zero_crossings = np.where(np.diff(np.signbit(centered)))[0]
    steps = max(2, len(zero_crossings))
    duration_sec = max(1.0, len(ankle_tilts) / max(fps, 1.0))
    cadence = int((steps / duration_sec) * 60)
    return max(90, min(200, cadence))


def _gait_insight(features: GaitFeatures, pronation_type: str, knee_alignment: str) -> str:
    if pronation_type == "overpronation":
        return "Slight inward ankle tilt detected - possible overpronation."
    if pronation_type == "supination":
        return "Outward foot loading pattern detected - possible supination."
    if knee_alignment == "valgus":
        return "Mild inward knee tracking observed during stance."
    if features.stride_symmetry < 0.75:
        return "Minor left-right asymmetry detected in pelvic movement."
    return "Balanced gait pattern detected with neutral foot mechanics."
