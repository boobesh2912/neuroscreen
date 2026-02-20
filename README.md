# NeuroScreen

**Voice-first neurological risk screening platform for early insight and faster clinical follow-up.**

## Overview

NeuroScreen is a full-stack SaaS-style product that analyzes voice recordings to estimate neurological risk signals, especially for Parkinson’s-related screening workflows.  
It helps users capture audio, run ML-powered analysis, view trend dashboards, and book specialist consultations from one interface.

### What problem it solves

Early neurological changes are often subtle and hard to track consistently. NeuroScreen provides a repeatable, lightweight screening workflow that can be used regularly, rather than relying on one-off observations.

### Who it helps

- Individuals monitoring neurological health
- Clinicians who need structured trend summaries
- Product teams exploring practical AI-in-health workflows

### Why it matters

It turns a complex ML pipeline into an accessible product flow: capture -> analyze -> interpret -> act.

---

## Features

- Secure user registration, login, token verification (JWT)
- Voice upload and in-browser recording workflow
- Parkinson’s-focused analysis and multi-disease analysis endpoint
- Risk score, confidence, key biomarker outputs, and recommendations
- Waveform and spectrogram visualization generation
- Dashboard with test history and risk trend tracking
- Doctor discovery, appointment booking, cancellation, and review flows
- Emergency contact management in user profile
- Learning/exercise content and guided educational UX
- Health/readiness endpoints for deployment monitoring
- Structured API error responses and production-safe exception handling

---

## Tech Stack (Auto-detected)

### Frontend

- React 18
- Vite 5
- React Router DOM
- Axios
- Tailwind CSS + PostCSS + Autoprefixer
- Lucide React icons
- ESLint

### Backend

- FastAPI
- Uvicorn (dev server)
- Gunicorn + UvicornWorker (production)
- Pydantic + pydantic-settings
- python-dotenv
- JWT auth (`pyjwt`)
- Audio/ML stack: librosa, numpy, scipy, pandas, scikit-learn, joblib, soundfile, matplotlib

### Database

- SQLite (local/dev default)
- PostgreSQL (production-ready via `DATABASE_URL`, recommended on Render)
- Driver/pool: `psycopg` + `psycopg-pool`
- Startup schema bootstrap (`CREATE TABLE IF NOT EXISTS`) with migration playbook in `backend/MIGRATIONS.md`

### Deployment

- Render Web Service (backend)
- Render Static Site (frontend)
- Procfile-based backend startup command
- SPA fallback via `frontend/public/_redirects`

---

## Demo

Demo: https://your-demo-link-here.com

---

## Screenshots

> Add real product screenshots here before sharing publicly.

- Landing page / marketing view
- Authentication flow (login/register)
- Voice test and analysis results screen
- Dashboard trend screen
- Doctor booking workflow

Example markdown placeholders:

```md
![Landing](./docs/screenshots/landing.png)
![Dashboard](./docs/screenshots/dashboard.png)
![Analysis](./docs/screenshots/analysis.png)
```

---

## Local Setup (Auto-detected Commands)

### Clone repository

```bash
git clone <repo-url>
cd <project-folder>
```

### Backend setup (FastAPI)

1. Create and activate virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Configure backend environment:

```bash
# macOS/Linux
cp backend/.env.example backend/.env
```

```powershell
# Windows PowerShell
Copy-Item backend/.env.example backend/.env
```

4. Migrations / schema setup:

- No Alembic command is required right now.
- Tables are initialized automatically at startup.
- See `backend/MIGRATIONS.md` for production schema rollout strategy.

5. Run FastAPI server:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 5000
```

Optional health checks:

```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/health/readiness
```

### Frontend setup (Vite + React)

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Configure frontend environment:

```bash
# macOS/Linux
cp .env.example .env
```

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

3. Start dev server:

```bash
npm run dev
```

4. Production build:

```bash
npm run build
```

5. Optional preview build locally:

```bash
npm run preview
```

---

## Environment Variables

### Backend (`backend/.env`)

```env
ENVIRONMENT=
LOG_LEVEL=
API_HOST=
API_PORT=
PORT=
DEBUG=

SECRET_KEY=
ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
API_VERSION=

MODEL_PATH=
FEATURE_NAMES_PATH=

DATABASE_URL=
DATABASE_PATH=
DATABASE_SSL_MODE=
DB_POOL_MIN_SIZE=
DB_POOL_MAX_SIZE=
DB_CONNECT_MAX_RETRIES=
DB_CONNECT_RETRY_DELAY_SECONDS=
ALLOW_SQLITE_IN_PRODUCTION=

TEMP_DIR=
UPLOAD_SUBDIR=

MAX_AUDIO_DURATION=
MIN_AUDIO_DURATION=
SUPPORTED_FORMATS=
MAX_FILE_SIZE_MB=

