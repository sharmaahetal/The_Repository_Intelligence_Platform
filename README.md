# Repository Intelligence Platform (RIP) 🚀

> **Forecasts the future evolution of GitHub repositories by learning from historical repository snapshots, producing probabilistic predictions for growth, maintainability, and abandonment while generating an explainable, natural language Repository Intelligence Report.**

---

## 🏛️ Architecture Overview

The **Repository Intelligence Platform (RIP)** follows a Service-Oriented Architecture (SOA) with strict causal temporal isolation and data isolation boundaries:

```
                      GitHub REST / GraphQL API
                                  │
                                  ▼
                      Collectors (Raw Fetchers)
                                  │
                                  ▼
                      Raw Data Store (PostgreSQL JSONB)
                                  │
                                  ▼
                      Snapshot Engine (`backend/app/snapshots/`)
                                  │
                                  ▼
                      Normalizer Engine (`backend/app/normalizers/`)
                                  │
                                  ▼
             Temporal Feature Store Engine (`backend/app/features/`)
              (Velocity, Acceleration, Density, Governance)
                                  │
               ┌──────────────────┴──────────────────┐
               ▼                                     ▼
      Label Generator Service               Inference Service Engine
      (Forward Window [t_0, t_0+Δt])                 │
               │                                     ▼
               ▼                           Repository Report Engine
      Dataset Builder Engine               (Derived Health + Narrative)
               │                                     │
               ▼                                     ▼
      Training Pipeline                      FastAPI Endpoints
               │                                     │
               ▼                                     ▼
        Model Registry                     Browser Extension UI (Zustand)
```

---

## 🎯 Key Capabilities & Design Innovations

1. **Multi-Snapshot Historical Pipeline**: Models train on point-in-time historical snapshots $S(t_0)$ rather than static repository state, avoiding lookahead bias.
2. **Multi-Horizon Probabilistic Matrix**: Explicit forecasts parameterizing outcomes over 90, 180, and 365-day prediction windows ($P(\text{Growth})$, $P(\text{Abandon})$, $P(\text{Retain})$).
3. **Derived Health Index**: Health score is a deterministic, explainable function derived from calibrated probabilistic model outputs (never used directly as a synthetic training target).
4. **Causal Temporal Leakage Guard**: Features for $S(t_k)$ are strictly restricted to data generated $\le t_k$.
5. **Repository Narrative Engine**: Translates raw ML probabilities and feature attributions into human-readable natural language reports.
6. **Inference Monitoring & Drift Evaluator**: Logs live predictions and evaluates accuracy once observation horizons expire ($t_k + H$).
7. **Cross-Browser Extension**: Built with React, Vite, and Zustand for state management; embeds seamlessly into GitHub repository pages with SPA navigation observers.

---

## 📁 Repository Structure

```
Predictive_Analytics_Pipeline/
├── .github/                  # GitHub Actions CI/CD workflows
├── backend/                  # FastAPI backend server
│   ├── app/
│   │   ├── api/              # HTTP routers (forecast, health, report)
│   │   ├── collectors/       # GitHub API integration & rate limiting
│   │   ├── raw_store/        # JSON payload persistence & repository
│   │   ├── snapshots/        # Point-in-time Snapshot Engine
│   │   ├── normalizers/      # Raw payload -> relational schema converter
│   │   ├── features/         # Temporal Feature Store Engine
│   │   ├── narrative/        # Natural Language Synthesis Engine
│   │   ├── services/         # Intelligence Report Generator Service
│   │   ├── monitoring/       # Drift & Accuracy Tracking Evaluator
│   │   ├── database/         # Async PostgreSQL & Redis connections
│   │   ├── config/           # Modularized environment settings
│   │   └── main.py           # FastAPI entrypoint
├── datasets/                 # Dataset & Label Generation Service
│   ├── label_generator.py    # Forward observation window labeler
│   └── leakage_guard.py      # Causal temporal leakage assertions
├── ml/                       # Machine Learning Pipeline
│   ├── training/             # XGBoost model trainers
│   ├── inference/            # Multi-horizon inference predictor
│   └── registry/             # Versioned Model Registry
├── extension/                # Browser Extension (Vite + React + Zustand)
├── research/                 # Problem formulation & evaluation protocols
├── docs/                     # Architecture & Feature Dictionary documentation
└── tests/                    # Unit, integration, and leakage test suite
```

---

## 🛠️ Getting Started

### Prerequisites
- **Python**: 3.11+
- **Node.js**: 18+
- **Docker & Docker Compose**: (Optional, for containerized deployment)

---

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone git@github.com:sharmaahetal/The_Repository_Intelligence_Platform.git
   cd Predictive_Analytics_Pipeline
   ```

2. **Set up Python Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt pytest ruff
   ```

3. **Run the FastAPI Backend Server**:
   ```bash
   source .venv/bin/activate
   uvicorn backend.app.main:app --reload --port 8000
   ```
   - **API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Health Endpoint**: `GET http://localhost:8000/health`

4. **Run Containerized via Docker Compose**:
   ```bash
   docker-compose up --build
   ```

---

### Browser Extension Setup

1. **Install dependencies and start development server**:
   ```bash
   cd extension
   npm install
   npm run dev
   ```

2. **Build production extension bundle**:
   ```bash
   npm run build
   ```
   Load the compiled `extension/dist` folder directly into Chrome/Edge via `chrome://extensions` (Enable **Developer Mode** -> **Load unpacked**).

---

## 🧪 Testing & Linting

### Run Test Suite
All backend, ML inference, and leakage assertion tests use `pytest`:
```bash
source .venv/bin/activate
pytest
```

### Run Code Formatting & Linting
Enforce Python code quality with `ruff`:
```bash
source .venv/bin/activate
ruff check .
```
To automatically apply fixes:
```bash
ruff check --fix .
```

---

## 📖 Documentation

- **[Feature Dictionary](docs/feature_dictionary.md)**: Catalog of engineered features (velocity, acceleration, density, governance).
- **[Research Notes](research/data_collection_strategy.md)**: Problem formulation, sampling strategies, and evaluation protocols.
- **[Development Guidelines](AGENTS.md)**: Conventional commit conventions and architectural guidelines.

---

## 📜 Development Guidelines

We follow strict **Conventional Commits** for commit messages:
- `feat:` New feature implementations
- `fix:` Bug fixes
- `refactor:` Code refactoring without functionality change
- `test:` Unit or integration test updates
- `docs:` Documentation additions or updates
- `chore:` Maintenance, dependency, or configuration tasks
