# ML Target Formulation & Derived Health Index

## Overview
This document specifies the exact ground-truth targets evaluated by the ML pipeline, as well as the deterministic formula for computing the user-facing `Repository Health Index`.

---

## 1. Probabilistic ML Targets

All ML models estimate probabilities for verifiable events occurring within a future observation horizon $H \in \{90, 180, 365\}$ days following snapshot timestamp $t_0$.

### 1.1 Growth Target ($y_{\text{growth}}^H$)
- **Task Type**: Binary Classification
- **Definition**: Evaluates whether the repository expands its user adoption base.
- **Formula**:
  $$y_{\text{growth}}^H = \mathbb{I}\left( \frac{\text{Stars}(t_0 + H) - \text{Stars}(t_0)}{\max(1, \text{Stars}(t_0))} \ge \theta_{\text{growth}} \right)$$
  where threshold $\theta_{\text{growth}} = 0.25$ (25% star growth).

### 1.2 Abandonment Target ($y_{\text{abandon}}^H$)
- **Task Type**: Binary Classification
- **Definition**: Evaluates whether maintainer activity completely ceases.
- **Formula**:
  $$y_{\text{abandon}}^H = \mathbb{I}\left( \text{Commits}(t_0, t_0 + H] = 0 \right)$$

### 1.3 Maintainer Retention Target ($y_{\text{retention}}^H$)
- **Task Type**: Binary Classification
- **Definition**: Evaluates whether core contributors remain engaged.
- **Formula**:
  $$y_{\text{retention}}^H = \mathbb{I}\left( \frac{|\mathcal{C}_{\text{core}}(t_0) \cap \mathcal{C}_{\text{active}}(t_0, t_0 + H]|}{|\mathcal{C}_{\text{core}}(t_0)|} \ge 0.50 \right)$$
  where $\mathcal{C}_{\text{core}}(t_0)$ is the set of top 20% active contributors at $t_0$.

---

## 2. Derived Repository Health Index

The `Repository Health Index` $H_{\text{index}} \in [0, 100]$ is computed deterministically in the business logic service:

$$H_{\text{index}} = \text{Clamp}_{0}^{100}\left( 35 \cdot P(\text{Retain}_H) + 35 \cdot (1 - P(\text{Abandon}_H)) + 30 \cdot P(\text{Growth}_H) \right)$$

### Advantages of Derived Health Index
1. **Explainability**: Enables exact attribution breakdowns showing why a repository score moved.
2. **No Subjective Labels**: Avoids noisy human labeling or arbitrary synthetic scoring during training.
3. **Calibrated Integrity**: Changes directly track calibrated statistical probabilities.
