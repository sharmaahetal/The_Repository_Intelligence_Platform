# ADR 0001: Primary Use of Apache Parquet Format for Training Datasets

- **Status**: Accepted
- **Date**: 2026-08-01
- **Deciders**: Architecture Review Board

## Context
Historical repository snapshot data and dataset features require high-throughput binary storage, schema preservation, typed column layouts, and high compression ratios. CSV format lacks type safety, compresses poorly, and incurs parsing overhead during dataset assembly.

## Decision
Adopt **Apache Parquet** (`dataset.parquet`) as the primary training dataset export format, accompanied by an immutable JSON manifest (`manifest.json`) recording dataset provenance metadata, git commit hash, and schema versions.

## Consequences
- **Positive**: 10x-50x compression ratio improvement over CSV; exact numeric type preservation (`float32`, `int64`, `bool`); direct zero-copy loading in pandas and PyArrow.
- **Negative**: Binary format requires specialized tools to view raw rows.
