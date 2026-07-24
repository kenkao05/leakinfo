"""
Searches for new India exam-leak incidents since the most recent date in the
CSV, validates and deduplicates them, and writes any accepted rows back into
india_exam_leaks_master.csv. Rows below Medium confidence, or touching
arrests/convictions/deaths fields, are written to pending_review.csv instead
so a human looks at them before they ever reach the dataset.
"""

import csv
import json
import os
import re
from datetime import date, datetime

from groq import Groq

CSV_PATH = "india_exam_leaks_master.csv"
REVIEW_PATH = "pending_review.csv"

COLUMNS = [
    "incident_id", "date", "era", "pm_of_year_exact", "ruling_party_centre_exact",
    "exam_name", "conducting_body", "body_type", "area", "leak_status",
    "action_taken", "note", "arrests", "convictions", "aspirants_affected",
    "linked_deaths", "deaths_note", "source_name", "source_url", "confidence"
]

# Known transition dates — extend this list if a government ever changes again.
PM_TRANSITIONS = [
    (date(1998, 3, 19), "Atal Bihari Vajpayee", "NDA"),
    (date(2004, 5, 22), "Manmohan Singh", "UPA"),
    (date(2014, 5, 26), "Narendra Modi", "NDA"),
]


def compute_exact_fields(incident_date: date):
    """Deterministically derive PM/ruling party from the real transition dates —
    never trust the model to get this arithmetic right."""
    pm, party = PM_TRANSITIONS[0][1], PM_TRANSITIONS[0][2]
    for transition_date, transition_pm, transition_party in PM_TRANSITIONS:
        if incident_date >= transition_date:
            pm, party = transition_pm, transition_party
    return pm, party


def parse_date(d: str) -> date:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except ValueError:
        # year-only placeholder like "2023-01-01"
        return datetime.strptime(d[:4] + "-01-01", "%Y-%m-%d").date()


def load_existing_rows():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def next_incident_id(rows):
    nums = [int(r["incident_id"].split("-")[1]) for r in rows if r["incident_id"].startswith("PL-")]
    return max(nums, default=0) + 1


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def is_duplicate(candidate, existing_rows):
    """Fuzzy-ish dedupe: same exam name + same area, dates within 30 days."""
    for row in existing_rows:
        if normalize(candidate["exam_name"]) == normalize(row["exam_name"]) and \
           normalize(candidate["area"]) == normalize(row["area"]):
            try:
                d1 = parse_date(candidate["date"])
                d2 = parse_date(row["date"])
                if abs((d1 - d2).days) <= 30:
                    return True
            except Exception:
                return True  # if dates are unparseable, err toward treating as duplicate
    return False


def ask_groq_for_incidents(since_date: str):
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    system_prompt = f"""You are a research assistant compiling a dataset of India exam-leak incidents.
Search the web for CONFIRMED, ALLEGED, DENIED, or SUSPECTED exam paper leaks, cancellations, or
related irregularities in India, reported since {since_date}. This includes national entrance exams
(NEET, JEE, CUET, CTET, UGC-NET), central recruitment exams (SSC, UPSC, Railways, KVS, ONGC, ASRB, Army),
state recruitment exams (police, teacher eligibility, PSC), and school board exams (CBSE, state boards).

Return ONLY a raw JSON array, no markdown fences, no commentary, no preamble. Each object must have
EXACTLY these keys (use empty string "" for unknown text fields, empty string for unknown numbers too):

date (YYYY-MM-DD, or YYYY-01-01 if only the year is known)
exam_name
conducting_body
body_type ("Central" or "State")
area (state/UT name, or "All India")
leak_status ("Confirmed", "Alleged", "Denied", or "Suspected")
action_taken (+-joined tags, e.g. "Exam cancelled + Arrests-FIR + Probe (CBI)")
note (2-3 sentence factual summary)
arrests (integer as string, or "")
convictions (integer as string, or "")
aspirants_affected (integer as string, or "")
linked_deaths (integer as string, or "")
deaths_note (only if linked_deaths > 0)
source_name (the publication name)
source_url (the actual article URL — must be a real, working URL you found via search)
confidence ("High", "Medium", or "Low" — how well-corroborated is this, not how serious)

If you find nothing new, return an empty array: []
Do not invent source_url values. If you cannot find a working URL for an incident, omit that incident
entirely rather than guessing at a URL."""

    response = client.chat.completions.create(
        model="groq/compound",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Find India exam leak incidents reported since {since_date}."},
        ],
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("WARNING: model did not return valid JSON. Raw output:")
        print(raw)
        return []


def main():
    existing_rows = load_existing_rows()
    last_date = max(parse_date(r["date"]) for r in existing_rows)
    since_str = last_date.isoformat()

    print(f"Sweeping for incidents since {since_str}...")
    candidates = ask_groq_for_incidents(since_str)
    print(f"Model returned {len(candidates)} candidate incident(s).")

    next_id = next_incident_id(existing_rows)
    accepted, needs_review = [], []

    for c in candidates:
        if not c.get("source_url") or not c.get("exam_name"):
            continue  # refuse anything without a real source or name
        if is_duplicate(c, existing_rows):
            print(f"Skipping likely duplicate: {c.get('exam_name')} / {c.get('area')}")
            continue

        d = parse_date(c["date"])
        pm, party = compute_exact_fields(d)

        row = {
            "incident_id": f"PL-{next_id:04d}",
            "date": c["date"],
            "era": "",  # left blank on purpose — see NOTE below
            "pm_of_year_exact": pm,
            "ruling_party_centre_exact": party,
            "exam_name": c.get("exam_name", ""),
            "conducting_body": c.get("conducting_body", ""),
            "body_type": c.get("body_type", ""),
            "area": c.get("area", ""),
            "leak_status": c.get("leak_status", "Suspected"),
            "action_taken": c.get("action_taken", ""),
            "note": c.get("note", ""),
            "arrests": c.get("arrests", ""),
            "convictions": c.get("convictions", ""),
            "aspirants_affected": c.get("aspirants_affected", ""),
            "linked_deaths": c.get("linked_deaths", ""),
            "deaths_note": c.get("deaths_note", ""),
            "source_name": c.get("source_name", ""),
            "source_url": c["source_url"],
            "confidence": c.get("confidence", "Low"),
        }

        needs_manual_review = (
            row["confidence"] not in ("High", "Medium")
            or row["arrests"] not in ("", "0")
            or row["convictions"] not in ("", "0")
            or row["linked_deaths"] not in ("", "0")
        )

        if needs_manual_review:
            needs_review.append(row)
        else:
            accepted.append(row)
            next_id += 1

    if accepted:
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            for row in accepted:
                writer.writerow(row)
        print(f"Appended {len(accepted)} row(s) to {CSV_PATH}.")

    if needs_review:
        write_header = not os.path.exists(REVIEW_PATH)
        with open(REVIEW_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            if write_header:
                writer.writeheader()
            for row in needs_review:
                writer.writerow(row)
        print(f"Flagged {len(needs_review)} row(s) for manual review in {REVIEW_PATH}.")

    if not accepted and not needs_review:
        print("Nothing new found this run.")


if __name__ == "__main__":
    main()