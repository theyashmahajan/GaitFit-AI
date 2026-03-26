from __future__ import annotations

from typing import Any

import numpy as np
from scipy.signal import find_peaks, savgol_filter

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
        neutral = rng.normal([0, 175, 0.05, 0.92, 160, 0.0], [3, 3, 0.02, 0.03, 8, 0.3], (90, 6))
        overpronation = rng.normal([13, 167, 0.09, 0.84, 150, -0.2], [4, 4, 0.03, 0.05, 8, 0.4], (90, 6))
        supination = rng.normal([-11, 176, 0.04, 0.9, 158, 0.2], [4, 3, 0.02, 0.04, 8, 0.3], (90, 6))
        x = np.vstack([neutral, overpronation, supination])
        y = np.array(["neutral"] * 90 + ["overpronation"] * 90 + ["supination"] * 90)
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


def analyze_gait(
    frame_poses: list[dict[str, Any]],
    sampled_fps: float = 10.0,
    input_mode: str = "video",
) -> tuple[GaitProfile, GaitFeatures]:
    if not frame_poses:
        raise ValueError("No pose data extracted from media.")
    cleaned = [p for p in frame_poses if p.get("landmarks")]
    if len(cleaned) < 1:
        raise ValueError("No detectable body frame. Please upload a clearer side-view image/video.")

    if input_mode == "photo":
        return _analyze_photo(cleaned), _photo_features(cleaned)

    ankle_tilts: list[float] = []
    knee_angles: list[float] = []
    hip_drops: list[float] = []
    strikes: list[float] = []

    for frame in cleaned:
        lm = frame["landmarks"]
        l_hip, r_hip = lm["left_hip"][:3], lm["right_hip"][:3]
        l_knee, r_knee = lm["left_knee"][:3], lm["right_knee"][:3]
        l_ankle, r_ankle = lm["left_ankle"][:3], lm["right_ankle"][:3]
        l_heel, r_heel = lm["left_heel"][:3], lm["right_heel"][:3]
        l_toe, r_toe = lm["left_foot_index"][:3], lm["right_foot_index"][:3]

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
    knee_alignment = "valgus" if avg_knee < 169 else "varus" if avg_knee > 181 else "normal"
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

    gait_events, per_leg = _detect_gait_events_and_per_leg_metrics(cleaned, sampled_fps)
    asym = _asymmetry_score(per_leg.get("left", {}), per_leg.get("right", {}))
    if asym > 15:
        gait_insight = "Noticeable left-right gait asymmetry detected (>15%)."
    else:
        gait_insight = _gait_insight(features, pronation_type, knee_alignment)

    profile = GaitProfile(
        pronation_type=pronation_type,
        strike_pattern=strike_pattern,
        knee_alignment=knee_alignment,
        arch_type=arch_type,
        pelvic_symmetry=symmetry,
        cadence_spm=int(cadence),
        confidence=confidence,
        confidence_cap=0.92,
        input_mode="video",
        gait_insight=gait_insight,
        gait_events=gait_events,
        left_leg={k: round(v, 3) for k, v in per_leg.get("left", {}).items()},
        right_leg={k: round(v, 3) for k, v in per_leg.get("right", {}).items()},
        asymmetry_score=round(asym, 2),
        raw_features={
            "ankle_tilt_deg": round(avg_ankle_tilt, 2),
            "knee_angle_deg": round(avg_knee, 2),
            "hip_drop_ratio": round(avg_hip_drop, 4),
            "strike_bias": round(strike_bias, 4),
        },
    )
    return profile, features


def _analyze_photo(cleaned: list[dict[str, Any]]) -> GaitProfile:
    lm = cleaned[0]["landmarks"]
    l_heel, l_ankle, l_toe = lm["left_heel"][:3], lm["left_ankle"][:3], lm["left_foot_index"][:3]
    r_heel, r_ankle, r_toe = lm["right_heel"][:3], lm["right_ankle"][:3], lm["right_foot_index"][:3]
    ankle_tilt = ((safe_angle(l_heel, l_ankle, l_toe) - 170.0) + (safe_angle(r_heel, r_ankle, r_toe) - 170.0)) / 2.0
    arch_type = "flat" if ankle_tilt > 8 else "high" if ankle_tilt < -8 else "normal"
    pronation = "overpronation" if ankle_tilt > 8 else "supination" if ankle_tilt < -8 else "neutral"
    confidence = min(0.55, 0.35 + min(0.2, abs(ankle_tilt) / 40.0))
    profile = GaitProfile(
        pronation_type=pronation,
        strike_pattern="midfoot",
        knee_alignment="normal",
        arch_type=arch_type,
        pelvic_symmetry=0.0,
        cadence_spm=0,
        confidence=round(confidence, 3),
        confidence_cap=0.55,
        input_mode="photo",
        gait_insight="Static photo estimate only. For best accuracy, upload a walking side-view video.",
        gait_events={"heel_strike": [], "mid_stance": [], "toe_off": []},
        left_leg={},
        right_leg={},
        asymmetry_score=0.0,
        raw_features={"ankle_tilt_deg": round(float(ankle_tilt), 2)},
    )
    return profile


