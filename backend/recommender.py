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
        "stability": 0.45,
        "motion_control": 0.35,
        "cushioned": 0.35,
        "neutral_running": 0.35,
    }

    if profile.pronation_type == "overpronation":
        base_scores["stability"] += 0.35
        base_scores["motion_control"] += 0.25
    elif profile.pronation_type == "supination":
        base_scores["cushioned"] += 0.35
    else:
        base_scores["neutral_running"] += 0.35

    if profile.knee_alignment == "valgus":
        base_scores["motion_control"] += 0.2
        base_scores["stability"] += 0.1
    if profile.strike_pattern == "heel":
        base_scores["cushioned"] += 0.15
    if profile.arch_type == "flat":
        base_scores["stability"] += 0.15
    if profile.arch_type == "high":
        base_scores["cushioned"] += 0.15

    recs: list[Recommendation] = []
    for shoe_type, score in base_scores.items():
        fit_score = clamp(score * profile.confidence, 0.0, 0.99)
        explanation = _explain(shoe_type, profile)
        recs.append(Recommendation(shoe_type=shoe_type, match_score=fit_score, why_this_fits=explanation))

    recs.sort(key=lambda r: r.match_score, reverse=True)
    return recs[:3]


def _explain(shoe_type: str, profile: GaitProfile) -> str:
    base = CATEGORY_EXPLANATIONS[shoe_type]
    return f"{base} Based on your {profile.pronation_type} pattern with {profile.strike_pattern} strike."

