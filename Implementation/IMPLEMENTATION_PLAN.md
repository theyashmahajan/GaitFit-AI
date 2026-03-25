# 🏃 GaitSense — AI Gait Analysis & Shoe Recommender
## Implementation Plan (Free Resources | Claude Code Ready)

---

## 📌 Project Overview

**Product:** A web app where a user uploads a short barefoot walking video → AI analyzes their gait pattern → recommends the right shoe type + specific Indian/global shoe models.

**Target:** B2B pitch prototype for Indian shoe brands (Campus, Bata, Puma India, etc.)

**Stack Philosophy:** 100% free-tier friendly. No paid APIs except Anthropic (which you already have). Runs locally or deploys free.

---

## 🗂️ Phase Breakdown

---

### ✅ Phase 0 — Prerequisites & Setup
**Duration: 2–3 days**

> See `PREREQUISITES.md` for full details.

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Git + GitHub account
- [ ] Anthropic API key (free tier or paid)
- [ ] ffmpeg installed locally
- [ ] MediaPipe installed (`pip install mediapipe`)
- [ ] Project scaffolded with Claude Code

---

### 🔨 Phase 1 — Video Ingestion & Pose Extraction
**Duration: 1 week**

**Goal:** Accept a video upload and extract pose keypoints frame-by-frame.

#### Tasks:
- [ ] **1.1** — Set up FastAPI backend with `/upload-video` endpoint
- [ ] **1.2** — Use `ffmpeg` to normalize uploaded video (resize to 720p, 30fps)
- [ ] **1.3** — Run **MediaPipe Pose** on each frame to extract 33 body landmarks
- [ ] **1.4** — Focus on lower-body landmarks: ankles, knees, hips (landmarks 23–32)
- [ ] **1.5** — Store extracted keypoints as JSON per frame
- [ ] **1.6** — Build a simple React frontend with video upload + progress indicator

#### Output:
```json
{
  "video_id": "abc123",
  "frames": [
    { "frame": 0, "landmarks": { "left_ankle": [x, y, z], "right_ankle": [...], ... } },
    ...
  ]
}
```

#### Free Tools Used:
- `mediapipe` (Google, free)
- `ffmpeg` (open source)
- `FastAPI` (Python, free)

---

### 🧠 Phase 2 — Gait Analysis Engine
**Duration: 1.5 weeks**

**Goal:** Detect gait patterns from pose keypoint sequences using rule-based logic + simple ML.

#### Gait Patterns to Detect:

| Pattern | What to Measure |
|---|---|
| **Overpronation** (flat feet) | Ankle inward roll angle across stance phase |
| **Supination** (underpronation) | Ankle outward tilt |
| **Heel striker** | Which landmark hits first — heel vs. midfoot vs. toe |
| **Knee valgus** (knock knees) | Knee tracking inward relative to ankle |
| **Pelvic tilt / lean** | Hip asymmetry left vs. right |
| **Cadence** | Steps per minute from ankle velocity |
| **Stride symmetry** | Left vs. right step timing difference |

#### Tasks:
- [ ] **2.1** — Write `gait_analyzer.py` — rule-based detector using landmark angle calculations
- [ ] **2.2** — Calculate joint angles: ankle dorsiflexion, knee flexion, hip tilt
- [ ] **2.3** — Aggregate across frames → assign confidence score per pattern
- [ ] **2.4** — Output a `GaitProfile` object:
```python
GaitProfile(
  pronation_type="overpronation",       # neutral | overpronation | supination
  strike_pattern="heel_striker",         # heel | midfoot | forefoot
  knee_alignment="valgus",               # normal | valgus | varus
  pelvic_symmetry=0.87,                  # 0.0–1.0 score
  cadence_spm=155,                       # steps per minute
  confidence=0.82                        # overall confidence 0–1
)
```
- [ ] **2.5** — Build unit tests with 5–10 sample keypoint sequences

#### Free Tools Used:
- `numpy` (angle calculations)
- `scipy` (signal smoothing across frames)

---

### 👟 Phase 3 — Shoe Recommendation Engine
**Duration: 1 week**

**Goal:** Map a GaitProfile to shoe type recommendations + specific Indian shoe models.

#### 3.1 — Build the Shoe Catalogue (JSON)
Manually curate a starter catalogue of 40–60 Indian/global shoes:

```json
{
  "shoes": [
    {
      "id": "campus_ogg_plus",
      "name": "Campus OG+",
      "brand": "Campus",
      "price_inr": 1299,
      "shoe_type": "stability",
      "support_level": "moderate",
      "arch_support": "medium",
      "suitable_for": ["overpronation", "flat_feet"],
      "strike_types": ["heel_striker", "midfoot"],
      "image_url": "...",
      "buy_url": "..."
    }
  ]
}
```

