# Changelog

All notable changes to the Repository Intelligence Platform (RIP) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-08-02

### 🎉 Major Release — Initial Production Release

#### **Features & Capabilities**:
- **Deterministic Historical Snapshot Engine**: Reliable collection from GitHub REST API v3 with persistent `AsyncClient` connection pooling, exponential backoff with full jitter, ETag `304 Not Modified` support, and rate limit auto-sleeping.
- **Pydantic Immutability & Schema Versioning**: Enforced `frozen=True` domain models for $S(t_k)$ snapshots and integer `schema_version` fields.
- **Temporal Feature Store Engine**: 24-dimensional feature extraction (Velocity, Acceleration, Density, Governance) with temporal anti-leakage guards.
- **Multi-Horizon Probabilistic Inference**: Calibrated XGBoost multi-horizon models parameterizing 90, 180, and 365-day prediction windows ($P(\text{Growth})$, $P(\text{Abandon})$, $P(\text{Retain})$).
- **Explainable Narrative Synthesis Engine**: SHAP tree attribution explainer coupled with natural language narrative synthesis.
- **FastAPI Production Service**: High-performance REST service with Prometheus metrics, health probes, and structured JSON logging.
- **Cross-Browser Extension (Manifest V3)**: React + Zustand content script injecting live repository forecasts directly into GitHub repository pages.

#### **Performance Benchmarks**:
- Snapshot Generation Latency: **$0.103\text{ ms}$**
- Feature Extraction Throughput: **$2,381.5\text{ snapshots/sec}$**
- Prediction Latency ($p_{50}$): **$12.5\text{ ms}$**
- Cache Hit Ratio: **$88.4\%$**
- Memory Footprint: Snapshot model ($0.07\text{ KB}$), API worker ($115\text{ MB}$)

#### **Documentation**:
- System Architecture & Sequence Diagrams ([README.md](README.md))
- Historical Snapshot Engine Architecture ([docs/historical_snapshot_engine.md](docs/historical_snapshot_engine.md))
- Performance & Reliability Report ([docs/performance.md](docs/performance.md))
- Multi-Cloud Deployment Guide ([docs/deployment.md](docs/deployment.md))
- Architectural Decision Records Index ([docs/adr/README.md](docs/adr/README.md))
