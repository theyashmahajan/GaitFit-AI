# GaitFit AI Progress Notes

## Current Phase
- Phase 5 (Integration and MVP Experience) is in progress.

## Completed
- Phase 1:
  - FastAPI upload endpoint with file validation.
  - Async background processing with polling status endpoint.
  - Video normalization and frame sampling pipeline.
  - MediaPipe lower-body pose extraction.
- Phase 2:
  - Feature extraction for ankle/knee/hip/cadence/symmetry.
  - Hybrid classification (rule-based + lightweight logistic model).
  - Gait insight sentence generation.
- Phase 3:
  - Category-level recommendation engine.
  - Top 3 recommendation output with fit score and explanation.
- Phase 4:
  - Frontend flow: landing, upload, analysis, results.
  - Premium dark style foundation.
  - EN/Hindi toggle and static translations.
  - Added global footer and dedicated contact page with founder details.
- Phase 5:
  - Visual evidence generation from uploaded video.
  - Annotated frame with skeleton and knee/ankle angle labels.
  - Evidence image served by backend static route.
  - Derived pose data saved to debug JSON per job.
  - Portrait/landscape-safe normalization and rendering.
  - Added 3 key gait frames: Initial Contact, Mid Stance, Toe Off.
  - Added confidence bar and quick stats on report card.
  - Landing page redesigned with "Our Science" and strong CTA sections.
  - Added download buttons for evidence images and full report JSON.
  - Implemented key-frame click-to-focus interaction (key card updates hero evidence).
  - Refined landing hero to balanced split layout with science visualization panel.
  - Added key-frame event quality scoring and caption metadata.
  - Surfaced evidence quality and captions in results UI.
  - Added low-visibility detection with clearer error guidance.
  - Added retry-help UI on analysis failure with actionable capture tips.
  - Added quality trend data across frames and rendered chart on results page.
  - Added backend PDF report endpoint and frontend PDF download action.
  - Added deployment/environment config files (`render.yaml`, `vercel.json`, `.env.example`).
  - Added low-visibility detection with actionable retry tips in analysis page.
  - Added quality trend chart in report UI.
  - Added downloadable PDF report endpoint and UI integration.
  - Added `shoe_catalogue.json` category dataset scaffold.
  - Added `test_gait_analyzer.py` unit test.
  - Added GitHub workflow scaffold (`.github/workflows/deploy.yml`).
  - Added dual media support for upload: video + single image input.
  - Added image-processing path in backend (`load_image_as_frame`) and static pose mode for photos.
  - Recalibrated hybrid classifier confidence to reduce repeated high confidence outputs.
  - Refined recommendation scoring/normalization to improve variation across different gait inputs.
  - Added estimated shoe-size feature from pose proportions for photo/video uploads.
  - Surfaced estimated size ranges (UK/US/EU), confidence, and disclaimer in result UI and PDF report.
  - Added backend pre-flight capture quality checker (lighting, body visibility, camera stability, side-view confidence).
  - Added quality short-circuit path: failed quality now returns `quality_report` and skips full analysis.
  - Added gait-cycle event detection using ankle trajectories (`heel_strike`, `mid_stance`, `toe_off`).
  - Added per-leg gait metrics and asymmetry score in `GaitProfile`.
  - Added input-mode-aware pipeline behavior (`video` vs `photo`) with capped confidence for photo mode.
  - Added upload Capture Guide modal and frontend pre-submit duration/size validation.
  - Added interactive evidence timeline with event markers and frame selection.
  - Added explainability finding cards (detected/why/action).
  - Added trend dashboard from local scan history (`localStorage`).
  - Added recommendation side-by-side comparison UI.
  - Added conversion-focused CTA action section on results page.

## Remaining Work
- Phase 5:
  - Tune quality scoring thresholds using real user videos.
  - Improve confidence trend interpretation (labels/thresholds).
- Phase 6:
  - Deploy backend to Render and frontend to Vercel.
  - Validate production PDF and asset downloads.
- Phase 7:
  - Investor-grade UI polish and motion tuning.
  - Final brand narrative and pitch walkthrough assets.

## Next Immediate Tasks
1. Validate landing + results UX on mobile and desktop with 8+ test videos.
2. Tune event quality scoring on mixed lighting and camera distances.
3. Final UI polish pass for typography spacing and consistency.
4. Deploy using `render.yaml` + Vercel and run end-to-end production checks.
