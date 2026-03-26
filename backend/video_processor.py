from __future__ import annotations

import os
import subprocess
from pathlib import Path

import cv2
import numpy as np

from utils.video_utils import read_video_meta

MAX_SECONDS = 10
TARGET_FPS = 30
LANDSCAPE_TARGET = (1280, 720)
PORTRAIT_TARGET = (720, 1280)
FRAME_SAMPLE_EVERY = 3


def normalize_video(input_path: str, output_path: str) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    source_meta = read_video_meta(input_path)
    target_w, target_h = _choose_target_size(source_meta)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-vf",
        (
            f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,"
            f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,"
            f"fps={TARGET_FPS}"
        ),
        "-t",
        str(MAX_SECONDS),
        "-an",
        output_path,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(output_path):
            return output_path
    except Exception:
        pass
    return _opencv_normalize_fallback(input_path, output_path, target_w, target_h)


def _opencv_normalize_fallback(input_path: str, output_path: str, target_w: int, target_h: int) -> str:
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, TARGET_FPS, (target_w, target_h))
    max_frames = MAX_SECONDS * TARGET_FPS
    written = 0
    while written < max_frames:
        ok, frame = cap.read()
        if not ok:
            break
        letterboxed = _letterbox(frame, target_w, target_h)
        out.write(letterboxed)
        written += 1
    cap.release()
    out.release()
    return output_path


def extract_sampled_frames(video_path: str) -> tuple[list[np.ndarray], dict]:
    meta = read_video_meta(video_path)
    cap = cv2.VideoCapture(video_path)
    frames: list[np.ndarray] = []
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % FRAME_SAMPLE_EVERY == 0:
            frames.append(frame)
        i += 1
    cap.release()
    sampled_fps = meta["fps"] / FRAME_SAMPLE_EVERY if meta["fps"] else 10.0
    meta["sampled_fps"] = sampled_fps
    meta["sampled_frames"] = len(frames)
    return frames, meta


def load_image_as_frame(image_path: str) -> tuple[list[np.ndarray], dict]:
    frame = cv2.imread(image_path)
    if frame is None:
        raise ValueError("Unable to read image file.")
    h, w = frame.shape[:2]
    orientation = "portrait" if h > w else "landscape"
    meta = {
        "duration_sec": 0.0,
        "fps": 0.0,
        "frame_count": 1,
        "width": int(w),
        "height": int(h),
        "orientation": orientation,
        "aspect_ratio": float(w / h) if h else 0.0,
        "sampled_fps": 1.0,
        "sampled_frames": 1,
        "input_type": "image",
    }
    return [frame], meta


def _choose_target_size(meta: dict) -> tuple[int, int]:
    orientation = meta.get("orientation", "landscape")
    return PORTRAIT_TARGET if orientation == "portrait" else LANDSCAPE_TARGET


def _letterbox(frame: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    src_h, src_w = frame.shape[:2]
    if src_h == 0 or src_w == 0:
        return np.zeros((target_h, target_w, 3), dtype=np.uint8)
    scale = min(target_w / src_w, target_h / src_h)
    new_w = max(2, int(src_w * scale))
    new_h = max(2, int(src_h * scale))
    resized = cv2.resize(frame, (new_w, new_h))
    canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
    x_offset = (target_w - new_w) // 2
    y_offset = (target_h - new_h) // 2
    canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
    return canvas
