"""
Generates synthetic SOC alert + case-management data for 5 fictional CSEs,
so the pipeline can be demoed without real/sensitive data.

Run: python sample_data/generate_sample_data.py
Produces: sample_data/alerts.csv, sample_data/cases.csv
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

CSES = ["CSE_Power_A", "CSE_Bank_B", "CSE_Telecom_C", "CSE_Transport_D", "CSE_Bank_E"]
SEVERITIES = ["Low", "Medium", "High", "Critical"]

# CSE_Bank_E is deliberately "problematic" — fast closures, low escalation
PROBLEM_ENTITY = "CSE_Bank_E"


def generate_alerts(n_per_entity=200):
    rows = []
    alert_id = 1
    start = datetime(2026, 1, 1)

    for cse in CSES:
        is_problem = cse == PROBLEM_ENTITY
        for _ in range(n_per_entity):
            created = start + timedelta(
                days=random.randint(0, 240), hours=random.randint(0, 23)
            )
            severity = random.choices(SEVERITIES, weights=[40, 30, 20, 10])[0]

            if is_problem:
                # unusually fast closure, low escalation on critical alerts
                closure_minutes = random.randint(2, 15)
                escalated = severity == "Critical" and random.random() < 0.15
            else:
                closure_minutes = random.randint(30, 600)
                escalated = severity in ("Critical", "High") and random.random() < 0.75

            rows.append(
                {
                    "alert_id": alert_id,
                    "cse": cse,
                    "created_at": created.isoformat(),
                    "severity": severity,
                    "closure_minutes": closure_minutes,
                    "escalated": escalated,
                    "asset": f"asset_{random.randint(1, 30)}",
                }
            )
            alert_id += 1
    return rows


def generate_cases(alerts):
    rows = []
    case_id = 1
    for alert in alerts:
        if random.random() < 0.6:  # not every alert becomes a case
            is_problem = alert["cse"] == PROBLEM_ENTITY
            investigation_notes_len = (
                random.randint(10, 40) if is_problem else random.randint(80, 400)
            )
            rows.append(
                {
                    "case_id": case_id,
                    "alert_id": alert["alert_id"],
                    "cse": alert["cse"],
                    "investigation_notes_length": investigation_notes_len,
                    "status": random.choice(["Closed", "Closed", "Open"]),
                }
            )
            case_id += 1
    return rows


if __name__ == "__main__":
    alerts = generate_alerts()
    cases = generate_cases(alerts)

    with open("sample_data/alerts.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=alerts[0].keys())
        writer.writeheader()
        writer.writerows(alerts)

    with open("sample_data/cases.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cases[0].keys())
        writer.writeheader()
        writer.writerows(cases)

    print(f"Generated {len(alerts)} alerts and {len(cases)} cases across {len(CSES)} CSEs.")
