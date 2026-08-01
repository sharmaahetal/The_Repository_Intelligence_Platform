# ADR 0004: Strict Use of Immutable Pydantic Domain Models Across All Pipeline Boundaries

- **Status**: Accepted
- **Date**: 2026-08-01
- **Deciders**: Core Architecture Team

## Context
Using unvalidated Python dictionaries across pipeline stages allows untyped key mutations (e.g. `snapshot["stars"] = "hello"`), leading to runtime type errors in downstream feature calculation or inference.

## Decision
All pipeline data structures (`RepositorySnapshot`, `RepositoryFeatures`, `TargetLabels`, `ForecastPrediction`, `ForecastResponse`) must be defined as immutable Pydantic models using `ConfigDict(frozen=True)` and strict type annotations.

## Consequences
- **Positive**: Complete compile-time and runtime type safety; automatic JSON schema generation; prevention of accidental in-place data mutations; autocomplete in IDEs.
- **Negative**: Minor Pydantic instantiation validation overhead compared to raw dict literals.