def _photo_features(cleaned: list[dict[str, Any]]) -> GaitFeatures:
    lm = cleaned[0]["landmarks"]
    l_heel, l_ankle, l_toe = lm["left_heel"][:3], lm["left_ankle"][:3], lm["left_foot_index"][:3]
    r_heel, r_ankle, r_toe = lm["right_heel"][:3], lm["right_ankle"][:3], lm["right_foot_index"][:3]
    ankle_tilt = ((safe_angle(l_heel, l_ankle, l_toe) - 170.0) + (safe_angle(r_heel, r_ankle, r_toe) - 170.0)) / 2.0
    return GaitFeatures(
        ankle_tilt_deg=float(ankle_tilt),
        knee_angle_deg=0.0,
        hip_drop_ratio=0.0,
        stride_symmetry=0.0,
        cadence_spm=0,
        strike_bias=0.0,
    )


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


def _detect_gait_events_and_per_leg_metrics(
    cleaned: list[dict[str, Any]],
    sampled_fps: float,
) -> tuple[dict[str, list[int]], dict[str, dict[str, float]]]:
    events: dict[str, list[int]] = {"heel_strike": [], "mid_stance": [], "toe_off": []}
    per_leg: dict[str, dict[str, float]] = {"left": {}, "right": {}}
    for side in ("left", "right"):
        y_series = []
        for p in cleaned:
            lm = p["landmarks"]
            if f"{side}_ankle" in lm:
                y_series.append(float(lm[f"{side}_ankle"][1]))
            else:
                y_series.append(np.nan)
        arr = np.array(y_series, dtype=float)
        if np.all(np.isnan(arr)):
            continue
        arr = _fill_nan(arr)
        inv = -arr
        min_distance = max(3, int(sampled_fps * 0.35))
        heel_idx, _ = find_peaks(inv, distance=min_distance)
        dy = np.gradient(arr)
        toe_idx, _ = find_peaks(-dy, distance=min_distance)
        heel = [int(i) for i in heel_idx.tolist()]
        toe = [int(i) for i in toe_idx.tolist()]
        mids = []
        for h in heel:
            next_toe = next((t for t in toe if t > h), None)
            if next_toe is not None:
                mids.append(int((h + next_toe) // 2))
        events["heel_strike"].extend(heel)
        events["toe_off"].extend(toe)
        events["mid_stance"].extend(mids)
        per_leg[side] = _leg_metrics(cleaned, side, heel, mids, sampled_fps)
    for k in events:
        events[k] = sorted(set(events[k]))
    return events, per_leg


def _leg_metrics(
    cleaned: list[dict[str, Any]],
    side: str,
    heel_events: list[int],
    mid_events: list[int],
    sampled_fps: float,
) -> dict[str, float]:
    out: dict[str, float] = {}
    if len(heel_events) >= 2:
        intervals = np.diff(np.array(heel_events, dtype=float)) / max(sampled_fps, 1.0)
        out["stride_duration_sec"] = float(np.median(intervals))
    knee_angles = []
    pron = []
    for idx in mid_events:
        lm = cleaned[idx]["landmarks"]
        knee_angles.append(
            safe_angle(lm[f"{side}_hip"][:3], lm[f"{side}_knee"][:3], lm[f"{side}_ankle"][:3])
        )
    for idx in heel_events:
        lm = cleaned[idx]["landmarks"]
        pron.append(
            safe_angle(lm[f"{side}_heel"][:3], lm[f"{side}_ankle"][:3], lm[f"{side}_foot_index"][:3]) - 170.0
        )
    if knee_angles:
        out["knee_mid_stance_deg"] = float(np.median(knee_angles))
    if pron:
        out["ankle_pronation_heel_deg"] = float(np.median(pron))
    return out


def _asymmetry_score(left: dict[str, float], right: dict[str, float]) -> float:
    metrics = ("stride_duration_sec", "knee_mid_stance_deg", "ankle_pronation_heel_deg")
    values = []
    for m in metrics:
        if m not in left or m not in right:
            continue
        avg = (abs(left[m]) + abs(right[m])) / 2.0
        if avg < 1e-6:
            continue
        values.append(abs(left[m] - right[m]) / avg * 100.0)
    if not values:
        return 0.0
    return float(np.mean(values))


def _fill_nan(arr: np.ndarray) -> np.ndarray:
    if not np.any(np.isnan(arr)):
        return arr
    idx = np.arange(arr.size)
    good = np.isfinite(arr)
    if good.sum() < 2:
        return np.nan_to_num(arr, nan=np.nanmean(arr))
    arr[~good] = np.interp(idx[~good], idx[good], arr[good])
    return arr


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
    return clamp(adjusted, 0.3, 0.92)


def _smooth(values: list[float]) -> np.ndarray:
    arr = np.array(values, dtype=float)
    if len(arr) < 7:
        return arr
    return savgol_filter(arr, window_length=7, polyorder=2)


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
