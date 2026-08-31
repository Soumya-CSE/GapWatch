"""
SAT-SA dashboard — Streamlit app for supervisors.
Runs fully locally: `streamlit run dashboard/app.py`
No internet access required once dependencies are installed.
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).parent.parent))
from explainability.explain import explain_entity

DB_PATH = Path(__file__).parent.parent / "data" / "sat_sa.db"

st.set_page_config(page_title="SAT-SA — Supervisory Analytics", layout="wide")
st.title("Supervisory Analytics Tool for SOC Assessment")
st.caption("Prototype — runs fully offline, no cloud dependency")


@st.cache_data
def load_scores():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM entity_risk_scores", conn)
    conn.close()
    return df


try:
    scores = load_scores()
except Exception:
    st.error(
        "No data found. Run `python ingestion/load_data.py` then "
        "`python analytics/pipeline.py` first."
    )
    st.stop()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Entity risk ranking")
    fig = px.bar(
        scores.sort_values("anomaly_score"),
        x="anomaly_score",
        y="cse",
        color="flagged",
        orientation="h",
        labels={"anomaly_score": "Anomaly score", "cse": "Entity", "flagged": "Flagged"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Entities flagged for review")
    st.dataframe(
        scores[scores["flagged"].astype(bool)][["cse", "anomaly_score"]].sort_values(
            "anomaly_score", ascending=False
        ),
        hide_index=True,
        use_container_width=True,
    )

st.divider()
st.subheader("Drill-down: why was an entity flagged?")

selected = st.selectbox("Select entity", scores["cse"].tolist())
row = scores[scores["cse"] == selected].iloc[0]

st.metric("Anomaly score", f"{row['anomaly_score']:.2f}")
st.write("**Contributing factors:**")
for reason in explain_entity(row):
    st.write(f"- {reason}")

with st.expander("Raw underlying metrics"):
    st.json(row.to_dict())
