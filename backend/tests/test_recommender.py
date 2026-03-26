from models import GaitProfile
from recommender import recommend_categories


def test_recommender_returns_top_three():
    profile = GaitProfile(
        pronation_type="overpronation",
        strike_pattern="heel",
        knee_alignment="valgus",
        arch_type="flat",
        pelvic_symmetry=0.8,
        cadence_spm=150,
        confidence=0.85,
        confidence_cap=0.92,
        input_mode="video",
        gait_insight="test",
        gait_events={},
        left_leg={},
        right_leg={},
        asymmetry_score=0.0,
        raw_features={},
    )
    recs = recommend_categories(profile)
    assert len(recs) == 3
    assert recs[0].match_score >= recs[1].match_score
