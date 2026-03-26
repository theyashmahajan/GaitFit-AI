from __future__ import annotations

import json
import os
import shutil
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from gait_analyzer import analyze_gait
from pose_extractor import extract_lower_body_landmarks
from quality_checker import check as check_quality
from recommender import recommend_categories
from report_builder import build_report_pdf
from size_estimator import estimate_shoe_size
from video_processor import MAX_SECONDS, extract_sampled_frames, load_image_as_frame, normalize_video
from utils.video_utils import read_video_meta
from visualizer import render_evidence_frame

MAX_UPLOAD_MB = 50
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_EXTENSIONS = VIDEO_EXTENSIONS | IMAGE_EXTENSIONS
MIN_MEAN_VISIBILITY = 0.45

load_dotenv()
origins_env = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS = [v.strip() for v in origins_env.split(",") if v.strip()]

app = FastAPI(title="GaitFit AI Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
TMP_DIR = BASE_DIR / "data" / "tmp_uploads"
OUT_DIR = BASE_DIR / "data" / "processed"
RESULTS_DB = BASE_DIR / "data" / "analysis_results.json"
TMP_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)
if not RESULTS_DB.exists():
    RESULTS_DB.write_text("{}", encoding="utf-8")

app.mount("/assets", StaticFiles(directory=str(OUT_DIR)), name="assets")

JOBS: dict[str, dict[str, Any]] = {}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload-video")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> dict[str, str]:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: mp4, mov, m4v, jpg, jpeg, png, webp.")

    data = await file.read()
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 50MB limit.")

    job_id = str(uuid.uuid4())
    src = TMP_DIR / f"{job_id}{suffix}"
    src.write_bytes(data)
    if suffix in VIDEO_EXTENSIONS:
        meta = read_video_meta(str(src))
        if (meta.get("duration_sec") or 0) > MAX_SECONDS:
            src.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="Video duration must be 10 seconds or less.")

    JOBS[job_id] = {"status": "queued", "progress": 3, "message": "Video received", "error": None}
    background_tasks.add_task(process_job, job_id, str(src))
    return {"job_id": job_id}


@app.get("/status/{job_id}")
async def get_status(job_id: str) -> dict[str, Any]:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/results/{job_id}")
async def get_results(job_id: str) -> dict[str, Any]:
    db = _read_db()
    if job_id not in db:
        raise HTTPException(status_code=404, detail="Result not ready")
    return db[job_id]


@app.get("/report/{job_id}.pdf")
async def get_report_pdf(job_id: str) -> Response:
    db = _read_db()
    payload = db.get(job_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Result not ready")
    pdf = build_report_pdf(payload, OUT_DIR)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=gaitfit_report_{job_id}.pdf"},
    )


