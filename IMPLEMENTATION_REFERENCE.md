# GaitFit AI - Implementation Reference (Pitch Material)

Last updated: March 25, 2026

## 1) Product Snapshot

- Product: GaitFit AI
- Tagline: Walk Smart. Wear Right.
- Core promise: Upload a short side-view walking video, analyze gait with computer vision + biomechanics, and return evidence-backed shoe-category recommendations.
- Target mode in V1: Anonymous upload, no auth, fast MVP pipeline.

## 2) Business Problem and Solution

### Problem
- Most users buy shoes using comfort or brand preference only.
- Gait mismatch (overpronation/supination/knee alignment issues) can reduce comfort and increase injury risk.
- Existing gait labs are expensive, slow, and not easily accessible.

### Solution
- Smartphone video based gait analysis (<=10 sec) with explainable output.
- Clear Top-3 shoe category recommendations.
- Visual evidence frames (angles + skeleton overlay) so the result is understandable, not black-box text.

## 3) Current Implementation Status (What is already built)

### Backend Pipeline (working)
1. Video upload and validation
2. Video normalization and frame sampling
3. Pose extraction (MediaPipe)
4. Gait feature extraction
5. Hybrid classification (rule-based + lightweight logistic model)
6. Shoe category recommendation
7. Visual evidence generation (main frame + 3 key frames)
8. Report export (JSON + PDF)

### Frontend Experience (working)
- Premium dark landing page (sports-tech direction)
- Upload page with constraints and progress
- Analysis progress UI with polling
- Results page with:
  - Gait profile card
  - Gait insight sentence
  - Top-3 recommendations with confidence
  - Evidence viewer with key-frame selection
  - Download buttons for evidence images + JSON + PDF
- EN/Hindi toggle (static translation)
- Contact page + footer links

## 4) Implemented Tech Stack

### Backend
- FastAPI
- OpenCV
- MediaPipe
- NumPy + SciPy
- scikit-learn (LogisticRegression bootstrap model)

### Frontend
- React + Vite
- Custom CSS (premium dark + gradients + glass-like cards)
- React Router

### Infra/DevOps
- Render deployment config: `render.yaml`
- Vercel config: `frontend/vercel.json`
- GitHub Actions scaffold: `.github/workflows/deploy.yml`

## 5) Repository Structure

```text
backend/
  main.py                # API routes and job orchestration
  video_processor.py     # video normalization + sampled frames
  pose_extractor.py      # MediaPipe landmark extraction
  gait_analyzer.py       # feature extraction + hybrid classifier
  recommender.py         # category scoring and top-3 output
  visualizer.py          # annotated evidence image generation
  report_builder.py      # PDF report generation
  models.py              # dataclasses for profile/recommendations
  data/
    analysis_results.json
    shoe_catalogue.json
  tests/
    test_gait_analyzer.py
    test_recommender.py

frontend/src/
  pages/
    LandingPage.jsx
    UploadPage.jsx
    AnalysisPage.jsx
    ResultsPage.jsx
    ContactPage.jsx
  components/
    VideoUploader.jsx
    ProgressStepper.jsx
    GaitReportCard.jsx
    VisualEvidence.jsx
    ShoeCard.jsx
    SiteFooter.jsx
    LanguageToggle.jsx
  api/gaitfit.js
  styles.css

Implementation/
  ARCHITECTURE_PLAN.md
  IMPLEMENTATION_PLAN.md
  PREREQUISITES.md

done.md
README.md
```

## 6) Backend API Contract (Current)

### Health
- `GET /health`
- Response: `{ "status": "ok" }`

### Upload
- `POST /upload-video` (multipart file)
- Constraints:
  - Max size: 50 MB
  - Max duration: 10 seconds
  - Formats: `.mp4`, `.mov`, `.m4v`
- Response: `{ "job_id": "..." }`

### Job Status
- `GET /status/{job_id}`
- Returns queue/progress state:
  - `status`: `queued | processing | done | failed`
  - `progress`: number
  - `message`
  - `error` (if failed)

### Results
- `GET /results/{job_id}`
- Returns:
  - `gait_profile`
  - `recommendations` (Top 3)
  - `summary`
  - `evidence` (main + key frames)
  - `meta` (video orientation, dimensions, duration)

### PDF Report
- `GET /report/{job_id}.pdf`

### Static Assets
- `GET /assets/{file}`
- Used to serve generated evidence images and debug pose JSON.

## 7) Gait Analysis Logic (Implemented)

### Extracted core signals
- Ankle tilt angle
- Knee angle
- Hip drop ratio
- Strike bias
- Cadence estimate
- Stride/pelvic symmetry

### Classification approach
- Rule logic for clear pronation cases
- LogisticRegression for lightweight ML blending
- Confidence score blended from ML confidence + rule confidence

