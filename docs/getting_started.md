# Getting Started in 5 Minutes 🚀

Welcome to the **Repository Intelligence Platform (RIP)**! This guide will get your local environment or containerized stack up and running in under 5 minutes.

---

## ⚡ 5-Minute Quick Start (Docker Compose)

The fastest way to launch the full platform stack (FastAPI backend, PostgreSQL database, and Redis cache) is via Docker Compose:

```bash
# 1. Clone the repository
git clone https://github.com/sharmaahetal/The_Repository_Intelligence_Platform.git
cd Predictive_Analytics_Pipeline

# 2. Copy environment template
cp .env.example .env

# 3. Launch container stack
docker compose up --build -d

# 4. Open Interactive OpenAPI / Swagger Documentation
open http://localhost:8000/docs
```

Verify backend health:
```bash
curl http://localhost:8000/api/v1/health/live
# Returns: {"status": "ok", "timestamp": "...", "version": "1.0.0"}
```

---

## 💻 Local Developer Setup (Python + Node.js)

If you prefer running the Python backend and Browser Extension directly on your host machine:

### 1. Prerequisites
- **Python**: 3.11 or 3.12
- **Node.js**: 18+ & npm
- **Git**: 2.30+

### 2. Backend Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package dependencies in editable mode
pip install -e .

# Run pytest test suite
pytest

# Start development backend server with auto-reload
uvicorn backend.app.main:app --reload --port 8000
```

### 3. Browser Extension Setup
```bash
cd extension

# Install extension dependencies
npm install

# Build production bundle (or run watch mode)
npm run build

# Load in Chrome / Brave:
# 1. Open chrome://extensions/
# 2. Enable "Developer mode" (top-right toggle)
# 3. Click "Load unpacked" and select the extension/dist/ directory
```

---

## ⚙️ Configuration Matrix

The platform is configured via environment variables. Below is the complete configuration matrix:

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `APP_ENVIRONMENT` | No | `development` | Environment mode (`development`, `staging`, `production`) |
| `APP_NAME` | No | `Repository Intelligence Platform` | Platform service identifier |
| `LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `GITHUB_TOKEN` | Yes (in prod) | `""` | GitHub Personal Access Token (PAT) for API rate limits |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///./data.db` | Async PostgreSQL or SQLite connection string |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection URL for caching |
| `CORS_ORIGINS` | No | `["*"]` | Allowed CORS origins (must be explicit origins in production) |
| `MODEL_REGISTRY_DIR` | No | `artifacts/registry` | Directory path for versioned model binaries |
