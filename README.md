# 🛰️ GapWatch — Supervisory Analytics Tool for SOC Assessment

**GapWatch** is a fully offline, privacy-focused supervisory analytics tool designed to evaluate Security Operations Center (SOC) alert and case-management performance across multiple Critical Sector Entities (CSEs).

By ingesting local alert logs and incident response records, GapWatch identifies execution gaps, operational anomalies, and "negative space" (unreported or suppressed telemetry) across monitored entities without relying on external cloud services or third-party APIs.

---

## ✨ Key Features

- **🔒 100% Offline & Air-Gapped Operation:** Runs entirely locally using Python, SQLite, and Streamlit. Zero outbound network calls.
- **🚨 Anomaly Detection:** Leverages Unsupervised Machine Learning (`IsolationForest`) to identify suspicious resolution times, irregular escalation paths, and anomalous case-handling behaviors.
- **📊 Peer Benchmarking:** Computes comparative statistical metrics (Z-scores, percentile ranks) across CSEs operating within similar risk profiles or sectors.
- **🧠 Explainable AI (XAI):** Integrated SHAP (SHapley Additive exPlanations) values to provide auditable, feature-level rationale for every flag raised by the system.
- **🖥️ Interactive Supervisory Dashboard:** Intuitive drill-down capabilities from macro entity-risk scores down to individual case evidence logs.

---

## 🖼️ Screenshots & Interface


---

## 🏗️ System Architecture & Data Flow

```
                              +-----------------------+
                              | CSV / JSON Telemetry  |
                              +-----------+-----------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| GapWatch Local Engine (Offline Boundary)                                          |
|                                                                                   |
|  +--------------------+      +--------------------+      +--------------------+   |
|  | Ingestion & Schema | ---> | Local SQLite DB    | ---> | Analytics & Scorer |   |
|  | Validation         |      | (sat_sa.db)        |      | Engine             |   |
|  +--------------------+      +--------------------+      +---------+----------+   |
|                                                                    |              |
|                                                                    v              |
|  +--------------------+      +--------------------+      +--------------------+   |
|  | Streamlit          | <--- | SHAP Rationale     | <--- | Isolation Forest   |   |
|  | Supervisory UI     |      | Generator          |      | & Z-Score Models   |   |
|  +--------------------+      +--------------------+      +--------------------+   |
+-----------------------------------------------------------------------------------+

```

---

## 📁 Project Structure


```

gapwatch/
├── analytics/               # Analytics pipeline & scoring algorithms
│   └── pipeline.py          # Master analytical execution & anomaly pipeline
├── dashboard/               # Streamlit supervisory UI app
│   └── app.py               # Main dashboard web application interface
├── data/                    # Storage directory for local SQLite runtime database
│   └── sat_sa.db            # SQLite database file storing alerts & cases
├── explainability/          # Explainable AI scripts
│   └── explain.py           # SHAP-based feature rationale and explanations
├── ingestion/               # Data ingestion module
│   └── load_data.py         # Loads CSV datasets into SQLite database
├── sample_data/             # Synthetic demo datasets & generator script
│   ├── alerts.csv           # Synthetic alert telemetry across CSEs
│   ├── cases.csv            # Synthetic case-management logs
│   └── generate_sample_data.py # Data generator script for testing
├── .gitignore               # Git ignore pattern rules
├── README.md                # Project documentation
├── requirements.txt         # Offline dependencies manifest

```

---

## ⚙️ How It Works (Working Principle)

GapWatch operates on a strict **linear dependency chain**. Data flows step-by-step through four isolated stages, moving from raw logs to an interactive supervisory interface:

1. **📥 Ingestion (`ingestion/load_data.py`):** Reads raw offline telemetry (`alerts.csv`, `cases.csv`), validates schema integrity, and persists records into `data/sat_sa.db`.
2. **📈 Analytics (`analytics/pipeline.py`):** Calculates key behavioral features (turnaround time, closure ratios), fits an `IsolationForest` model to flag operational anomalies, and computes cross-CSE Z-scores.
3. **🧩 Explainability (`explainability/explain.py`):** Applies SHAP values to compute explicit feature attributions for every flagged anomaly (e.g., "+35 points due to prolonged acknowledgment lag").
4. **🖥️ Presentation (`dashboard/app.py`):** Queries `sat_sa.db` via Streamlit to render sortable risk tables, Plotly visualizations, and auditable case evidence views.

---

## 🗂️ Data Schema Overview

GapWatch expects two primary inputs: **Alert Telemetry** and **Case Management Logs**.

