# Problem Definition: GitHub Repository Forecasting

## Executive Summary
This document establishes the mathematical and conceptual problem formulation for the **Repository Intelligence Platform (RIP)**.

RIP treats open-source GitHub repositories as dynamic, non-stationary time-series processes. Rather than assigning arbitrary static quality scores, RIP models the probabilistic transition of a repository's state over future observation horizons $H \in \{90, 180, 365\}$ days based on point-in-time snapshot observations $S(t_0)$.

---

## 1. Mathematical Formulation

Let a repository $R$ be represented as a continuous event stream $\mathcal{E}_R = \{e_1, e_2, \dots, e_N\}$, where each event $e_i = (t_i, \text{type}_i, \text{payload}_i)$ represents a commit, issue creation, pull request merge, release tag, or star event occurring at timestamp $t_i$.

### 1.1 Snapshot Operator
We define the **Snapshot Operator** $\mathcal{S}(R, t_0)$ as the projection of the event stream $\mathcal{E}_R$ filtered strictly up to timestamp $t_0$:

$$\mathcal{S}(R, t_0) = \{ e_i \in \mathcal{E}_R \mid t_i \le t_0 \}$$

### 1.2 Feature Map
A deterministic feature transformation function $\phi: \mathcal{S}(R, t_0) \to \mathbb{R}^d$ maps the historical snapshot payload into a $d$-dimensional feature vector $\mathbf{x}_{t_0}$:

$$\mathbf{x}_{t_0} = \phi(\mathcal{S}(R, t_0))$$

Feature domains include temporal commit velocity ($\frac{dC}{dt}$), commit acceleration ($\frac{d^2C}{dt^2}$), star growth velocity, maintainer response time distributions, and contributor retention rates.

### 1.3 Forward Outcome Operator
For a given prediction horizon $H > 0$, the **Forward Outcome Operator** $\mathcal{O}(R, t_0, H)$ observes events strictly within the future window $(t_0, t_0 + H]$:

$$\mathcal{O}(R, t_0, H) = \{ e_i \in \mathcal{E}_R \mid t_0 < t_i \le t_0 + H \}$$

Target labels $y_{t_0}^H \in \{0, 1\}$ (or $\mathbb{R}$) are generated as deterministic functionals of $\mathcal{O}(R, t_0, H)$.

### 1.4 Learning Objective
The learning goal is to train calibrated conditional estimators $f_\theta(\mathbf{x}_{t_0}; H)$ that output the probability distribution of future outcomes:

$$\hat{y}_{t_0}^H = f_\theta(\mathbf{x}_{t_0}; H) \approx P(y_{t_0}^H = 1 \mid \mathbf{x}_{t_0})$$

---

## 2. Decoupling ML Inference from Product Reports

A fundamental design choice in RIP is the complete separation between **Probabilistic Model Targets** and **Product Health Metrics**:

- **ML Models**: Learn objective, un-arguable physical events (e.g., "Will zero commits occur in 90 days?", "Will stars grow by $\ge 25\%$ in 180 days?").
- **Product Layer**: Computes a deterministic, explainable `Repository Health Index` from calibrated ML probabilities using explicit weightings.
