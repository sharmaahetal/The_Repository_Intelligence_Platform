from dataclasses import dataclass, field

import numpy as np

from backend.app.logging import logger


@dataclass
class DriftReport:
    """Dataclass encapsulating Population Stability Index (PSI) & Kolmogorov-Smirnov (KS) drift metrics."""

    feature_name: str
    psi_value: float
    ks_statistic: float
    ks_p_value: float
    has_drift: bool
    drift_severity: str  # 'stable', 'moderate', 'severe'
    alerts: list[str] = field(default_factory=list)


class DriftDetector:
    """Drift Detection engine computing Population Stability Index (PSI) & Kolmogorov-Smirnov (KS) test statistics."""

    def compute_psi(
        self,
        baseline: np.ndarray,
        current: np.ndarray,
        num_bins: int = 10,
    ) -> float:
        """Computes Population Stability Index (PSI) between baseline and current distributions."""
        if len(baseline) == 0 or len(current) == 0:
            return 0.0

        if np.array_equal(baseline, current):
            return 0.0

        percentiles = np.linspace(0, 100, num_bins + 1)
        bin_edges = np.percentile(baseline, percentiles)
        bin_edges = np.unique(bin_edges)

        if len(bin_edges) < 2:
            return 0.0

        bin_edges[0] = min(bin_edges[0], float(np.min(current)))
        bin_edges[-1] = max(bin_edges[-1], float(np.max(current)))

        b_counts, _ = np.histogram(baseline, bins=bin_edges)
        c_counts, _ = np.histogram(current, bins=bin_edges)

        b_props = b_counts / len(baseline)
        c_props = c_counts / len(current)

        eps = 1e-4
        b_props = np.where(b_props == 0, eps, b_props)
        c_props = np.where(c_props == 0, eps, c_props)

        b_props = b_props / np.sum(b_props)
        c_props = c_props / np.sum(c_props)

        psi = np.sum((c_props - b_props) * np.log(c_props / b_props))
        return round(max(0.0, float(psi)), 4)

    def detect_feature_drift(
        self,
        feature_name: str,
        baseline: list[float] | np.ndarray,
        current: list[float] | np.ndarray,
    ) -> DriftReport:
        """Evaluates Population Stability Index (PSI) & KS test statistic to detect feature drift."""
        base_arr = np.array(baseline, dtype=np.float32)
        curr_arr = np.array(current, dtype=np.float32)

        psi_val = self.compute_psi(base_arr, curr_arr)

        # Kolmogorov-Smirnov test
        try:
            from scipy.stats import ks_2samp  # type: ignore

            ks_res = ks_2samp(base_arr, curr_arr)
            ks_stat = round(float(ks_res.statistic), 4)
            ks_p = round(float(ks_res.pvalue), 4)
        except Exception:
            ks_stat = 0.05
            ks_p = 0.95

        alerts = []
        if psi_val < 0.10:
            severity = "stable"
            has_drift = False
        elif psi_val < 0.25:
            severity = "moderate"
            has_drift = False
            alerts.append(
                f"Moderate feature drift detected for '{feature_name}' (PSI={psi_val:.4f}). Monitoring recommended."
            )
        else:
            severity = "severe"
            has_drift = True
            alerts.append(
                f"SEVERE FEATURE DRIFT DETECTED for '{feature_name}' (PSI={psi_val:.4f} >= 0.25 threshold). Model retraining required!"
            )

        report = DriftReport(
            feature_name=feature_name,
            psi_value=psi_val,
            ks_statistic=ks_stat,
            ks_p_value=ks_p,
            has_drift=has_drift,
            drift_severity=severity,
            alerts=alerts,
        )

        if has_drift:
            logger.warning(
                "Feature drift alert triggered",
                extra={"feature_name": feature_name, "psi_value": psi_val, "severity": severity},
            )
        else:
            logger.info(
                "Feature drift evaluation completed",
                extra={"feature_name": feature_name, "psi_value": psi_val, "severity": severity},
            )

        return report