#### 3.2 — Mapping Logic

| GaitProfile | Shoe Type | Why |
|---|---|---|
| Overpronation + Heel Strike | **Stability / Motion Control** | Controls inward roll |
| Supination + Forefoot | **Neutral + Extra Cushion** | Needs shock absorption |
| Neutral + Heel Strike | **Neutral cushioned** | Standard support |
| Knee Valgus | **Motion Control** | Corrects inward knee |
| Flat feet (low arch) | **Arch Support / Stability** | Prevents collapse |

#### Tasks:
- [ ] **3.1** — Create `shoe_catalogue.json` with 40–60 curated shoes
- [ ] **3.2** — Write `recommender.py` — rule-based matching engine
- [ ] **3.3** — Add Claude API call to generate a **personalized explanation** in plain English/Hindi
- [ ] **3.4** — Return top 3–5 shoe recommendations with reasoning

---

### 🎨 Phase 4 — Frontend UI (Pitch-Ready)
**Duration: 1 week**

**Goal:** A clean, demo-able React interface that looks good enough to show investors/brands.

#### Pages:
1. **Landing page** — "Know Your Gait. Find Your Shoe." hero section
2. **Upload page** — Drag & drop video or record on mobile
3. **Analysis page** — Animated progress (extracting pose → analyzing gait → matching shoes)
4. **Results page** — Gait report card + shoe recommendations with images + buy links

#### Tasks:
- [ ] **4.1** — Set up React + Vite + TailwindCSS
- [ ] **4.2** — Build video upload component with preview
- [ ] **4.3** — Build animated progress stepper (3 steps)
- [ ] **4.4** — Build GaitReport card component (show pronation type, strike, arch, etc.)
- [ ] **4.5** — Build ShoeCard component (image, name, price, "why this shoe" explanation)
- [ ] **4.6** — Make it mobile-first (users will shoot video on phone)

---

### 🔗 Phase 5 — Integration & End-to-End Flow
**Duration: 3–4 days**

- [ ] **5.1** — Wire frontend upload → backend `/upload-video` → analysis → recommendation
- [ ] **5.2** — Add WebSocket or polling for real-time progress updates
- [ ] **5.3** — Add error handling (bad video, person not detected, too short clip)
- [ ] **5.4** — Test with 10+ real walking videos (record yourself + friends/family)
- [ ] **5.5** — Tune thresholds based on real-world test results

---

### 🚀 Phase 6 — Deployment (Free)
**Duration: 2 days**

| Component | Free Hosting |
|---|---|
| Frontend (React) | **Vercel** (free tier) |
| Backend (FastAPI) | **Render.com** (free tier) or **Railway** |
| Database (shoe catalogue) | JSON file or **Supabase** free tier |
| Video storage | **Cloudflare R2** (10GB free) or local temp |

- [ ] **6.1** — Deploy frontend to Vercel
- [ ] **6.2** — Deploy backend to Render
- [ ] **6.3** — Set up environment variables (Anthropic API key)
- [ ] **6.4** — Test full flow on deployed URLs
- [ ] **6.5** — Get a shareable demo link for pitching

---

### 🎯 Phase 7 — Pitch Polish
**Duration: 2–3 days**

- [ ] **7.1** — Record a 2-min demo video of the full flow
- [ ] **7.2** — Add branding: logo, color scheme, tagline
- [ ] **7.3** — Add a "For Brands" landing page explaining the B2B pitch
- [ ] **7.4** — Prepare the pitch deck (separate doc)

---

## 📅 Total Timeline

| Phase | Duration |
|---|---|
| Phase 0 — Prerequisites | 2–3 days |
| Phase 1 — Video + Pose | 1 week |
| Phase 2 — Gait Analysis | 1.5 weeks |
| Phase 3 — Shoe Recommender | 1 week |
| Phase 4 — Frontend | 1 week |
| Phase 5 — Integration | 3–4 days |
| Phase 6 — Deployment | 2 days |
| Phase 7 — Pitch Polish | 2–3 days |
| **TOTAL** | **~6–7 weeks** |

---

## 💰 Cost Summary

| Item | Cost |
|---|---|
| Vercel (frontend hosting) | Free |
| Render (backend hosting) | Free |
| All Python libraries | Free |
| Cloudflare R2 (video storage) | Free up to 10GB |
| **Total** | **~$0–5/month** |

---

## 🧪 Definition of "Pitch-Ready"

The prototype is pitch-ready when:
1. A user can upload a 10-second barefoot walking video
2. The app detects at least 3 gait characteristics (pronation, strike, symmetry)
3. The app recommends 3 shoes with a plain-English explanation
4. The full flow works on mobile browser
5. A shareable URL exists for live demo