### 1. Alert Records (`sample_data/alerts.csv`)
| Field | Type | Description |
| :--- | :--- | :--- |
| `alert_id` | String (UUID) | Unique identifier for the alert |
| `cse_id` | String | Identifier for the Critical Sector Entity (e.g., `CSE-01`) |
| `timestamp` | Datetime (ISO) | Detection timestamp |
| `category` | String | Threat classification (e.g., `Phishing`, `Ransomware`, `Auth failure`) |
| `severity` | String | Severity rating (`Low`, `Medium`, `High`, `Critical`) |
| `status` | String | Final alert status (`Escalated`, `Closed-FP`, `Closed-TP`, `Ignored`) |

### 2. Case Management Records (`sample_data/cases.csv`)
| Field | Type | Description |
| :--- | :--- | :--- |
| `case_id` | String (UUID) | Unique incident case identifier |
| `cse_id` | String | Identifier for the Critical Sector Entity |
| `created_at` | Datetime (ISO) | Case opening timestamp |
| `closed_at` | Datetime (ISO) | Case resolution/closing timestamp |
| `time_to_acknowledge_min` | Float | Minutes from creation to first analyst action |
| `time_to_resolve_min` | Float | Minutes from creation to case closure |
| `analyst_id` | String | Identifier for assigned SOC operator |
| `escalation_level` | Integer | Max escalation tier reached (1–4) |
| `false_positive_flag` | Boolean | True if case was marked as false positive |

---

## 🧮 Analytics & Scoring Methodology

GapWatch processes data through three key analytical filters:

1. **🌲 Isolation Forest Anomaly Scoring ($S_{anomaly}$):**
   - Fits an unsupervised decision forest on operational metrics (e.g., `time_to_acknowledge_min`, `time_to_resolve_min`, closure ratios).
   - Isolates cases exhibiting extreme turnaround times or abnormal analyst routing behavior.

2. **📉 Peer Benchmarking Z-Score ($Z_{peer}$):**
   - Calculates mean ($\mu$) and standard deviation ($\sigma$) for key performance indicators across similar CSEs:
     $$Z = \frac{X - \mu}{\sigma}$$
   - Identifies entities deviating significantly from sector-wide operational norms.

3. **🧭 Combined Execution Gap Index (EGI):**
   - Aggregates individual metrics into a normalized composite risk score ($0.0 - 100.0$):
     $$\text{EGI} = w_1 \cdot S_{anomaly} + w_2 \cdot Z_{peer} + w_3 \cdot R_{unreported}$$
   - High EGI indicates elevated operational friction, potential under-reporting, or compromised incident response.

---

## 🚀 Setup & Execution Guide

> **Note:** Initial environment creation and dependency download require internet access. Once installed, the application operates completely offline.

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

```

### 2. Run the Pipeline & Launch UI

Run the steps in sequential order:

```bash
# Step 0: (Optional) Regenerate synthetic test datasets
python sample_data/generate_sample_data.py

# Step 1: Load sample data into local SQLite database (data/sat_sa.db)
python ingestion/load_data.py

# Step 2: Run analytics pipeline & SHAP scoring
python analytics/pipeline.py

# Step 3: Launch interactive dashboard (fully local)
streamlit run dashboard/app.py

```

The application will launch locally at `http://localhost:8501`.

---

## 🗺️ Roadmap & Next Steps

* [ ] **🔌 Data Connectors:** Extend ingestion beyond CSV/JSON to support offline database dumps (PostgreSQL, ElasticDump).
* [ ] **🕳️ "Negative Space" Detection:** Implement statistical algorithms to detect missing telemetry categories or unexpected periods of zero alerts.
* [ ] **📆 Multi-Entity Temporal Trend Analysis:** Track changes in CSE risk scores over trailing quarters and fiscal periods.
* [ ] **🤖 Local LLM Summary Generation:** Integrate offline local LLMs via [Ollama](https://ollama.ai/) to automatically write executive summaries and supervisory notes.
* [ ] **📄 Report Export:** Export full supervisory audit reports as standalone PDFs.

---

---

## 👨‍💻 Author

### Soumya Kanti Hazra

Computer Science & Engineering Student

Aspiring SOC Analyst | Cybersecurity Enthusiast

**GitHub:**
[https://github.com/Soumya-CSE](https://github.com/Soumya-CSE)

**LinkedIn:**
[https://www.linkedin.com/in/soumya-kanti-hazra-b20162374](https://www.linkedin.com/in/soumya-kanti-hazra-b20162374)

**TryHackMe:**
[https://tryhackme.com/p/soumyahazra](https://tryhackme.com/p/soumyahazra)

---

## 📜 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for more information.

---

## ⭐ Support & Appreciation

If you found **GapWatch** useful for learning **Cybersecurity Operations, Unsupervised Machine Learning, Explainable AI (XAI), or Streamlit Dashboard Development**, consider giving this repository a ⭐ on GitHub!

Your support helps highlight the importance of open, air-gapped supervisory analytics tools for critical infrastructure protection.
If you found this project useful for learning **Cybersecurity, Cryptography, Python, or Flask**, consider giving the repository a ⭐ on GitHub.
