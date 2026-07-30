# Feature Dictionary

## Overview
This document records every engineered feature computed by the Feature Store Engine (`backend/app/features/`), including feature names, categories, formulas, and hypotheses on why they influence repository forecasting.

---

## Feature Catalog

| Feature Name | Category | Data Type | Formula / Description | Hypothesis |
| :--- | :--- | :--- | :--- | :--- |
| `commit_velocity_30d` | Temporal Velocity | Float | Count of maintainer commits in $[t_0 - 30\text{d}, t_0] / 30$ | High recent velocity correlates with active development momentum. |
| `commit_acceleration` | Temporal Momentum | Float | $\frac{\text{commit\_velocity\_30d}}{\max(1, \text{commit\_velocity\_90d})}$ | Ratio $> 1.0$ indicates accelerating developer engagement. |
| `star_velocity_90d` | Growth Velocity | Float | Star count delta in $[t_0 - 90\text{d}, t_0] / 90$ | Measures organic user adoption speed. |
| `contributor_retention_rate` | Community | Float | $\frac{|\mathcal{C}_{90\text{d}} \cap \mathcal{C}_{180\text{d}}|}{|\mathcal{C}_{180\text{d}}|}$ | High contributor retention protects against maintainer abandonment. |
| `pr_merge_time_p50` | Maintainability | Float | Median hours from PR creation to merge in $[t_0 - 90\text{d}, t_0]$ | Fast PR merges signal welcoming maintainer governance. |
| `issue_resolution_velocity` | Maintainability | Float | Resolved issues / Created issues in $[t_0 - 90\text{d}, t_0]$ | Ratios $< 0.5$ signal unmanaged issue backlogs. |
| `release_cadence_days` | Governance | Float | Mean days between tagged releases over $[t_0 - 365\text{d}, t_0]$ | Regular release cadence indicates software release maturity. |
| `star_density_index` | Density | Float | $\frac{\text{stars\_count}}{\max(1.0, \text{size\_mb})}$ | High star density per MB indicates code value efficiency. |
| `fork_to_star_ratio` | Engagement | Float | $\frac{\text{forks\_count}}{\max(1, \text{stars\_count})}$ | High fork-to-star ratio signals active developer usage over passive bookmarking. |
| `open_issue_density` | Maintenance Burden | Float | $\frac{\text{open\_issues\_count}}{\max(1, \text{stars\_count})}$ | High issue density relative to stars signals maintenance debt. |
| `subscriber_engagement_ratio` | Watchers | Float | $\frac{\text{subscribers\_count}}{\max(1, \text{stars\_count})}$ | High watcher ratio reflects deep developer community interest. |

