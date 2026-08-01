# ADR 0003: Mandatory Explicit Versioning & Schema Locking for Feature Store

- **Status**: Accepted
- **Date**: 2026-08-01
- **Deciders**: Data Engineering & ML Infrastructure

## Context
Adding, removing, or modifying feature computation logic without explicit schema locking creates subtle feature mismatch errors during inference when a trained model expects $N$ features but receives $N+K$ features.

## Decision
Every `Feature` carries an explicit versioned identifier (e.g., `star_density_index:v1`). Every trained model records `feature_schema_version` inside `feature_schema.json` within its versioned registry directory (`registry/<model_name>/v<N>/`).

## Consequences
- **Positive**: Complete prevention of feature vector dimension mismatches; strict backward compatibility auditing; seamless multi-version feature store upgrades.
- **Negative**: Requires formal schema version bumps when introducing new features.
