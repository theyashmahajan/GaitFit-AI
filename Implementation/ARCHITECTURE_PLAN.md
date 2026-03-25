# 🏗️ GaitSense — System Architecture
## Finalized Architecture (Free Resources | Claude Code Compatible)

---

## 🎯 Architecture Philosophy

- **Simple over clever** — Rule-based logic first, ML later
- **No GPU required** — MediaPipe runs on CPU
- **Free tier first** — Every component has a free hosting path
- **Claude Code friendly** — Each module is a clear, isolated file Claude Code can build independently
- **Mobile-first input** — Video shot on phone must work end-to-end

---

## 🗺️ High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER (Mobile/Web)                    │
│                  Records 10-sec barefoot walk               │
└───────────────────────┬─────────────────────────────────────┘
                        │ Video Upload (MP4/MOV)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                  │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Upload Page │  │ Progress UI  │  │   Results Page    │  │
│  │ (drag/drop) │  │ (3-step anim)│  │ (GaitCard+Shoes)  │  │
│  └─────────────┘  └──────────────┘  └───────────────────┘  │
│              Hosted on Vercel (Free)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │ REST API + WebSocket
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI / Python)                │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              API LAYER (main.py)                    │   │
│  │  POST /upload-video  →  returns job_id              │   │
│  │  GET  /status/{job_id}  →  returns progress         │   │
│  │  GET  /results/{job_id}  →  returns GaitProfile     │   │
│  │                          + ShoeRecommendations      │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        │                                    │
│  ┌─────────────────────▼───────────────────────────────┐   │
│  │           VIDEO PROCESSOR (video_processor.py)      │   │
│  │  • ffmpeg: normalize → 720p, 30fps, 10s max        │   │
│  │  • Extract frames (every 3rd frame = ~10fps)        │   │
│  │  • Output: frames as numpy arrays                   │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        │                                    │
│  ┌─────────────────────▼───────────────────────────────┐   │
│  │           POSE EXTRACTOR (pose_extractor.py)        │   │
│  │  • MediaPipe Pose on each frame                     │   │
│  │  • Extract 33 landmarks per frame                   │   │
│  │  • Focus: landmarks 23–32 (hips, knees, ankles)     │   │
│  │  • Output: List[FramePose] as JSON                  │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        │                                    │
│  ┌─────────────────────▼───────────────────────────────┐   │
│  │           GAIT ANALYZER (gait_analyzer.py)          │   │
│  │  • Angle calculations (numpy)                       │   │
│  │  • Frame sequence analysis (scipy smoothing)        │   │
│  │  • Detect: pronation, strike, symmetry, cadence     │   │
│  │  • Output: GaitProfile dataclass                    │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        │                                    │
│  ┌─────────────────────▼───────────────────────────────┐   │
│  │          SHOE RECOMMENDER (recommender.py)          │   │
│  │  • Load shoe_catalogue.json                         │   │
│  │  • Rule-based gait → shoe_type mapping              │   │
│  │  • Score + rank shoes by match quality              │   │
│  │  • Call Claude API → generate plain-English report  │   │
│  │  • Output: List[ShoeRecommendation]                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│           Hosted on Render.com (Free)                       │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                         │
│  ┌──────────────────┐    ┌──────────────────────────────┐  │
│  │  Anthropic API   │    │  Cloudflare R2 (video store) │  │
│  │  (Claude Sonnet) │    │  Free up to 10GB             │  │
│  │  Explanation gen │    │  Temp video storage          │  │
│  └──────────────────┘    └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Folder Structure

```
gaitsense/
│
├── backend/
│   ├── main.py                    # FastAPI app, routes
│   ├── video_processor.py         # ffmpeg normalization + frame extraction
│   ├── pose_extractor.py          # MediaPipe pose landmark extraction
│   ├── gait_analyzer.py           # Gait pattern detection (angles, rules)
│   ├── recommender.py             # Shoe matching + Claude API explanation
│   ├── models.py                  # Pydantic data models (GaitProfile, etc.)
│   ├── data/
│   │   └── shoe_catalogue.json    # Curated shoe database (40–60 shoes)
│   ├── utils/
│   │   ├── angle_utils.py         # Joint angle calculation helpers
│   │   └── video_utils.py         # Video I/O helpers
│   ├── tests/
│   │   ├── test_gait_analyzer.py
│   │   └── test_recommender.py
│   ├── requirements.txt
│   └── .env                       # ANTHROPIC_API_KEY
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── UploadPage.jsx
│   │   │   ├── AnalysisPage.jsx
│   │   │   └── ResultsPage.jsx
│   │   ├── components/
│   │   │   ├── VideoUploader.jsx
│   │   │   ├── ProgressStepper.jsx
│   │   │   ├── GaitReportCard.jsx
│   │   │   └── ShoeCard.jsx
│   │   └── api/
│   │       └── gaitsense.js       # API client functions
│   ├── package.json
│   └── vite.config.js
│
├── README.md
└── .github/
    └── workflows/
        └── deploy.yml             # Auto-deploy on push
```

---

## 🔬 Core Data Models

### GaitProfile
```python
@dataclass
class GaitProfile:
    pronation_type: str         # "neutral" | "overpronation" | "supination"
    strike_pattern: str         # "heel" | "midfoot" | "forefoot"
    knee_alignment: str         # "normal" | "valgus" | "varus"
    arch_type: str              # "normal" | "flat" | "high"
    pelvic_symmetry: float      # 0.0–1.0 (1.0 = perfectly symmetric)
    cadence_spm: int            # steps per minute
    confidence: float           # 0.0–1.0 (how sure we are)
    raw_angles: dict            # debug data — all measured angles
```

