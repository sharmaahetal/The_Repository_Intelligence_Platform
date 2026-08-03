# System Architecture Specification 🏛️

## 1. High-Level Architecture (20-Second Overview)

```mermaid
graph TD
    GitHub["GitHub API"] -->|Raw Payload| Snapshot["Snapshot Engine S(t_k)"]
    Snapshot -->|RepositorySnapshot| Features["Feature Pipeline"]
    Features -->|RepositoryFeatures| ML["ML Model / Inference"]
    ML -->|ForecastDetails| FastAPI["FastAPI Backend"]
    FastAPI -->|ForecastResponse| Extension["Browser Extension"]
```

---

## 2. End-to-End Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant Extension as Browser Extension
    participant API as FastAPI Backend
    participant Builder as Snapshot Builder
    participant Registry as Feature Registry
    participant ML as Inference Engine
    participant Synthesizer as Narrative Synthesizer

    Extension->>API: GET /api/v1/forecast/{owner}/{repo}?horizon=180
    API->>Builder: build_snapshot(owner, repo, t_k)
    Builder-->>API: RepositorySnapshot S(t_k)
    API->>Registry: extract_features(snapshot)
    Registry-->>API: FeatureVector (24 features)
    API->>ML: predict(FeatureVector, horizon=180)
    ML-->>API: ForecastDetails + SHAP Attributions
    API->>Synthesizer: synthesize_report(predictions, shap_values)
    Synthesizer-->>API: Natural Language Report
    API-->>Extension: ForecastResponseDTO
```

---

## 3. Failure Mode & Recovery Matrix

| Component | Failure Scenario | System Handling / Degradation | Recovery Procedure |
|---|---|---|---|
| **GitHub API** | 503 / Rate Limit / Timeout | CircuitBreaker opens, fast-failing; fallback to cached snapshot | Automatic retry with exponential backoff & jitter |
| **Redis Cache** | Connection Refused | Transparent fallback to snapshot builder & direct DB evaluation | Automatic reconnection on next operation |
| **PostgreSQL DB** | OperationalError / Disconnect | Readiness probe returns `"degraded"`, API raises HTTP 503 | Auto-restart via Docker / Connection pool reconnect |
| **Model Registry** | Model Artifact Missing | Fallbacks to default baseline heuristic predictor | Model reload via `/health/ready` initialization |

---

## 4. Architectural Decision Records (ADR Timeline)

```mermaid
timeline
    title System Architecture Evolution
    ADR-0001 : Parquet Dataset Format (Zero-copy PyArrow & Columnar Compression)
    ADR-0002 : XGBoost Model Selection (Native SHAP TreeExplainer Integration)
    ADR-0003 : Feature Schema Lock (Integer Versioning & Anti-Dimension Mismatch)
    ADR-0004 : Pydantic Snapshot Immutability (Temporal Anti-Leakage Guard)
    ADR-0005 : Modularized Settings Root (Centralized Dependency Injection)
```

| ADR | Title | Status | Impact |
| :--- | :--- | :---: | :--- |
| **[ADR-0001](adr/0001-parquet-dataset-format.md)** | Parquet Dataset Storage Format | **Accepted** | Columnar compression & zero-copy PyArrow integration. |
| **[ADR-0002](adr/0002-xgboost-over-lightgbm.md)** | XGBoost Model Selection | **Accepted** | Native SHAP tree explainer integration. |
| **[ADR-0003](adr/0003-feature-schema-versioning.md)** | Feature Schema Versioning | **Accepted** | Integer schema lock preventing vector mismatch. |
| **[ADR-0004](adr/0004-pydantic-domain-models.md)** | Pydantic Snapshot Immutability | **Accepted** | Strict temporal anti-leakage guards. |
| **ADR-0005** | Modularized Settings Root | **Accepted** | Single root configuration & provider DI. |
