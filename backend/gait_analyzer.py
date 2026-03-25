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
        model = LogisticRegression(max_iter=500)
        model.fit(x, y)
        return model

    def predict(self, f: GaitFeatures) -> tuple[str, float]:
        vector = np.array(
            [[f.ankle_tilt_deg, f.knee_angle_deg, f.hip_drop_ratio, f.stride_symmetry, f.cadence_spm, f.strike_bias]]
        )
        rule_label = _pronation_from_rules(f.ankle_tilt_deg)
        rule_conf = _rule_confidence(f.ankle_tilt_deg)
        if self.model is None:
            return rule_label, rule_conf
        probs = self.model.predict_proba(vector)[0]
        labels = self.model.classes_
        ml_idx = int(np.argmax(probs))
        ml_label = str(labels[ml_idx])
        ml_conf = float(probs[ml_idx])
        # Blend rule and ML confidence while allowing ML to override borderline rule outcomes.
        if abs(f.ankle_tilt_deg) > 10:
            label = rule_label
        else:
            label = ml_label
        confidence = clamp(0.6 * ml_conf + 0.4 * rule_conf, 0.0, 1.0)
        return label, confidence


def _pronation_from_rules(ankle_tilt_deg: float) -> str:
    if ankle_tilt_deg >= 8:
        return "overpronation"
    if ankle_tilt_deg <= -8:
        return "supination"
    return "neutral"


def _rule_confidence(ankle_tilt_deg: float) -> float:
    return clamp(abs(ankle_tilt_deg) / 18.0, 0.35, 0.95)


def analyze_gait(frame_poses: list[dict[str, Any]], sampled_fps: float = 10.0) -> tuple[GaitProfile, GaitFeatures]:
    if not frame_poses:
        raise ValueError("No pose data extracted from video.")
    cleaned = [p for p in frame_poses if p.get("landmarks")]
    if len(cleaned) < 8:
        raise ValueError("Insufficient detectable body frames. Please upload a clearer side-view walking video.")

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

    ankle_sm = _smooth(ankle_tilts)
    knee_sm = _smooth(knee_angles)
    hip_sm = _smooth(hip_drops)

    cadence = _estimate_cadence(ankle_sm, sampled_fps)
    symmetry = clamp(1.0 - float(np.std(hip_sm) * 4), 0.0, 1.0)
    strike_bias = float(np.mean(strikes))
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

