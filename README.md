# GaitFit AI

Walk Smart. Wear Right.

AI-powered gait analysis prototype that takes a short side-view walking video, extracts pose landmarks, analyzes gait mechanics, and returns explainable shoe-category recommendations.

## Features

- Side-view video upload (`<= 10s`, `<= 50MB`)
- FastAPI async processing with polling status
- MediaPipe lower-body pose extraction
- Hybrid gait classification (rule-based + lightweight ML)
- Visual evidence output:
  - Main annotated gait frame
  - 3 key gait frames (Initial Contact, Mid Stance, Toe Off)
  - Downloadable evidence images
- Results report:
  - Gait insight + confidence
  - Top 3 shoe category recommendations
  - Downloadable report JSON
- Premium dark frontend with English/Hindi toggle
- Dedicated contact page + global footer with founder contact details
- PDF + JSON downloadable reports

## Tech Stack

- Backend: FastAPI, OpenCV, MediaPipe, NumPy, SciPy, scikit-learn
- Frontend: React, Vite, CSS
- Processing: ffmpeg (with OpenCV fallback normalization)

## Project Structure

```text
backend/
  main.py
  video_processor.py
  pose_extractor.py
  gait_analyzer.py
  recommender.py
  visualizer.py
  models.py
  utils/
  data/
    shoe_catalogue.json
frontend/
  src/
Implementation/
done.md
```

## Local Setup

### 1) Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Health check: `http://localhost:8000/health`

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173`

## API Endpoints

- `POST /upload-video`
- `GET /status/{job_id}`
- `GET /results/{job_id}`
- `GET /report/{job_id}.pdf`
- `GET /assets/{file}` (generated evidence images and debug assets)

## Notes

- `done.md` tracks completed work, current phase, and next tasks.
- Temporary uploads and generated processed files are git-ignored.
- Current recommendation scope is shoe categories (not brand catalog matching yet).
- CI workflow now runs backend tests and frontend build on push to `main`.

## Environment

Copy `.env.example` to `.env` and set values:

- `FRONTEND_ORIGINS` (comma-separated allowed frontend URLs)
- `ANTHROPIC_API_KEY` (optional for later Claude explanation integration)

## Deployment

- Render backend config: [render.yaml](./render.yaml)
- Vercel SPA routing config: [frontend/vercel.json](./frontend/vercel.json)
 .github/
   workflows/deploy.yml
