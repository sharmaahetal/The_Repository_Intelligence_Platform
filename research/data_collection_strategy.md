# Data Collection Strategy: Historical Snapshot Reconstruction

## 1. The Historical Reconstruction Problem
The GitHub REST API returns live repository state at $t_{\text{now}}$. Machine learning models require point-in-time snapshot states $S(t_k)$ for historical dates $t_k < t_{\text{now}}$.

RIP uses a **Dual-Stream Reconstruction Strategy**:

## 2. Reconstructing Historical State Variables

| Metric at $t_k$ | Reconstruction Method | Source |
| :--- | :--- | :--- |
| **Stars Count** | Count star events where $t_{\text{star}} \le t_k$ | REST Stargazers API (`starred_at`) |
| **Forks Count** | Count fork events where $t_{\text{fork}} \le t_k$ | GH Archive / REST Forks API |
| **Commit Velocity** | Count commits in window $[t_k - 30\text{d}, t_k]$ | REST Commits API (`until=t_k`) |
| **Issue Resolution**| Ratio of issues closed $\le t_k$ to created $\le t_k$ | REST Issues API (`state=all`) |

## 3. Dataset Sampling Scale

- **Target Repositories**: 10,000 top starred & active open-source GitHub repositories across 15 programming languages.
- **Snapshot Frequency**: Monthly sampling ($\Delta t = 30\text{ days}$) across a 3-year historical window (2022–2025).
- **Total Training Examples**: $10,000 \times 24 = 240,000$ snapshot feature-label pairs $(X_{t_k}, Y_{t_k}^H)$.
