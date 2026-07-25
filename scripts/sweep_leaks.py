"""
Searches for new India exam-leak incidents since the most recent date in the
CSV, validates and deduplicates them, and writes any accepted rows back into
india_exam_leaks_master.csv. Rows below Medium confidence, or touching
arrests/convictions/deaths fields, are written to pending_review.csv instead
so a human looks at them before they ever reach the dataset.

Uses Tavily for search (free tier, no card) and a plain Groq model (not
groq/compound) purely for extraction from the returned snippets.

Guards this version implements:
1. Skips protest/political-fallout coverage of an ALREADY-KNOWN leak rather
   than treating it as a new incident.
2. Dedupes candidates against BOTH the existing CSV and each other within
   the same run, using substring matching on exam name (not exact string
   equality) since sources spell out exam names with varying completeness
   (e.g. "Maharashtra TET" vs "Maharashtra Teacher Eligibility Test (TET)").
3. Uses action-word + recency-narrowed search queries and sorts results by
   published date, so single-institution/regional stories aren't drowned
   out by the dominant national story of the moment.
4. Increments the incident ID counter for EVERY accepted candidate,
   including ones routed to pending_review.csv — previously only fully
   auto-accepted rows incremented the counter, so multiple flagged rows in
   the same run all got stamped with the same ID.
5. Filters out social media URLs (Facebook, Twitter/X, Instagram, Reddit,
   YouTube) before they ever reach the model — these aren't edited/
   fact-checked sources and shouldn't be treated as equivalent to news
   reporting.
"""

import csv
import json
import os
import re
from datetime import date, datetime

import requests
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

# Action-word and category-specific queries. Pure topic queries tend to
# surface evergreen explainers and whatever the dominant national story is
# that week, drowning out smaller regional or single-institution leaks.
SEARCH_QUERIES = [
    "India exam paper leak arrested",
    "India recruitment exam leak cancelled arrested",
    "NEET JEE CUET leak investigation",
    "India board exam paper leak cancelled",
    "state PSC teacher eligibility test leak India arrested",
    "university exam paper leak India professor arrested",
    "college exam question paper leaked India cancelled",
]

# Social platforms aren't edited/fact-checked sources — exclude them at the
# search stage so the model never even sees them as candidate sources.
BLOCKED_DOMAINS = (
    "facebook.com", "twitter.com", "x.com", "instagram.com",
    "reddit.com", "youtube.com", "threads.net",
)

# How many recent existing rows to show the model, so it can recognize
# "this article is about something already in the dataset" rather than
# inventing a new row for follow-up coverage.
RECENT_CONTEXT_ROWS = 15


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


def is_duplicate(candidate, rows_to_check):
    """Fuzzy dedupe: exam name as a SUBSTRING match either direction (not
    exact equality, since sources spell out names with varying completeness)
    + same area, dates within 30 days. rows_to_check should include BOTH the
    pre-existing CSV rows AND anything already accepted earlier in this run."""
    cand_name = normalize(candidate["exam_name"])
    cand_area = normalize(candidate["area"])
    for row in rows_to_check:
        row_name = normalize(row["exam_name"])
        row_area = normalize(row["area"])
        name_match = bool(cand_name) and bool(row_name) and (cand_name in row_name or row_name in cand_name)
        if name_match and cand_area == row_area:
            try:
                d1 = parse_date(candidate["date"])
                d2 = parse_date(row["date"])
                if abs((d1 - d2).days) <= 30:
                    return True
            except Exception:
                return True  # if dates are unparseable, err toward treating as duplicate
    return False


def search_tavily(query: str):
    resp = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": os.environ["TAVILY_API_KEY"],
            "query": query,
            "topic": "news",
            "time_range": "week",   # narrower window surfaces fresher, less-covered stories
            "days": 14,             # explicit lookback, belt-and-suspenders with time_range
            "max_results": 10,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def gather_search_results():
    all_results = []
    seen_urls = set()
    for q in SEARCH_QUERIES:
        try:
            results = search_tavily(q)
        except requests.HTTPError as e:
            print(f"Tavily search failed for query '{q}': {e}")
            continue
        for r in results:
            url = r.get("url", "")
            if not url or url in seen_urls:
                continue
            if any(domain in url for domain in BLOCKED_DOMAINS):
                print(f"Skipping social media source: {url}")
                continue
            seen_urls.add(url)
            all_results.append(r)

    # Most recent first — helps the model prioritize genuinely new stories
    # over evergreen/background pieces that happen to rank well.
    all_results.sort(key=lambda r: r.get("published_date", ""), reverse=True)
    return all_results


def recent_incidents_summary(existing_rows):
    """A short plain-text list of recent known incidents, so the model can
    recognize when an article is follow-up coverage of something already
    in the dataset rather than a new incident."""
    sorted_rows = sorted(existing_rows, key=lambda r: parse_date(r["date"]), reverse=True)
    lines = []
    for r in sorted_rows[:RECENT_CONTEXT_ROWS]:
        lines.append(f"- {r['date']}: {r['exam_name']} ({r['area']}) — status: {r['leak_status']}")
    return "\n".join(lines)


