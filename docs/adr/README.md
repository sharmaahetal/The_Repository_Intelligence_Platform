# Architectural Decision Records (ADR) Index

This document lists all Architectural Decision Records (ADRs) for the Repository Intelligence Platform (RIP), detailing the rationale, context, and status of major technical decisions.

---

| ADR | Title | Status | Rationale & Impact Summary |
| :--- | :--- | :---: | :--- |
| **[ADR-0001](0001-parquet-dataset-format.md)** | Parquet Dataset Storage Format | **Accepted** | Selected Apache Parquet over CSV/JSON for dataset storage due to columnar compression, zero-copy PyArrow integration, and schema enforcement. |
| **[ADR-0002](0002-xgboost-over-lightgbm.md)** | XGBoost Model Framework Selection | **Accepted** | Chosen over LightGBM due to native SHAP tree explainer integration, robust handling of sparse tabular features, and reliable multi-output calibration. |
| **[ADR-0003](0003-feature-schema-versioning.md)** | Feature Schema Versioning & Stability | **Accepted** | Enforced integer `schema_version` fields in feature vectors to guarantee backward compatibility and prevent model-feature dimension mismatch during inference. |
| **[ADR-0004](0004-pydantic-domain-models.md)** | Pydantic Immutability for Repository Snapshots | **Accepted** | Mandated Pydantic v2 `frozen=True` models for point-in-time snapshots $S(t_k)$ to eliminate data mutation and enforce temporal anti-leakage guards across pipeline stages. |
