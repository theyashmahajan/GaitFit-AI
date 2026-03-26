from gait_analyzer import analyze_gait


def _frame(i: int):
    # Minimal synthetic side-view lower-body landmarks for test stability.
    shift = i * 0.002
    return {
        "frame": i,
        "landmarks": {
            "left_hip": [0.45 + shift, 0.45, 0.0, 0.9],
            "right_hip": [0.50 + shift, 0.45, 0.0, 0.9],
            "left_knee": [0.46 + shift, 0.60, 0.0, 0.9],
            "right_knee": [0.51 + shift, 0.60, 0.0, 0.9],
            "left_ankle": [0.47 + shift, 0.76, 0.0, 0.9],
            "right_ankle": [0.52 + shift, 0.76, 0.0, 0.9],
            "left_heel": [0.45 + shift, 0.79, 0.0, 0.9],
            "right_heel": [0.50 + shift, 0.79, 0.0, 0.9],
            "left_foot_index": [0.50 + shift, 0.78, 0.0, 0.9],
            "right_foot_index": [0.55 + shift, 0.78, 0.0, 0.9],
        },
    }


def test_analyze_gait_returns_profile_and_features():
    poses = [_frame(i) for i in range(12)]
    profile, features = analyze_gait(poses, sampled_fps=10.0)
    assert profile.pronation_type in {"neutral", "overpronation", "supination"}
    assert profile.strike_pattern in {"heel", "midfoot", "forefoot"}
    assert 0 <= profile.confidence <= 1
    assert profile.input_mode == "video"
    assert isinstance(profile.gait_events, dict)
    assert isinstance(features.cadence_spm, int)