CORS_ORIGINS=
CORS_ALLOW_ORIGIN_REGEX=
CORS_ALLOW_CREDENTIALS=
CORS_ALLOW_METHODS=
CORS_ALLOW_HEADERS=
```

### Frontend (`frontend/.env`)

```env
VITE_API_ROOT_URL=
VITE_DEV_API_PROXY_TARGET=
```

### Quick meaning guide

- `DATABASE_URL`: Primary DB connection string (use Render PostgreSQL in production)
- `DATABASE_PATH`: Local SQLite file path fallback
- `SECRET_KEY`: JWT signing key (must be strong in production)
- `PORT`: Runtime port (set by Render)
- `VITE_API_ROOT_URL`: Frontend API base host (acts as API base URL in production)
- `DATABASE_SSL_MODE`: DB SSL mode (`require` recommended for managed Postgres)
- `ALLOW_SQLITE_IN_PRODUCTION`: Keep `False` unless intentionally deploying SQLite

---

## How to Use

1. Open the frontend app and create an account.
2. Sign in and access the dashboard.
3. Go to **Voice Assessment** and record/upload a voice sample.
4. Submit analysis and review:
   - risk score
   - confidence
   - key voice biomarkers
   - recommendations
5. Track longitudinal changes in the dashboard history.
6. If needed, use **Consultations** to find a doctor and book an appointment.
7. Add emergency contacts in **Profile** for safer escalation workflows.

---

## Project Structure

```text
.
├── backend
│   ├── app
│   │   ├── core            # config, db, security, logging, lifespan
│   │   ├── routers         # auth, analysis, dashboard, doctors, appointments, health, profile
│   │   ├── schemas         # request/response models
│   │   ├── services        # business logic (auth, booking, audio, disease analyzer)
│   │   ├── ml              # ML feature extraction and disease logic
│   │   └── utils
│   ├── data               # audio datasets used for model workflows
│   ├── models             # trained model artifacts
│   ├── scripts            # seed/bootstrap scripts
│   ├── main.py            # FastAPI app entrypoint
│   ├── Procfile           # production start command
│   └── .env.example
├── frontend
│   ├── src
│   │   ├── components     # pages and UI modules
│   │   ├── api.js         # Axios client + API wrappers
│   │   └── App.jsx        # routing + auth gating + metadata
│   ├── public             # PWA assets, manifest, favicon, redirects
│   ├── package.json
│   └── .env.example
├── models                 # shared/legacy model artifacts
└── README.md
```

---

## Deployment on Render

### Backend deploy (Render Web Service)

1. Create a **Web Service**.
2. Set **Root Directory**: `backend`
3. Set **Build Command**:

```bash
pip install -r requirements.txt
```

4. Set **Start Command**:

```bash
gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

(Equivalent from Procfile: `gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:${PORT:-10000} --workers 2 --timeout 120`)

5. Set required backend env vars (minimum):
- `ENVIRONMENT=production`
- `DEBUG=False`
- `SECRET_KEY=<strong-random-secret>`
- `DATABASE_URL=<Render PostgreSQL URL>`
- `DATABASE_SSL_MODE=require`
- `ALLOW_SQLITE_IN_PRODUCTION=False`
- `CORS_ORIGINS=["https://<your-frontend>.onrender.com"]`

6. Validate:
- `GET /api/health`
- `GET /api/health/readiness`

### Frontend deploy (Render Static Site)

1. Create a **Static Site**.
2. Set **Root Directory**: `frontend`
3. Set **Build Command**:

```bash
npm ci && npm run build
```

4. Set **Publish Directory**: `dist`
5. Set env var:
- `VITE_API_ROOT_URL=https://<your-backend>.onrender.com`
6. Deploy and verify SPA routing works (`frontend/public/_redirects` is configured).

---

## Troubleshooting

- **Backend fails at startup with SQLite blocked in production**
  - Cause: `ALLOW_SQLITE_IN_PRODUCTION=False` and no Postgres URL.
  - Fix: set `DATABASE_URL` to Render Postgres, or explicitly set `ALLOW_SQLITE_IN_PRODUCTION=True` (not recommended).

- **CORS errors in browser**
  - Cause: frontend URL not in `CORS_ORIGINS`.
  - Fix: add deployed frontend origin to backend env and redeploy.

- **`ERR_NETWORK` from frontend**
  - Cause: incorrect `VITE_API_ROOT_URL` or backend down.
  - Fix: verify backend health endpoint and frontend env value.

- **`Prediction model is not available on server`**
  - Cause: model artifact path misconfigured.
  - Fix: check `MODEL_PATH` and model files in backend deployment.

- **413 file too large**
  - Cause: upload exceeded backend max size.
  - Fix: reduce audio file size/duration or adjust `MAX_FILE_SIZE_MB`.

---

## Recruiter Note

This project demonstrates end-to-end product engineering: a production-style FastAPI backend, a polished React frontend, ML-powered feature workflows, database reliability controls, and Render deployment readiness. It reflects practical full-stack architecture decisions, not just a UI demo.

---

## Builder’s Note

NeuroScreen started as a hackathon-style idea around Parkinson’s-related voice screening. Over time, it evolved into a more complete product with authentication, analysis APIs, dashboarding, booking workflows, and deployment infrastructure. The focus has been on learning real product architecture through curiosity, experimentation, and shipping practical improvements step by step.