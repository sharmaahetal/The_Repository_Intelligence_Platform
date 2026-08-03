# Testing Strategy & Execution Guide 🧪

The **Repository Intelligence Platform (RIP)** maintains a strict automated test suite covering unit tests, integration tests, anti-leakage assertions, and contract validations.

---

## 🏛️ Test Architecture & Directory Layout

```
tests/
├── backend/                             # API, Collectors, Snapshots & Services
│   ├── test_api_v1.py                   # API router endpoint integration tests
│   ├── test_collector_and_validator.py  # GitHub API collection & validation
│   ├── test_collectors_resilience.py     # Retry, Rate Limiter & Circuit Breaker
│   ├── test_domain_models.py            # Pydantic model immutability
│   ├── test_domain_snapshot_refinements.py # Snapshot ID & provenance tests
│   ├── test_feature_platform_refinements.py # Feature DAG & Manifest tests
│   ├── test_forecast_api.py             # Forecast endpoint contract tests
│   ├── test_logging_and_observability.py# Contextvars & secret redaction
│   ├── test_ml_platform_refinements.py  # Model & Experiment Registry tests
│   ├── test_prediction_pipeline_refinements.py # Idempotency & Stages tests
│   └── test_devops_platform_refinements.py # Probes & Security Headers tests
├── datasets/                            # Dataset Pipeline & Anti-Leakage
│   ├── test_causal_leakage.py           # Temporal leakage boundary assertions
│   └── test_dataset_pipeline.py         # Chronological splitter & exporter
└── ml/                                  # ML Platform
    ├── test_inference.py                # Multi-Horizon Predictor tests
    └── test_training_pipeline.py        # Walk-forward trainer & XGBoost
```

---

## 🚀 Running Tests

### 1. Run All Tests
```bash
pytest
```

### 2. Run Specific Subsystem Tests
```bash
pytest tests/backend/test_prediction_pipeline_refinements.py
```

### 3. Run with Coverage Report
```bash
pytest --cov=backend --cov=ml --cov-report=term-missing
```

---

## 🛡️ Key Testing Principles
1. **Zero Mocking of Domain Logic**: Pure builder functions (`SnapshotBuilder`, `FeatureDAG`, `InferenceService`) are tested with actual objects.
2. **Temporal Anti-Leakage Assertions**: `test_causal_leakage.py` verifies that features generated at $t_k$ contain zero data from $t > t_k$.
3. **Determinism Verification**: Snapshot identity derivation (`snp_<sha256>`) and prediction caching hash keys are verified for strict repeatability.
