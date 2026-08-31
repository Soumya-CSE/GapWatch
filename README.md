# SAT-SA — Supervisory Analytics Tool for SOC Assessment
Analyzes SOC alert and case-management
data across multiple Critical Sector Entities (CSEs) to flag execution gaps
and negative space for supervisory review — fully offline, no cloud, no
external API dependency.

## Project layout

```
sat-sa/
├── ingestion/        # load & validate CSE alert/case data (CSV/JSON)
├── analytics/         # anomaly detection, peer benchmarking, gap scoring
├── explainability/     # SHAP-based rationale generation
├── dashboard/         # Streamlit app tying it all together
├── sample_data/        # synthetic sample alert/case data for demo
└── data/              # local SQLite DB (created at runtime)
```

## Setup (offline-capable after first install)

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt   # do this once, with internet
```

## Run the prototype

```bash
# 1. Load sample data into local SQLite db
python ingestion/load_data.py

# 2. Run the analytics + scoring pipeline
python analytics/pipeline.py

# 3. Launch the dashboard (fully local, opens in browser)
streamlit run dashboard/app.py
```

Once dependencies and model files are installed, this runs with zero
internet access — disable your network connection before the demo to prove
the "air-gapped" requirement.

## What's implemented so far (prototype scope)

- Synthetic sample data for 5 CSEs across alerts + case-management records
- Isolation Forest anomaly detection on closure-time / escalation patterns
- Peer benchmarking (z-scores against other CSEs)
- SHAP-based explanations for every flagged entity/case
- Streamlit dashboard: entity risk ranking, drill-down to evidence

## Not yet implemented (next steps)

- Real CSE data connectors (API ingestion beyond CSV/JSON)
- "Negative space" detection (missing telemetry / absent alert categories)
- Multi-entity trend analysis over time
- Local LLM-generated narrative summaries (optional, via Ollama)
