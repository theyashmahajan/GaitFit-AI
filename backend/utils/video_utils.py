from __future__ import annotations

import cv2


def read_video_meta(video_path: str) -> dict:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"fps": 0.0, "frames": 0, "duration_sec": 0.0, "width": 0, "height": 0, "aspect_ratio": 0.0, "orientation": "unknown"}
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    cap.release()
    duration = (frames / fps) if fps > 0 else 0.0
    aspect_ratio = float(width / height) if height > 0 else 0.0
    orientation = "portrait" if height > width else "landscape"
    return {
        "fps": float(fps),
        "frames": frames,
        "duration_sec": float(duration),
        "width": width,
        "height": height,
        "aspect_ratio": aspect_ratio,
        "orientation": orientation,
    }
