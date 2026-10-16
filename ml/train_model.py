"""Train a demo Random Forest from a labelled CSV.

Expected columns:
amount, merchant, location, channel, is_fraud
is_fraud must contain 0/1 labels. Use a sufficiently large, representative,
authorized dataset; the bundled sample is only for interface testing.
"""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data" / "labelled_transactions.csv"
OUT = BASE / "models" / "fraud_model.joblib"

def main():
    if not DATA.exists():
        raise SystemExit(f"Create {DATA} with labelled transaction data first.")
    df = pd.read_csv(DATA)
    required = {"amount", "merchant", "location", "channel", "is_fraud"}
    if not required.issubset(df.columns):
        raise SystemExit(f"Required columns: {sorted(required)}")
    if df["is_fraud"].nunique() < 2:
        raise SystemExit("Training data must contain both fraud (1) and legitimate (0) labels.")
    X = df[["amount", "merchant", "location", "channel"]]
    y = df["is_fraud"].astype(int)
    numeric = ["amount"]
    categorical = ["merchant", "location", "channel"]
    prep = ColumnTransformer([
        ("numeric", StandardScaler(), numeric),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical)
    ])
    model = Pipeline([
        ("preprocess", prep),
        ("classifier", RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=42))
    ])
    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=stratify)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    print(classification_report(y_test, preds, zero_division=0))
    print("Confusion matrix:\n", confusion_matrix(y_test, preds))
    OUT.parent.mkdir(exist_ok=True)
    joblib.dump(model, OUT)
    print("Saved model:", OUT)

if __name__ == "__main__":
    main()
