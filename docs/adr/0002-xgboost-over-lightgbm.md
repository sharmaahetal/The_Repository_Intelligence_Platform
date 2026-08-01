# ADR 0002: Selection of XGBoost over LightGBM for Core Growth Classifier

- **Status**: Accepted
- **Date**: 2026-08-01
- **Deciders**: ML Engineering Team

## Context
The repository growth prediction task involves tabular time-series snapshot features with non-linear feature interactions, mixed dense activity metrics, and sparse boolean community flags.

## Decision
Select **XGBoost** (`XGBClassifier`) with Universal Binary JSON (`.ubj`) artifact serialization as the primary baseline classifier.

## Consequences
- **Positive**: Native tree SHAP integration (`shap.TreeExplainer`); deterministic training via fixed random seed; exact versioned artifact serialization (`.ubj`); robust handling of missing feature values.
- **Negative**: Slightly longer training times compared to LightGBM histogram binning on small datasets.