def ask_groq_to_extract(since_date: str, search_results, existing_rows):
    if not search_results:
        return []

    source_block = "\n\n".join(
        f"URL: {r['url']}\nPublished: {r.get('published_date', 'unknown')}\n"
        f"Title: {r.get('title', '')}\nSnippet: {r.get('content', '')[:500]}"
        for r in search_results
    )

    known_incidents = recent_incidents_summary(existing_rows)

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    system_prompt = f"""You are extracting NEW India exam-leak INCIDENTS from search results below.
An "incident" means a specific instance of an exam paper leak, exam cancellation due to
irregularities, or a newly reported exam-related fraud/malpractice case. This includes school,
college, and university-level leaks, not just national/state government exams.

Only include incidents clearly described in the provided sources, reported since {since_date}.
Never invent a URL or a detail not present in the snippets. If a snippet is too vague to extract
a real incident, skip it. Use the Published date of each source to judge how current it is.

DO NOT create a row for an article that is:
- Protest coverage, sit-ins, marches, or demonstrations about an exam leak (even if described in
  detail) unless it also reports a genuinely NEW, separate leak incident not already covered below
- A resignation demand, political statement, or government response (e.g. "fast-track courts
  announced") about an ALREADY-KNOWN leak
- A court hearing, verdict update, or investigation-progress update on an incident already listed
  below
- An opinion piece, retrospective, or analysis piece referencing past leaks
- An official denial/refutation of leak rumors (e.g. "CBSE says claims are baseless") — that is a
  non-incident, not a leak
- An UNVERIFIED allegation with no confirmed action taken (no cancellation, no arrest, no official
  investigation) — mark these Low confidence at most, and only if a credible news outlet reported it

These are RECENT INCIDENTS ALREADY IN THE DATASET — do not create new rows that are just follow-up
coverage of these, and use loose/partial name matches too (e.g. "Maharashtra TET" and "Maharashtra
Teacher Eligibility Test" are the SAME incident, not two):
{known_incidents}

If an article is about ongoing fallout (protests, political demands, court proceedings) tied to one
of the incidents above, or an incident with a similar exam name / area / date to one above, SKIP IT
ENTIRELY. Only extract something as new if it describes a genuinely distinct leak.

Return ONLY a raw JSON array, no markdown fences, no commentary, no preamble. Each object must
have EXACTLY these keys (use "" for unknown text/number fields):

date (YYYY-MM-DD — use the date of the EXAM/INCIDENT itself, not the date of an arrest or report
  that came later, if both are mentioned)
exam_name
conducting_body
body_type ("Central" or "State")
area (state/UT name, or "All India")
leak_status ("Confirmed", "Alleged", "Denied", or "Suspected")
action_taken (+-joined tags, e.g. "Exam cancelled + Arrests-FIR + Probe (CBI)")
note (2-3 sentence factual summary of the LEAK ITSELF, not the political fallout)
arrests (integer as string, or "")
convictions (integer as string, or "")
aspirants_affected (integer as string, or "")
linked_deaths (integer as string, or "")
deaths_note (only if linked_deaths > 0)
source_name (the publication name — must be a real news outlet, not a social media platform)
source_url (must be one of the exact URLs given above — do not alter or guess at URLs)
confidence ("High", "Medium", or "Low" — how well-corroborated is this, not how serious)

If nothing qualifies as a genuinely new incident, return [].

SOURCES:
{source_block}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}],
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

    search_results = gather_search_results()
    print(f"Tavily returned {len(search_results)} unique source(s) after filtering.")

    candidates = ask_groq_to_extract(since_str, search_results, existing_rows)
    print(f"Model extracted {len(candidates)} candidate incident(s).")

    next_id = next_incident_id(existing_rows)
    accepted, needs_review = [], []
    valid_urls = {r["url"] for r in search_results}

    # This list grows as we accept/flag rows within this same run, so
    # candidate #2 gets checked against candidate #1 too — not just against
    # the CSV as it was before this run started.
    rows_seen_this_run = list(existing_rows)

    for c in candidates:
        if not c.get("source_url") or not c.get("exam_name"):
            continue  # refuse anything without a real source or name
        if c["source_url"] not in valid_urls:
            print(f"Skipping row with unverified URL: {c.get('source_url')}")
            continue
        if is_duplicate(c, rows_seen_this_run):
            print(f"Skipping likely duplicate: {c.get('exam_name')} / {c.get('area')}")
            continue

        d = parse_date(c["date"])
        pm, party = compute_exact_fields(d)

        row = {
            "incident_id": f"PL-{next_id:04d}",
            "date": c["date"],
            "era": "",  # left blank on purpose — fill in during PR review if you want it
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

        # next_id is incremented in BOTH branches now — previously only the
        # accepted branch incremented it, so multiple flagged rows in the
        # same run all got stamped with the same incident_id.
        if needs_manual_review:
            needs_review.append(row)
        else:
            accepted.append(row)
        rows_seen_this_run.append(row)
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