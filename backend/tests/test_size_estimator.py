from size_estimator import estimate_shoe_size


def test_estimate_shoe_size_returns_estimate():
    pose = {
        "frame": 0,
        "landmarks": {
            "right_knee": [0.6, 0.55, 0.0, 0.95],
            "right_ankle": [0.62, 0.72, 0.0, 0.95],
            "right_heel": [0.6, 0.82, 0.0, 0.95],
            "right_foot_index": [0.69, 0.81, 0.0, 0.95],
        },
    }
    out = estimate_shoe_size([pose] * 10, input_type="video")
    assert out["estimated"] is True
    assert "uk_size" in out
    assert "disclaimer" in out
