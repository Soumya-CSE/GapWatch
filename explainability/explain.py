"""
Generates human-readable rationale for why an entity was flagged, using
the z-scores computed in the analytics pipeline (a lightweight, fully
transparent alternative to SHAP for the prototype — swap in real SHAP
values once a supervised model is trained on labeled outcomes).
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).parent.parent / "data" / "sat_sa.db"

FEATURE_LABELS = {
    "z_avg_closure_minutes": "average alert closure time",
    "z_median_closure_minutes": "median alert closure time",
    "z_escalation_rate_critical": "escalation rate for critical alerts",
    "z_escalation_rate_high": "escalation rate for high-severity alerts",
    "z_avg_investigation_notes_length": "depth of investigation notes",
}


def explain_entity(row: pd.Series, top_n: int = 3) -> list[str]:
    """
    Returns the top contributing factors for a flagged entity, in plain
    language, ranked by how far each feature deviates from the peer
    average (|z-score|).
    """
    z_cols = [c for c in row.index if c.startswith("z_")]
    deviations = row[z_cols].astype(float).abs().sort_values(ascending=False)

    explanations = []
    for col in deviations.index[:top_n]:
        z = row[col]
        label = FEATURE_LABELS.get(col, col)
        direction = "unusually low" if z < 0 else "unusually high"
        explanations.append(f"{label} is {direction} vs. peer entities (z={z:.2f})")
    return explanations


def main():
    conn = sqlite3.connect(DB_PATH)
    scores = pd.read_sql("SELECT * FROM entity_risk_scores", conn)
    conn.close()

    flagged = scores[scores["flagged"].astype(bool)]

    print("Supervisory findings:\n")
    for _, row in flagged.iterrows():
        print(f"== {row['cse']} (anomaly score: {row['anomaly_score']:.2f}) ==")
        for reason in explain_entity(row):
            print(f"  - {reason}")
        print()


if __name__ == "__main__":
    main()
