from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import cv2

try:
    import mediapipe as mp
except Exception:  # pragma: no cover
    mp = None


LOWER_BODY_IDS = {
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
    "left_heel": 29,
    "right_heel": 30,
    "left_foot_index": 31,
    "right_foot_index": 32,
}


@dataclass
class FramePose:
    frame: int
    landmarks: dict[str, list[float]]


def extract_lower_body_landmarks(frames: list[Any]) -> list[dict[str, Any]]:
    if mp is None:
        raise RuntimeError("MediaPipe is not installed. Run `pip install mediapipe`.")
    pose = mp.solutions.pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    output: list[dict[str, Any]] = []
    for idx, frame in enumerate(frames):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)
        landmarks: dict[str, list[float]] = {}
        if result.pose_landmarks:
            all_lm = result.pose_landmarks.landmark
            for name, lm_idx in LOWER_BODY_IDS.items():
                lm = all_lm[lm_idx]
                landmarks[name] = [float(lm.x), float(lm.y), float(lm.z), float(lm.visibility)]
        output.append(asdict(FramePose(frame=idx, landmarks=landmarks)))
    pose.close()
    return output

