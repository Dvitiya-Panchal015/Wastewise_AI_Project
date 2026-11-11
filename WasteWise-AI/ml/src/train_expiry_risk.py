
from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "inventory_batches.csv"
)

MODEL_DIR = PROJECT_ROOT / "models"
ARTIFACT_DIR = PROJECT_ROOT / "artifacts"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    # --------------------------------------------------
    # 2. Load dataset
    # --------------------------------------------------
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    target = "expiry_risk_label"

    required_columns = [
        "category",
        "initial_quantity",
        "quantity_remaining",
        "days_to_expiry",
        "avg_daily_sales_7d",
        "expected_demand_before_expiry",
        "unit_price",
        "unit_cost",
        "discount_pct",
        target,
        "waste_units_actual_simulated",
    ]

    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns are missing: {missing_columns}"
        )

    # --------------------------------------------------
    # 3. Validate target and inspect label relationship
    # --------------------------------------------------
    df = df.dropna(subset=[target]).copy()

    if not set(df[target].unique()).issubset({0, 1}):
        raise ValueError("Expiry-risk target must contain only 0 and 1.")

    label_matches_waste = (
        (df[target] == 1)
        == (df["waste_units_actual_simulated"] > 0)
    )

    print("\nTARGET VALIDATION")
    print("-----------------")
    print("Dataset shape:", df.shape)
    print("Label counts:")
    print(df[target].value_counts().sort_index().to_string())
    print(
        "Label exactly matches simulated waste:",
        bool(label_matches_waste.all()),
    )

    # --------------------------------------------------
    # 4. Select model inputs
    # Do not include IDs, dates, target, or simulated waste.
    # --------------------------------------------------
    feature_columns = [
        "category",
        "initial_quantity",
        "quantity_remaining",
        "days_to_expiry",
        "avg_daily_sales_7d",
        "expected_demand_before_expiry",
        "unit_price",
        "unit_cost",
        "discount_pct",
    ]

    X = df[feature_columns].copy()
    y = df[target].astype(int)

    categorical_features = ["category"]
    numeric_features = [
        col for col in feature_columns
        if col not in categorical_features
    ]

    # --------------------------------------------------
    # 5. Preprocessing
    # --------------------------------------------------
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore"),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            (
                "categorical",
                categorical_pipeline,
                categorical_features,
            ),
        ]
    )

    # --------------------------------------------------
    # 6. Build model pipeline
    # --------------------------------------------------
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=200,
                    random_state=42,
                    class_weight="balanced",
                    n_jobs=-1,
                ),
            ),
        ]
    )

    # --------------------------------------------------
    # 7. Split data
    # --------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print("\nDATA SPLIT")
    print("----------")
    print("Training records:", len(X_train))
    print("Testing records:", len(X_test))

    # --------------------------------------------------
    # 8. Train model
    # --------------------------------------------------
    model.fit(X_train, y_train)

    # --------------------------------------------------
    # 9. Evaluate model
    # --------------------------------------------------
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(
            precision_score(y_test, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(y_test, predictions, zero_division=0)
        ),
        "f1_score": float(
            f1_score(y_test, predictions, zero_division=0)
        ),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "training_records": int(len(X_train)),
        "testing_records": int(len(X_test)),
        "features": feature_columns,
        "target": target,
        "label_is_simulated": True,
        "label_matches_simulated_waste_exactly": bool(
            label_matches_waste.all()
        ),
    }

    print("\nEVALUATION METRICS")
    print("------------------")
    for name, value in metrics.items():
        print(f"{name}: {value}")

    print("\nCONFUSION MATRIX")
    print("----------------")
    print(confusion_matrix(y_test, predictions))

    print("\nCLASSIFICATION REPORT")
    print("---------------------")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    # --------------------------------------------------
    # 10. Save model and metrics
    # --------------------------------------------------
    model_path = MODEL_DIR / "expiry_risk_model.joblib"
    metrics_path = ARTIFACT_DIR / "expiry_risk_metrics.json"

    joblib.dump(model, model_path)

    with open(metrics_path, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)

    print("\nSAVED FILES")
    print("-----------")
    print("Model:", model_path)
    print("Metrics:", metrics_path)


if __name__ == "__main__":
    main()