### ShoeRecommendation
```python
@dataclass
class ShoeRecommendation:
    shoe_id: str
    name: str
    brand: str
    price_inr: int
    shoe_type: str              # "stability" | "neutral" | "motion_control" | "cushioned"
    match_score: float          # 0.0–1.0
    why_this_shoe: str          # Claude-generated explanation in English
    image_url: str
    buy_url: str
```

### API Response
```json
{
  "gait_profile": {
    "pronation_type": "overpronation",
    "strike_pattern": "heel",
    "knee_alignment": "valgus",
    "arch_type": "flat",
    "pelvic_symmetry": 0.78,
    "cadence_spm": 148,
    "confidence": 0.84
  },
  "recommendations": [
    {
      "name": "Campus OG+",
      "brand": "Campus",
      "price_inr": 1299,
      "shoe_type": "stability",
      "match_score": 0.92,
      "why_this_shoe": "Your flat feet and inward ankle roll need a stability shoe. The Campus OG+ has a firm medial post that corrects overpronation and reduces knee stress over long walks.",
      "image_url": "...",
      "buy_url": "..."
    }
  ],
  "summary": "You have flat feet with mild overpronation. Your right ankle rolls inward more than your left. We recommend stability shoes with arch support."
}
```

---

## 🧮 Gait Analysis Logic (How It Works)

### Step 1 — Extract Key Angles Per Frame

```
Ankle Pronation Angle:
  = angle between (heel → ankle → forefoot) projected on frontal plane
  > 15° inward → overpronation
  > 10° outward → supination

Strike Pattern:
  = which landmark contacts "ground" first (lowest Y value at foot strike frame)
  heel landmark lowest → heel striker
  midfoot → midfoot striker
  toe landmark lowest → forefoot striker

Knee Valgus:
  = angle between (hip → knee → ankle) on frontal plane
  < 170° (knees cave inward) → valgus

Arch Type (approximated):
  = relative height of midfoot landmark vs heel and toe
  Low midfoot height → flat arch
  High midfoot height → high arch
```

### Step 2 — Aggregate Across Frames

- Smooth angles with `scipy.signal.savgol_filter` to remove noise
- Identify "stance phase" frames (when foot is on ground) using velocity threshold
- Average angles only during stance phase (most informative)
- Assign confidence based on: how many frames were detected, how stable the values are

### Step 3 — Apply Rules

```python
RULES = {
    ("overpronation", "heel", "flat") : "motion_control",
    ("overpronation", "heel", "normal"): "stability",
    ("overpronation", "midfoot", "flat"): "stability",
    ("neutral", "heel", "normal")      : "neutral_cushioned",
    ("neutral", "midfoot", "normal")   : "neutral_cushioned",
    ("supination", "forefoot", "high") : "cushioned",
    ("supination", "heel", "high")     : "neutral_cushioned",
}
```

---

## 🤖 Claude API Usage (Explanation Generation)

```python
prompt = f"""
You are a shoe fitting expert. A user walked barefoot and their gait was analyzed.

Gait Profile:
- Pronation: {profile.pronation_type}
- Foot Strike: {profile.strike_pattern}
- Arch: {profile.arch_type}
- Knee Alignment: {profile.knee_alignment}
- Pelvic Symmetry: {profile.pelvic_symmetry:.0%}

We are recommending: {shoe.name} ({shoe.shoe_type} type)

Write 2-3 sentences explaining:
1. What the user's gait issue is, in plain simple language
2. Why this specific shoe type helps them
Keep it friendly, non-medical. User is an everyday Indian consumer.
"""
```

---

## 🛠️ Tech Stack Summary

| Layer | Technology | Why | Cost |
|---|---|---|---|
| Frontend | React + Vite + TailwindCSS | Fast, mobile-friendly | Free |
| Backend | FastAPI (Python) | Fast, async, easy | Free |
| Video Processing | ffmpeg | Industry standard | Free |
| Pose Detection | MediaPipe Pose (Google) | CPU-only, accurate | Free |
| Angle Math | NumPy + SciPy | Standard, reliable | Free |
| AI Explanations | Anthropic Claude API | Best text quality | ~$0–5/mo |
| Frontend Host | Vercel | Auto-deploy, fast CDN | Free |
| Backend Host | Render.com | Free 750hrs/month | Free |
| Video Storage | Temp local (Phase 1) → Cloudflare R2 | Simple start | Free |
| Database | JSON file (Phase 1) → Supabase | No DB needed to start | Free |

---

## ⚡ Performance Estimates

| Operation | Time on Free Server |
|---|---|
| Video upload (10s, ~15MB) | 3–5 seconds |
| ffmpeg normalization | 5–10 seconds |
| MediaPipe pose extraction (100 frames) | 15–25 seconds |
| Gait analysis calculation | < 1 second |
| Claude API explanation | 2–4 seconds |
| **Total end-to-end** | **~30–45 seconds** |

This is acceptable for a prototype. Show a progress animation with steps.

---

## 🔐 Security (Minimum Viable)

- Video files deleted from server after processing (never stored permanently in Phase 1)
- API key stored in `.env`, never in frontend
- CORS restricted to your frontend domain
- Max upload size: 50MB cap on backend

---

## 📈 Future Upgrades (Post-Pitch)

| Upgrade | What it adds |
|---|---|
| Train a custom model on gait data | Higher accuracy, replace rule-based logic |
| Add insole pressure mapping | Richer data from phone gyroscope |
| Side + back video simultaneously | More angles = better analysis |
| Brand-specific shoe catalogue API | Live inventory from partner brand |
| Report PDF export | Printable for physio/doctor sharing |
| Hindi language support | Wider India reach |
