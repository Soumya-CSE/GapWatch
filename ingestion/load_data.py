"""
Ingests alert/case CSVs into a local SQLite database.
No network calls — reads from disk, writes to disk.
"""

import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "sat_sa.db"
SAMPLE_DIR = Path(__file__).parent.parent / "sample_data"


def load_csv_to_db(csv_path: Path, table_name: str, conn: sqlite3.Connection):
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into '{table_name}'")
    return df


def validate_schema(df: pd.DataFrame, required_cols: list, table_name: str):
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"'{table_name}' is missing required columns: {missing}")


def main():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    alerts_csv = SAMPLE_DIR / "alerts.csv"
    cases_csv = SAMPLE_DIR / "cases.csv"

    if not alerts_csv.exists():
        raise FileNotFoundError(
            "Sample data not found. Run: python sample_data/generate_sample_data.py"
        )

    alerts_df = load_csv_to_db(alerts_csv, "alerts", conn)
    cases_df = load_csv_to_db(cases_csv, "cases", conn)

    validate_schema(
        alerts_df, ["alert_id", "cse", "severity", "closure_minutes", "escalated"], "alerts"
    )
    validate_schema(cases_df, ["case_id", "alert_id", "cse", "status"], "cases")

    conn.close()
    print(f"Ingestion complete. Database at {DB_PATH}")


if __name__ == "__main__":
    main()
