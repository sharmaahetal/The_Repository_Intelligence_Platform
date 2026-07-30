# System Architecture: Repository Intelligence Platform (RIP)

## Overview
The **Repository Intelligence Platform (RIP)** is a forecasting-native platform predicting open-source GitHub repository health, maintainability, growth, and abandonment.

---

## Service-Oriented Component Architecture

```
                     ┌───────────────────────────────────┐
                     │    Browser Extension (React)      │
                     │    - observer.ts (SPA Nav)        │
                     │    - inject.ts (Shadow DOM)       │
                     └─────────────────┬─────────────────┘
                                       │ HTTP POST /api/v1/forecast
                                       ▼
                     ┌───────────────────────────────────┐
                     │       FastAPI API Router          │
                     │    - telemetry middleware          │
                     └─────────────────┬─────────────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                ▼                      ▼                      ▼
    ┌──────────────────────┐ ┌──────────────────┐ ┌──────────────────────┐
    │  Collector Service   │ │ Snapshot Engine  │ │ Feature Store Engine │
    │  (GitHub REST/GQL)   │ │ (snapshots/)     │ │ (features/registry)  │
    └───────────┬──────────┘ └─────────┬────────┘ └───────────┬──────────┘
                │                      │                      │
                ▼                      ▼                      ▼
    ┌──────────────────────┐ ┌──────────────────┐ ┌──────────────────────┐
    │  Raw Payload Store   │ │ Normalizer Engine│ │ Dataset Service      │
    │  (PostgreSQL JSONB)  │ │ (Relational DB)  │ │ (label_generator.py) │
    └──────────────────────┘ └──────────────────┘ └───────────┬──────────┘
                                                              │
                                                              ▼
                                                   ┌──────────────────────┐
                                                   │ Model Registry       │
                                                   │ (ml/registry/)       │
                                                   └──────────────────────┘
```

---

## Key Subsystems

### 1. Data Layer & Raw Store
- API responses are saved unmodified into `raw_payload_store` table using PostgreSQL JSONB.
- Shields downstream normalizers and feature pipelines from GitHub API schema changes.

### 2. Snapshot Engine (`backend/app/snapshots/`)
- Groups event payloads into historical snapshot states $S(t_k)$ at specified timestamps.
- Enables backtesting and dataset generation across historical temporal windows.

### 3. Feature Store Engine (`backend/app/features/`)
- Pluggable feature builders registered in `registry.py`.
- Computes velocity, acceleration, and trend features strictly bounded by snapshot timestamp $t_k$.

### 4. Label Generator (`datasets/label_generator.py`)
- Evaluates forward observation window $[t_k, t_k + H]$ to assign ground-truth labels for Growth, Abandonment, and Contributor Retention.

### 5. Repository Narrative Engine (`backend/app/narrative/`)
- Synthesizes model predictions and SHAP feature drivers into natural language report sentences.