def process_job(job_id: str, input_path: str) -> None:
    try:
        suffix = Path(input_path).suffix.lower()
        input_mode = "video" if suffix in VIDEO_EXTENSIONS else "photo"
        if input_mode == "video":
            _update(job_id, "processing", 10, "Normalizing video")
            normalized_path = str(OUT_DIR / f"{job_id}_normalized.mp4")
            normalize_video(input_path, normalized_path)

            _update(job_id, "processing", 22, "Running capture quality checks")
            quality_report = check_quality(normalized_path)
            if not quality_report.get("passed", False):
                _update(
                    job_id,
                    "failed",
                    100,
                    "Capture quality check failed",
                    error="Please retake the video with better capture conditions.",
                    quality_report=quality_report,
                )
                return

            _update(job_id, "processing", 35, "Extracting frames")
            frames, meta = extract_sampled_frames(normalized_path)
            if not frames:
                raise ValueError("No frames extracted from video.")
            if (meta.get("duration_sec") or 0) > MAX_SECONDS + 0.3:
                raise ValueError("Please upload a clip up to 10 seconds.")
        else:
            _update(job_id, "processing", 25, "Reading image")
            frames, meta = load_image_as_frame(input_path)
            normalized_path = ""

        _update(job_id, "processing", 55, "Running pose extraction")
        poses = extract_lower_body_landmarks(frames, static_image_mode=(suffix in IMAGE_EXTENSIONS))
        mean_visibility = _mean_visibility(poses)
        if mean_visibility < MIN_MEAN_VISIBILITY:
            raise ValueError(
                "Low body visibility detected. Use brighter lighting, keep full body in frame, and keep camera steady."
            )
        pose_json_path = OUT_DIR / f"{job_id}_poses.json"
        pose_json_path.write_text(json.dumps(poses), encoding="utf-8")

        _update(job_id, "processing", 75, "Analyzing gait features")
        profile, _features = analyze_gait(
            poses,
            sampled_fps=float(meta.get("sampled_fps", 10.0)),
            input_mode=input_mode,
        )
        evidence = render_evidence_frame(
            job_id=job_id,
            frames=frames,
            poses=poses,
            out_dir=OUT_DIR,
            gait_events=profile.gait_events,
        )

        _update(job_id, "processing", 88, "Generating recommendations")
        recs = recommend_categories(profile)
        shoe_size_estimate = estimate_shoe_size(poses, input_type=str(meta.get("input_type", input_mode)))

        payload = {
            "job_id": job_id,
            "gait_profile": asdict(profile),
            "recommendations": [asdict(r) for r in recs],
            "summary": _summary(profile),
            "shoe_size_estimate": shoe_size_estimate,
            "evidence": evidence,
            "meta": {
                "sampled_frames": meta.get("sampled_frames", 0),
                "duration_sec": round(meta.get("duration_sec", 0), 2),
                "width": meta.get("width", 0),
                "height": meta.get("height", 0),
                "orientation": meta.get("orientation", "unknown"),
                "aspect_ratio": round(meta.get("aspect_ratio", 0.0), 4),
                "input_type": meta.get("input_type", "video"),
            },
            "debug": {"pose_file": f"/assets/{pose_json_path.name}"},
        }
        _persist(job_id, payload)
        _update(job_id, "done", 100, "Completed")
    except Exception as ex:  # pragma: no cover
        _update(job_id, "failed", 100, "Processing failed", error=str(ex))
    finally:
        try:
            Path(input_path).unlink(missing_ok=True)
        except Exception:
            pass


def _summary(profile) -> str:
    base = (
        f"Detected {profile.pronation_type} with {profile.strike_pattern} strike and "
        f"{profile.knee_alignment} knee alignment. {profile.gait_insight}"
    )
    if getattr(profile, "input_mode", "video") == "photo":
        return f"{base} This result is from a single photo and has lower confidence."
    return base


def _mean_visibility(poses: list[dict[str, Any]]) -> float:
    values: list[float] = []
    for p in poses:
        lm = p.get("landmarks", {})
        for point in lm.values():
            if len(point) > 3:
                values.append(float(point[3]))
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _update(
    job_id: str,
    status: str,
    progress: int,
    message: str,
    error: str | None = None,
    quality_report: dict[str, Any] | None = None,
) -> None:
    if job_id not in JOBS:
        JOBS[job_id] = {}
    JOBS[job_id].update(
        {"status": status, "progress": progress, "message": message, "error": error, "quality_report": quality_report}
    )


def _read_db() -> dict[str, Any]:
    with RESULTS_DB.open("r", encoding="utf-8") as f:
        return json.load(f)


def _persist(job_id: str, payload: dict[str, Any]) -> None:
    db = _read_db()
    db[job_id] = payload
    with RESULTS_DB.open("w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


@app.on_event("shutdown")
def cleanup_files() -> None:
    for p in TMP_DIR.glob("*"):
        p.unlink(missing_ok=True)
    for p in OUT_DIR.glob("*_normalized.mp4"):
        p.unlink(missing_ok=True)
    try:
        shutil.rmtree(TMP_DIR, ignore_errors=True)
        TMP_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
