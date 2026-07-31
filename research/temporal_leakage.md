# Temporal Leakage Prevention Protocol

## Overview
Temporal data leakage is the single most common failure mode in time-series machine learning projects. It occurs when information from the future (post-$t_0$) accidentally influences the features calculated for historical snapshot $S(t_0)$.

This protocol outlines RIP's architectural boundaries to eliminate temporal leakage.

---

## 1. Architectural Guardrails

```
             ┌─────────────────────────────────────────────────────────────┐
             │                  SNAPSHOT TIMESTAMP (t_0)                   │
             └──────────────────────────────┬──────────────────────────────┘
                                            │
                      HISTORY (t <= t_0)    │    FUTURE (t > t_0)
                      ──────────────────    │    ────────────────
                                            │
  [Commits, PRs, Issues, Stars]             │    [Commits, PRs, Issues, Stars]
              │                             │                 │
              ▼                             │                 ▼
      FEATURE GENERATION                    │         LABEL GENERATION
      (X_t0 computed ONLY here)             │         (Y_t0 computed ONLY here)
```

### 1.1 Strict Timestamp Cutting
Every database query in the Feature Store includes an explicit filter: `WHERE created_at <= snapshot_timestamp`.

### 1.2 Chronological Out-of-Time Splitting
Random $k$-fold cross-validation causes temporal leakage because future snapshots leak into training splits. RIP uses **Strict Chronological Splitting**:

- **Training Window**: Snapshots $t_0 \in [2021\text{-01-01}, 2023\text{-12-31}]$
- **Validation Window**: Snapshots $t_0 \in [2024\text{-01-01}, 2024\text{-12-31}]$
- **Test Window (Out-of-Time)**: Snapshots $t_0 \in [2025\text{-01-01}, 2025\text{-12-31}]$

---

## 2. Automated Leakage Assertions

Automated tests in `tests/datasets/test_causal_leakage.py` enforce:
1. Injecting synthetic future events into raw snapshot stores after $t_0$.
2. Re-computing feature vector $X(t_0)$.
3. Asserting that $X_{\text{original}}(t_0) \equiv X_{\text{mutated}}(t_0)$ bit-for-bit.
