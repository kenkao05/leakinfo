import csv, json, re
from datetime import date
from collections import Counter, defaultdict

IN_PATH = "india_exam_leaks_master.csv"  # place the CSV at the project root
OUT_PATH = "src/data/leaks.json"

STATES = [
    "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat",
    "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh",
    "Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan",
    "Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal",
    "Delhi","Jammu & Kashmir","Ladakh","Puducherry","Chandigarh","Andaman & Nicobar Islands",
]
STATES_SORTED = sorted(STATES, key=len, reverse=True)

def extract_states(area_text):
    found = []
    remaining = area_text
    for s in STATES_SORTED:
        if s in remaining:
            found.append(s)
    if not found and "All India" in area_text:
        return ["All India"]
    return found or ["Unspecified"]

def bucket_action(token):
    t = token.strip()
    if not t:
        return None
    if t.startswith("Probe"):
        return "Investigation / probe"
    if t == "Arrests-FIR":
        return "Arrests / FIR"
    if t == "Exam cancelled":
        return "Exam cancelled"
    if t == "Retest":
        return "Retest / re-exam"
    if t == "Convictions":
        return "Convictions secured"
    if t == "None reported":
        return "No action reported"
    if t == "Not detailed in sources reviewed":
        return "Not detailed in sources"
    return t

with open(IN_PATH, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# ---- yearly counts, filled 2000-2026 ----
year_counts = {str(y): 0 for y in range(2000, 2027)}
for r in rows:
    y = r["date"][:4]
    if y in year_counts:
        year_counts[y] += 1

# ---- era / PM aggregation with years-in-office normalization ----
ERA_WINDOWS = [
    ("Atal Bihari Vajpayee", "NDA (BJP-led)", date(2000, 1, 1), date(2004, 5, 21)),
    ("Manmohan Singh", "UPA (INC-led)", date(2004, 5, 22), date(2014, 5, 25)),
    ("Narendra Modi", "NDA (BJP-led)", date(2014, 5, 26), date(2026, 7, 24)),
]
era_counts = Counter(r["pm_of_year_exact"] for r in rows)
era_data = []
for pm, party, start, end in ERA_WINDOWS:
    years_in_office = round((end - start).days / 365.25, 2)
    count = era_counts.get(pm, 0)
    era_data.append({
        "pm": pm,
        "party": party,
        "count": count,
        "years_in_office": years_in_office,
        "rate_per_year": round(count / years_in_office, 2) if years_in_office else 0,
    })

# ---- body type ----
body_type_counts = dict(Counter(r["body_type"] for r in rows))

# ---- leak status ----
leak_status_counts = dict(Counter(r["leak_status"] for r in rows))

# ---- action taken breakdown ----
action_counter = Counter()
for r in rows:
    for tok in r["action_taken"].split("+"):
        b = bucket_action(tok)
        if b:
            action_counter[b] += 1
action_data = sorted(
    [{"label": k, "count": v} for k, v in action_counter.items()],
    key=lambda x: -x["count"]
)

# ---- top states by incident count (multi-state incidents count once per state) ----
state_counter = Counter()
for r in rows:
    for s in extract_states(r["area"]):
        state_counter[s] += 1
top_states = sorted(
    [{"state": k, "count": v} for k, v in state_counter.items() if k not in ("All India", "Unspecified")],
    key=lambda x: -x["count"]
)[:12]

# ---- top exams by aspirants affected ----
exam_reach = []
for r in rows:
    v = r["aspirants_affected"].strip()
    if v.isdigit():
        exam_reach.append({
            "incident_id": r["incident_id"],
            "exam_name": r["exam_name"],
            "date": r["date"],
            "aspirants_affected": int(v),
        })
top_exams = sorted(exam_reach, key=lambda x: -x["aspirants_affected"])[:10]

# ---- KPI summary ----
total_incidents = len(rows)
confirmed_pct = round(100 * leak_status_counts.get("Confirmed", 0) / total_incidents)
total_arrests = sum(int(r["arrests"]) for r in rows if r["arrests"].strip().isdigit())
total_convictions = sum(int(r["convictions"]) for r in rows if r["convictions"].strip().isdigit())
distinct_states = len([s for s in state_counter if s not in ("All India", "Unspecified")])

kpis = {
    "total_incidents": total_incidents,
    "confirmed_pct": confirmed_pct,
    "total_arrests": total_arrests,
    "total_convictions": total_convictions,
    "distinct_states": distinct_states,
    "years_covered": "2000-2026",
}

# ---- raw rows for the searchable table (trimmed) ----
table_rows = []
for r in rows:
    table_rows.append({
        "id": r["incident_id"],
        "date": r["date"],
        "year": r["date"][:4],
        "exam_name": r["exam_name"],
        "conducting_body": r["conducting_body"],
        "body_type": r["body_type"],
        "area": r["area"],
        "pm": r["pm_of_year_exact"],
        "party": r["ruling_party_centre_exact"],
        "leak_status": r["leak_status"],
        "action_taken": r["action_taken"],
        "note": r["note"],
        "arrests": r["arrests"],
        "convictions": r["convictions"],
        "aspirants_affected": r["aspirants_affected"],
        "source_name": r["source_name"],
        "source_url": r["source_url"],
        "confidence": r["confidence"],
    })

out = {
    "kpis": kpis,
    "yearly_counts": year_counts,
    "era_data": era_data,
    "body_type_counts": body_type_counts,
    "leak_status_counts": leak_status_counts,
    "action_data": action_data,
    "top_states": top_states,
    "top_exams": top_exams,
    "rows": table_rows,
}

import os
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("KPIs:", kpis)
print("Era data:", era_data)
print("Body type:", body_type_counts)
print("Leak status:", leak_status_counts)
print("Action data:", action_data)
print("Top states:", top_states[:5])
print("Top exams:", top_exams[:3])
print("Table rows:", len(table_rows))
