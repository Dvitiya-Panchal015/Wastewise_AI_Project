
from pathlib import Path
import json

import pandas as pd


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = PROJECT_ROOT / "artifacts"


def load_metrics(filename):
    """Load a model's saved evaluation metrics."""
    path = ARTIFACT_DIR / filename

    if not path.exists():
        print(f"WARNING: Metrics file not found: {path}")
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    # --------------------------------------------------
    # 2. Load both model reports
    # --------------------------------------------------
    expiry_metrics = load_metrics("expiry_risk_metrics.json")
    forecast_metrics = load_metrics("demand_forecast_metrics.json")

    reports = []

    if expiry_metrics:
        reports.append(
            {
                "Model": "Expiry Risk Classification",
                "Metric": "Accuracy",
                "Value": expiry_metrics.get("accuracy"),
                "Additional Metrics": (
                    f"Precision={expiry_metrics.get('precision')}, "
                    f"Recall={expiry_metrics.get('recall')}, "
                    f"F1={expiry_metrics.get('f1_score')}, "
                    f"ROC-AUC={expiry_metrics.get('roc_auc')}"
                ),
                "Data Note": (
                    "Simulated label; exactly matches simulated waste"
                    if expiry_metrics.get(
                        "label_matches_simulated_waste_exactly"
                    )
                    else "Review target definition"
                ),
            }
        )

    if forecast_metrics:
        reports.append(
            {
                "Model": "Demand Forecasting",
                "Metric": "MAE (lower is better)",
                "Value": forecast_metrics.get("mae"),
                "Additional Metrics": (
                    f"RMSE={forecast_metrics.get('rmse')}, "
                    f"R2={forecast_metrics.get('r2')}, "
                    f"Baseline MAE={forecast_metrics.get('baseline_mae')}, "
                    f"Baseline RMSE={forecast_metrics.get('baseline_rmse')}"
                ),
                "Data Note": "Historical simulated sales; initial evaluation",
            }
        )

    # --------------------------------------------------
    # 3. Display and save combined report
    # --------------------------------------------------
    if not reports:
        print("No metrics files found. Train the models first.")
        return

    report = pd.DataFrame(reports)

    print("\nWASTEWISE AI - MODEL EVALUATION SUMMARY")
    print("=" * 45)
    print(report.to_string(index=False))

    output_path = ARTIFACT_DIR / "model_evaluation_summary.csv"
    report.to_csv(output_path, index=False)

    print("\nCombined report saved to:")
    print(output_path)


if __name__ == "__main__":
    main()
