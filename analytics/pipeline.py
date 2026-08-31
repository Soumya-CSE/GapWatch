"""
Core analytics engine: detects execution gaps (fast closures, low
escalation, thin investigations) per entity, benchmarks entities against
each other, and produces a per-entity risk score with contributing
features for the explainability layer.

Runs fully offline — scikit-learn only, no network calls.
"""

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

DB_PATH = Path(__file__).parent.parent / "data" / "sat_sa.db"


def load_data(conn):
    alerts = pd.read_sql("SELECT * FROM alerts", conn)
    cases = pd.read_sql("SELECT * FROM cases", conn)
    return alerts, cases


def build_entity_features(alerts: pd.DataFrame, cases: pd.DataFrame) -> pd.DataFrame:
    """Aggregate alert/case data into one feature row per CSE."""
    g = alerts.groupby("cse")

    features = pd.DataFrame(
        {
            "avg_closure_minutes": g["closure_minutes"].mean(),
            "median_closure_minutes": g["closure_minutes"].median(),
            "pct_critical": g.apply(lambda x: (x["severity"] == "Critical").mean()),
            "escalation_rate_critical": g.apply(
                lambda x: x.loc[x["severity"] == "Critical", "escalated"].mean()
                if (x["severity"] == "Critical").any()
                else 0
            ),
            "escalation_rate_high": g.apply(
                lambda x: x.loc[x["severity"] == "High", "escalated"].mean()
                if (x["severity"] == "High").any()
                else 0
            ),
        }
    )

    case_notes = cases.groupby("cse")["investigation_notes_length"].mean()
    features["avg_investigation_notes_length"] = case_notes

    features = features.reset_index()
    return features


def score_entities(features: pd.DataFrame):
    """
    Isolation Forest flags entities whose overall pattern is anomalous
    relative to peers. Lower closure time, lower escalation, and shorter
    investigation notes push a CSE toward 'execution gap' territory.
    """
    feature_cols = [
        "avg_closure_minutes",
        "median_closure_minutes",
        "escalation_rate_critical",
        "escalation_rate_high",
        "avg_investigation_notes_length",
    ]

    X = features[feature_cols].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(contamination=0.2, random_state=42)
    model.fit(X_scaled)

    features["anomaly_score"] = -model.decision_function(X_scaled)  # higher = more anomalous
    features["flagged"] = model.predict(X_scaled) == -1

    # Peer benchmarking: z-score each feature so we can explain *why*
    z_scores = (X - X.mean()) / X.std().replace(0, 1)
    z_scores.columns = [f"z_{c}" for c in feature_cols]
    features = pd.concat([features, z_scores], axis=1)

    return features.sort_values("anomaly_score", ascending=False)


def main():
    conn = sqlite3.connect(DB_PATH)
    alerts, cases = load_data(conn)

    features = build_entity_features(alerts, cases)
    scored = score_entities(features)

    scored.to_sql("entity_risk_scores", conn, if_exists="replace", index=False)
    conn.close()

    print("\nEntity risk ranking (higher anomaly_score = more supervisory attention needed):\n")
    print(
        scored[
            ["cse", "anomaly_score", "flagged", "avg_closure_minutes", "escalation_rate_critical"]
        ].to_string(index=False)
    )
    print(f"\nSaved to entity_risk_scores table in {DB_PATH}")


if __name__ == "__main__":
    main()
