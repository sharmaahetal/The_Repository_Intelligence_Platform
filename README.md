# Repository Intelligence Platform (RIP) 🚀

> **Forecasts the future evolution of GitHub repositories by learning from historical repository snapshots, producing probabilistic predictions for growth, maintainability, and abandonment while generating an explainable, natural language Repository Intelligence Report.**

---

## 🏛️ Architecture Overview

The **Repository Intelligence Platform (RIP)** uses a Service-Oriented Architecture (SOA) with a strict dependency hierarchy:

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
                      Snapshot Engine (backend/app/snapshots/)
                                  │
                                  ▼
                      Normalizer Engine
                                  │
                                  ▼
            Temporal Feature Store (Velocity, Acceleration, Momentum)
                                  │
               ┌──────────────────┴──────────────────┐
               ▼                                     ▼
      Label Generator                       Inference Service
      (Forward Window [t_0, t_0+Δt])                 │
               │                                     ▼
               ▼                           Repository Report Engine
      Dataset Builder                      (Derived Health + Narrative)
               │                                     │
               ▼                                     ▼
      Training Pipeline                      FastAPI Endpoints
               │                                     │
               ▼                                     ▼
        Model Registry                     Browser Extension UI (Zustand)
```

---

## 🎯 Key Design Features

1. **Multi-Snapshot Historical Pipeline**: Models train on point-in-time snapshots $S(t_0)$ rather than static repository data.
2. **Multi-Horizon Probabilistic Matrix**: Explicit forecasts parameterizing outcomes over 90, 180, and 365-day prediction windows ($P(\text{Growth})$, $P(\text{Abandon})$, $P(\text{Retain})$).
3. **Derived Health Index**: Health score is a deterministic, explainable function derived from calibrated probabilistic model outputs (never used directly as a training label).
4. **Causal Temporal Leakage Prevention**: Features for $S(t_k)$ are strictly restricted to data generated $\le t_k$.
5. **Repository Narrative Engine**: Translates raw ML probabilities and SHAP feature attributions into readable natural language synthesis.
6. **Inference Monitoring & Calibration Drift**: Logs live predictions and evaluates accuracy once observation horizons expire ($t_k + H$).
7. **Cross-Browser Extension**: Built with React, Vite, and Zustand for state management; embeds directly into GitHub with dynamic SPA navigation observers.

---

## 📁 Repository Structure

```
repository-intelligence/
├── backend/                  # FastAPI backend server
│   ├── app/
│   │   ├── api/              # HTTP routers (forecast, health, repos)
│   │   ├── collectors/       # GitHub API integration
│   │   ├── raw_store/        # JSON payload persistence
│   │   ├── snapshots/        # Snapshot Engine
│   │   ├── normalizers/      # Raw payload -> relational schema
│   │   ├── features/         # Temporal Feature Store Engine
│   │   ├── narrative/        # Repository Narrative Engine
│   │   ├── monitoring/       # Drift & Accuracy Monitoring Service
│   │   ├── database/         # Async PostgreSQL & Redis connections
│   │   ├── config/           # Modularized settings
│   │   └── main.py           # FastAPI entrypoint
├── datasets/                 # Dataset & Label Generation Service
│   ├── label_generator.py    # Forward observation window labeler
│   └── leakage_guard.py      # Causal temporal leakage assertions
├── ml/                       # Machine Learning Pipeline
│   ├── training/             # XGBoost model trainers
│   ├── inference/            # Multi-horizon inference wrappers
│   └── registry/             # Versioned Model Registry
├── extension/                # Cross-Browser Extension (Vite + React + Zustand)
├── research/                 # Problem formulation & evaluation protocols
├── docs/                     # Architecture & Feature Dictionary docs
└── tests/                    # Unit, integration, and leakage test suite
```

---

## 🛠️ Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

### 1. Run Services with Docker Compose
```bash
docker-compose up --build
```
The FastAPI backend will be available at `http://localhost:8000`. OpenAPI docs: `http://localhost:8000/docs`.

### 2. Extension Development Setup
```bash
cd extension
npm install
npm run dev
```

---

## 🧪 Running Tests
```bash
pytest
```
