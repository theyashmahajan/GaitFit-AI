# ✅ GaitSense — Prerequisites Checklist
## Everything You Need Before Writing a Single Line of Code

---

## 🖥️ 1. Local Machine Setup

### Python
```bash
# Check version — need 3.10 or higher
python --version

# If not installed → https://python.org/downloads
# On Ubuntu/Debian:
sudo apt update && sudo apt install python3.10 python3-pip python3-venv
```

### Node.js
```bash
# Check version — need 18 or higher
node --version

# If not installed → https://nodejs.org
# Recommended: install via nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### ffmpeg
```bash
# Check if installed
ffmpeg -version

# Install on Ubuntu/Debian:
sudo apt install ffmpeg

# Install on macOS:
brew install ffmpeg

# Install on Windows:
# Download from https://ffmpeg.org/download.html and add to PATH
```

### Git
```bash
git --version
# If not installed: https://git-scm.com/downloads
```

---

## ☁️ 2. Accounts to Create (All Free)

| Service | Purpose | URL |
|---|---|---|
| **GitHub** | Code repository + version control | https://github.com |
| **Vercel** | Frontend hosting (free) | https://vercel.com — sign up with GitHub |
| **Render.com** | Backend hosting (free) | https://render.com — sign up with GitHub |
| **Cloudflare** | Video storage (R2, 10GB free) | https://cloudflare.com |

**Important:** Link Vercel and Render to your GitHub account during signup — this enables auto-deploy from GitHub push.

---


### Cloudflare R2 (Optional for Phase 1 — can skip until Phase 6)
1. Go to Cloudflare dashboard → R2 → Create bucket named `gaitsense-videos`
2. Create API token with R2 read/write permissions
3. Note: Account ID, Access Key ID, Secret Access Key

---

## 🐍 4. Python Environment Setup

```bash
# Create project folder
mkdir gaitsense && cd gaitsense

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install all required Python packages
pip install fastapi uvicorn python-multipart
pip install mediapipe opencv-python
pip install numpy scipy
pip install anthropic
pip install python-dotenv
pip install ffmpeg-python
pip install pillow

# Save dependencies
pip freeze > requirements.txt
```

### Verify MediaPipe Works
```python
# Run this to verify MediaPipe is correctly installed
import mediapipe as mp
import cv2

mp_pose = mp.solutions.pose
print("MediaPipe Pose loaded successfully!")
print(f"MediaPipe version: {mp.__version__}")
```

---

## ⚛️ 5. Frontend Setup

```bash
# Inside your gaitsense/ folder
npm create vite@latest frontend -- --template react
cd frontend
npm install

# Install TailwindCSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install other frontend dependencies
npm install axios react-router-dom react-dropzone lucide-react
```

### Configure Tailwind (`tailwind.config.js`):
```javascript
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
```

### Add to `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

## 🧪 6. Verify Your Full Stack Starts

### Test Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
# Should open: http://localhost:8000/docs (FastAPI Swagger UI)
```

### Test Frontend
```bash
cd frontend
npm run dev
# Should open: http://localhost:5173
```

---



# Give it the architecture file on Day 1:
# "Read ARCHITECTURE_PLAN.md and IMPLEMENTATION_PLAN.md, 
#  then help me build Phase 1 — the video upload endpoint and 
#  MediaPipe pose extraction. Start with backend/pose_extractor.py"
```

**Claude Code Tips for This Project:**
- Always tell Claude Code which Phase you're on
- Give it the `models.py` file first — it defines all data structures
- Ask it to write tests alongside each module
- Say "use only free/open-source libraries" if it suggests paid services

---

## 🎥 8. Sample Walking Videos for Testing

You need at least 10 test videos before you can tune your gait analyzer.

**How to record:**
- Barefoot on a flat floor (tile or wood, not carpet)
- Phone held steady at knee height (prop it against a wall)
- Walk toward the camera for "front view" — 3–4 steps
- Walk past the camera for "side view" — 3–4 steps
- Bright lighting, no shadows on feet
- 10–15 seconds per clip

**Who to recruit:**
- Yourself
- 5–8 family/friends with varying foot types
- Try to get at least 2 people with known flat feet

**Naming convention:**
```
test_001_front_flatfoot.mp4
test_001_side_flatfoot.mp4
test_002_front_neutral.mp4
...
```

---

## 📚 9. Background Reading (1–2 hours total)

These are quick reads that will make you much better at building this:

| Topic | What to Read |
|---|---|
| MediaPipe Pose landmarks | https://developers.google.com/mediapipe/solutions/vision/pose_landmarker |
| Gait analysis basics | Search: "gait analysis pronation supination explained" — any physio site |
| Overpronation vs Supination | https://www.runnersworld.com/gear/a20842285/how-to-find-the-right-running-shoe/ |
| Indian shoe brands guide | Campus, Bata, Puma India, Adidas India, Asics India official sites |

---

## ✅ Pre-Flight Checklist

Before opening Claude Code and starting to build, verify ALL of these:

- [ ] Python 3.10+ → `python --version`
- [ ] pip working → `pip --version`
- [ ] Virtual environment created and activated
- [ ] `mediapipe` imported without error
- [ ] `ffmpeg` installed → `ffmpeg -version`
- [ ] Node.js 18+ → `node --version`
- [ ] React app runs → `npm run dev` works
- [ ] GitHub repo created and code pushed
- [ ] Anthropic API key saved in `.env`
- [ ] Vercel account linked to GitHub
- [ ] Render.com account linked to GitHub
- [ ] At least 5 test walking videos recorded
- [ ] Both implementation and architecture docs saved locally

**Once all boxes are checked → you're ready. Start Phase 1.**

---

## 🆘 Common Setup Issues

| Problem | Fix |
|---|---|
| `mediapipe` install fails | Try `pip install mediapipe --pre` or use Python 3.10 (not 3.12) |
| `ffmpeg` not found | Make sure it's in your system PATH |
| MediaPipe can't find camera | For video files, don't use `cv2.VideoCapture(0)` — use file path |
| Render.com cold start slow | Free tier sleeps after 15min. Expected behavior for prototype |
| CORS errors in browser | Add your Vercel URL to FastAPI's CORS allowed origins |
