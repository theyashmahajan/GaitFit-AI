from __future__ import annotations

from models import GaitProfile, Recommendation
from utils.angle_utils import clamp


CATEGORY_EXPLANATIONS = {
    "stability": "Stability shoes can reduce inward roll and improve control through stance.",
    "motion_control": "Motion control shoes provide stronger structure for heavier inward collapse patterns.",
    "cushioned": "Cushioned shoes absorb impact and help with outward-loading feet.",
    "neutral_running": "Neutral running shoes support efficient, balanced gait without over-correction.",
}


def recommend_categories(profile: GaitProfile) -> list[Recommendation]:
    base_scores = {
        "stability": 0.22,
        "motion_control": 0.18,
        "cushioned": 0.2,
        "neutral_running": 0.2,
    }

    if profile.pronation_type == "overpronation":
        base_scores["stability"] += 0.5
        base_scores["motion_control"] += 0.34
        base_scores["cushioned"] -= 0.04
    elif profile.pronation_type == "supination":
        base_scores["cushioned"] += 0.55
        base_scores["neutral_running"] += 0.14
        base_scores["motion_control"] -= 0.06
    else:
        base_scores["neutral_running"] += 0.48
        base_scores["stability"] += 0.1

    if profile.knee_alignment == "valgus":
        base_scores["motion_control"] += 0.22
        base_scores["stability"] += 0.12
        base_scores["neutral_running"] -= 0.05
    elif profile.knee_alignment == "varus":
        base_scores["cushioned"] += 0.08
    if profile.strike_pattern == "heel":
        base_scores["cushioned"] += 0.18
    elif profile.strike_pattern == "forefoot":
        base_scores["neutral_running"] += 0.1
    if profile.arch_type == "flat":
        base_scores["stability"] += 0.24
        base_scores["motion_control"] += 0.12
    if profile.arch_type == "high":
        base_scores["cushioned"] += 0.2

    normalized = _normalize_scores(base_scores)
    recs: list[Recommendation] = []
    for shoe_type, score in normalized.items():
        fit_score = _to_fit_score(score, profile.confidence)
        explanation = _explain(shoe_type, profile)
        recs.append(Recommendation(shoe_type=shoe_type, match_score=fit_score, why_this_fits=explanation))

    recs.sort(key=lambda r: r.match_score, reverse=True)
    return recs[:3]


def _explain(shoe_type: str, profile: GaitProfile) -> str:
    base = CATEGORY_EXPLANATIONS[shoe_type]
    return f"{base} Based on your {profile.pronation_type} pattern with {profile.strike_pattern} strike."


def _normalize_scores(scores: dict[str, float]) -> dict[str, float]:
    shifted = {k: max(0.01, v) for k, v in scores.items()}
    total = sum(shifted.values())
    if total <= 0:
        return {k: 0.25 for k in shifted}
    return {k: v / total for k, v in shifted.items()}


def _to_fit_score(normalized_score: float, confidence: float) -> float:
    # Map rank-weight and analysis confidence to a realistic public score range.
    weighted = (0.6 * normalized_score) + (0.4 * confidence)
    return clamp(0.35 + weighted * 0.5, 0.35, 0.94)