### Primary outputs
- `pronation_type`: neutral / overpronation / supination
- `strike_pattern`: heel / midfoot / forefoot
- `knee_alignment`: normal / valgus / varus
- `arch_type`: flat / normal / high
- `pelvic_symmetry`
- `cadence_spm`
- `confidence`
- `gait_insight` narrative sentence

## 8) Recommendation Engine (Implemented)

- Scope in V1: Shoe categories only (not brand-specific SKU recommendation).
- Categories currently mapped:
  - Stability Shoes
  - Motion Control Shoes
  - Cushioned Shoes
  - Neutral Running Shoes
- Strategy:
  - Score categories from gait profile rules
  - Multiply by confidence
  - Return Top 3 with short "why this fits" explanations

## 9) Visual Evidence System (Implemented)

### What is generated
- Main annotated frame with:
  - Skeleton overlay
  - Knee + ankle angle labels
  - Frame/side metadata
- 3 key gait frames:
  - Initial Contact
  - Mid Stance
  - Toe Off

### UX capabilities
- Click any key frame to focus it in hero evidence panel
- Aspect-ratio-safe rendering for portrait and landscape videos
- Per-frame quality scoring and captions
- Download each evidence image

## 10) Frontend/Design Implementation

### Current style direction
- Premium sports-tech dark interface
- Electric blue and neon green accents
- Glass/gradient card treatment
- Motion cues in hero and visual blocks

### Content and navigation
- Landing sections for:
  - Hero value proposition
  - "Our Science"
  - "How it Works"
  - Evidence-first value block
- CTA flow to upload and analyze
- Contact page and rich footer with website/GitHub/LinkedIn/email/location links

### Internationalization
- EN / Hindi toggle
- Static translation object based approach (intentionally simple for V1)

## 11) Data Handling and Privacy in V1

- Uploaded videos are temporary and processed for analysis.
- Derived outputs are stored for debugging and product improvement:
  - extracted features
  - classification results
  - generated evidence assets
- CORS is configurable via `FRONTEND_ORIGINS`.

## 12) Quality and Error Handling

### Implemented safeguards
- File type check
- Size check
- Duration check
- Low-visibility detection (guides user to retry with better lighting/framing)
- Analysis failure state with actionable retry tips

### Testing
- Backend unit tests present for:
  - gait analyzer
  - recommender

## 13) Phase Tracking Against Plan

### Completed/mostly completed
- Phase 1: Upload + processing + pose extraction
- Phase 2: Feature extraction + classification
- Phase 3: Recommendation engine
- Phase 4: Frontend flow and core UI
- Phase 5: End-to-end integration + evidence outputs + downloads

### Remaining (next)
1. Threshold tuning using more real-world videos (lighting, distance, camera angle diversity)
2. Production deployment and hardening (Render + Vercel live validation)
3. Final investor-grade motion/typography polish pass
4. Extended dataset and evaluation benchmarks for confidence calibration

## 14) What is intentionally NOT in V1

- No authentication
- No brand-level product matching (category-level only)
- No Claude personalized narrative integration (explicitly deferred)
- No admin/debug dashboard in UI
- No websocket complexity (polling used for speed of implementation)

## 15) Pitch-Ready Talking Points

- "From 10-second phone video to explainable gait recommendation in under a minute."
- "Not just text output: visual evidence with angle overlays and key gait events."
- "Hybrid AI approach: biomechanical rules + lightweight ML for practical MVP accuracy."
- "Category-first recommendation strategy enables easy brand mapping in Phase 2."
- "Built modularly for fast iteration and deployment on low-cost infrastructure."

## 16) Suggested Slide Mapping (for PPT)

1. Problem and market gap
2. GaitFit AI solution overview
3. Product flow (Upload -> Analyze -> Recommend)
4. Architecture and AI pipeline
5. Evidence-first output screenshots
6. Recommendation logic and explainability
7. Tech stack and deployment readiness
8. Current progress vs roadmap
9. Go-to-market extension (brand mapping next)

## 17) Key Files for Demo Prep

- Product overview: `README.md`
- Progress tracking: `done.md`
- Architecture reference: `Implementation/ARCHITECTURE_PLAN.md`
- Execution plan: `Implementation/IMPLEMENTATION_PLAN.md`
- Main backend API: `backend/main.py`
- Main results UI: `frontend/src/pages/ResultsPage.jsx`
- Evidence UI: `frontend/src/components/VisualEvidence.jsx`
- Landing UX: `frontend/src/pages/LandingPage.jsx`

---

If you want, I can create a second file next: `PITCH_ONE_PAGER.md` (1-page investor version) and `PPT_SCRIPT.md` (slide-by-slide speaking script) from this same source.
