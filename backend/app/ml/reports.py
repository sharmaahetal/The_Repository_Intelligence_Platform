import json
import os
from typing import Any

from backend.app.logging import logger


class EvaluationReportGenerator:
    """Generates comprehensive HTML evaluation report dashboards and JSON metric artifacts."""

    def generate_report(
        self,
        output_dir: str,
        metrics: dict[str, Any],
        shap_summary: dict[str, float] | None = None,
        model_name: str = "rip-growth",
    ) -> dict[str, str]:
        """Writes evaluation report artifacts (report.html, metrics.json, feature_importance.json) to output_dir.

        Returns dictionary of artifact names to file paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        metrics_path = os.path.join(output_dir, "metrics.json")
        report_html_path = os.path.join(output_dir, "report.html")
        importance_path = os.path.join(output_dir, "feature_importance.json")

        # 1. Write metrics.json
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        # 2. Write feature_importance.json
        feature_importance = shap_summary or {}
        with open(importance_path, "w", encoding="utf-8") as f:
            json.dump(feature_importance, f, indent=2)

        # 3. Generate report.html
        html_content = self._render_html_report(
            model_name=model_name,
            metrics=metrics,
            feature_importance=feature_importance,
        )
        with open(report_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(
            "Generated evaluation report artifacts",
            extra={"output_dir": output_dir, "metrics_count": len(metrics)},
        )

        return {
            "metrics_json": metrics_path,
            "report_html": report_html_path,
            "feature_importance_json": importance_path,
        }

    def _render_html_report(
        self,
        model_name: str,
        metrics: dict[str, Any],
        feature_importance: dict[str, float],
    ) -> str:
        metrics_rows = ""
        for k, v in metrics.items():
            val_str = f"{v:.4f}" if isinstance(v, float | int) else str(v)
            metrics_rows += f"<tr><td><strong>{k}</strong></td><td>{val_str}</td></tr>"

        importance_rows = "".join(
            f"<tr><td>{k}</td><td>{v:.4f}</td></tr>" for k, v in feature_importance.items()
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Evaluation Report - {model_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 30px; background-color: #f8fafc; color: #0f172a; }}
        h1 {{ color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background-color: #f1f5f9; }}
    </style>
</head>
<body>
    <h1>ML Model Evaluation Report: {model_name}</h1>
    <div class="card">
        <h2>Performance Metrics</h2>
        <table>
            <thead><tr><th>Metric</th><th>Score</th></tr></thead>
            <tbody>{metrics_rows}</tbody>
        </table>
    </div>
    <div class="card">
        <h2>SHAP Feature Importances</h2>
        <table>
            <thead><tr><th>Feature</th><th>Importance Score</th></tr></thead>
            <tbody>{importance_rows if importance_rows else '<tr><td colspan="2">No feature importances recorded</td></tr>'}</tbody>
        </table>
    </div>
</body>
</html>"""
