# India Exam Leak Tracker — full project handoff

This is a complete, self-contained handoff for the `leakinfo` dashboard: what the dataset is, how it was built, the full file structure, and every line of code needed to reproduce the project from scratch on your own machine and deploy it to Vercel.

**Stack:** Vite + React 18, Chart.js, GSAP, ogl (WebGL), plain CSS (no Tailwind). No backend — the dataset is baked into the app at build time as a static JSON file generated from the CSV.

---

## 1. About the dataset

The master file is **`india_exam_leaks_master.csv`** (delivered alongside this document, not pasted inline since it's a data file, not code). It contains **129 incidents** of alleged or confirmed exam paper leaks and cancellations in India, **2000–2026**, spanning national entrance exams (NEET, JEE, CUET, CTET, UGC-NET), central recruitment exams (SSC, UPSC, Railways, KVS, ONGC, ASRB, Army), state recruitment exams (police, teacher eligibility, PSC exams), and school board exams (CBSE, state boards).

### Schema (20 columns)

| Column | Description |
|---|---|
| `incident_id` | Stable ID, `PL-0001`...`PL-0129` |
| `date` | Best-known date (`YYYY-MM-DD`); some are year-only placeholders (`-01-01`) where sources didn't give an exact date |
| `era` | Coarse original bucket (`NDA (1998-2004)`, `UPA (2004-May2014)`, `NDA (May2014-now)`) — kept for reference but see the caveat below |
| `pm_of_year_exact` | Prime Minister in office on the **exact** incident date, computed from real transition dates (2004-05-22, 2014-05-26), not the coarse bucket |
| `ruling_party_centre_exact` | Ruling party/coalition at the Centre, same exact-date basis |
| `exam_name` | Name of the exam and year/session |
| `conducting_body` | Organisation that ran the exam |
| `body_type` | `Central` or `State` |
| `area` | State/UT or "All India" |
| `leak_status` | `Confirmed`, `Alleged`, `Denied`, or `Suspected` — many "leaks" were later downgraded or denied by investigators; don't treat every row as proven |
| `action_taken` | `+`-joined tags, e.g. `Exam cancelled + Arrests-FIR + Probe (CBI)` |
| `note` | Free-text summary of what happened, with named officials/arrest counts where known |
| `arrests` / `convictions` | Plain integers where reported, blank otherwise |
| `aspirants_affected` | Plain integer where a specific number was reported, blank otherwise (most rows are blank — don't treat this as a complete census of scale) |
| `linked_deaths` / `deaths_note` | Only populated for cases with documented deaths connected to the investigation (e.g. Vyapam) |
| `source_name` / `source_url` | Attribution |
| `confidence` | `High` / `Medium` / `Low` — reflects how well-corroborated the row is, not how serious the incident was |

### Known caveats (worth repeating to anyone using this data)

- **Not exhaustive.** There is no official, complete registry of exam leaks in India. This is a research compilation from openly published English-language news coverage, so it under-represents incidents that only got regional-language or purely local coverage.
- **`era` vs `pm_of_year_exact` can disagree at the edges.** Example: incident `PL-0001` (AIPMT, 11 Apr 2004) is bucketed under `era = UPA (2004-May2014)` by the original source file, but the exact PM in office that day was Vajpayee (NDA) — Manmohan Singh's government only took office 22 May 2004. Use `pm_of_year_exact` for anything date-sensitive.
- **Raw incident counts by administration are misleading** without normalizing for years in office and for how much better documentation/social media leak-detection has gotten over the 2000–2026 window. The dashboard normalizes for this; if you build your own charts, do the same.
- **`aspirants_affected` is sparse.** Ranking exams by this field ranks "biggest reported number," not "biggest actual leak."

---

## 2. What the site does

Three views, switched client-side (no routing library, no page reloads — simplest for a static Vercel deploy):

1. **Charts** — KPI strip + a `MagicBento` grid of Chart.js visualizations (yearly trend, incidents-per-year-in-office by administration, central-vs-state split, leak-status breakdown, top exams by aspirants affected, top states by incident count, action-taken breakdown), each with an inline methodology caveat. A `LineSidebar` on the right (desktop only) jumps between chart sections.
2. **Info** — the full CSV as a filterable, searchable, sortable table (filter by leak status, conducting-body type, administration, confidence; click a row to expand its full note and source link).
3. **About** — why the project exists, written in plain language, plus a `CardSwap` stack cycling through the major sources used.

A `CardNav` pill at the top switches between the three. A disclaimer modal appears on every load, stating the dataset was researched with AI assistance from open sources and should be independently verified before being relied on.

**Design tokens:** pastel blue/white throughout (`--accent: #6fa8dc`, `--bg: #f5faff`, `--surface: #ffffff`), Fraunces for display type, IBM Plex Sans for body, IBM Plex Mono for numbers/data. The `LightRays` WebGL background sits at `z-index: 0` in a fixed backdrop layer, with all real content in a `z-index: 1` wrapper, so it never renders on top of anything. The one deliberate contrast accent is the `CardSwap` cards on the About page, which use a dark navy gradient against the light page — everywhere else stays pastel.

**Mobile-first notes:**
- `CardNav` collapses to a hamburger with stacked full-width cards under 768px (built into the component).
- `MagicBento`'s hover/tilt/magnetism/particle effects auto-disable under 768px (`useMobileDetection`) — cards still render, just static, since none of those effects mean anything on touch.
- The right-side `LineSidebar` chart nav (proximity-hover driven, not touch-friendly) is hidden entirely under 1180px via `.charts-sidebar { display: none }` — on mobile you scroll the chart grid directly instead.
- `CardSwap` scales down at 640px via its own media query.
- The `DataTable` scrolls horizontally on narrow screens rather than compressing columns unreadably.
- `MagicBento`'s grid is `auto-fit, minmax(280px, 1fr)` below 900px, so cards stack to one column on phones automatically.

---

## 3. Setup steps

```bash
# 1. Create the project folder
mkdir leakinfo && cd leakinfo

# 2. Create the file structure below (Section 4), pasting in the code from Section 6.
#    Also save the master CSV (delivered separately) as india_exam_leaks_master.csv
#    at the project root.

# 3. Install dependencies
npm install

# 4. Generate src/data/leaks.json from the CSV
#    (save the script in Section 6.1 as prep_data.py at the project root first)
python3 prep_data.py

# 5. Run the dev server
npm run dev
# -> open http://localhost:5173

# 6. Build for production (sanity check before deploying)
npm run build
npm run preview

# 7. Deploy to Vercel
#    - Push the folder to a GitHub repo
#    - Import the repo at vercel.com/new
#    - Vercel auto-detects Vite: build command `npm run build`, output dir `dist`
#    - No environment variables needed (fully static, no backend)
```

If you ever edit the CSV, just re-run `python3 prep_data.py` and restart the dev server — `leaks.json` isn't meant to be hand-edited.

---

## 4. Final file structure

```
leakinfo/
├── india_exam_leaks_master.csv     ← the dataset (delivered separately)
├── prep_data.py                    ← CSV → src/data/leaks.json converter
├── package.json
├── vite.config.js
├── index.html
└── src/
    ├── main.jsx
    ├── index.css                   ← design tokens + global/layout CSS
    ├── App.jsx                     ← LightRays backdrop, CardNav, page switch
    ├── data/
    │   └── leaks.json              ← generated, do not hand-edit
    ├── components/
    │   ├── LightRays.jsx / .css    ← WebGL background (React Bits, adapted)
    │   ├── MagicBento.jsx / .css   ← animated chart-card grid (React Bits, adapted)
    │   ├── LineSidebar.jsx / .css  ← right-side chart jump-nav (React Bits, adapted)
    │   ├── CardNav.jsx / .css      ← top pill nav (React Bits, adapted)
    │   ├── CardSwap.jsx / .css     ← About-page source cards (React Bits, unchanged logic)
    │   ├── ChartCanvas.jsx         ← Chart.js wrapper used by every chart
    │   ├── CardHeader.jsx          ← small title+caveat header used inside bento cards
    │   ├── DataTable.jsx           ← searchable/sortable table (used by Info page)
    │   └── DisclaimerModal.jsx     ← AI/sourcing disclaimer, shown on every load
    └── pages/
        ├── ChartsPage.jsx
        ├── InfoPage.jsx
        └── AboutPage.jsx
```

---

## 5. Dependencies (`package.json`)

## 6. Full source code

### 6.1 `prep_data.py` (run once to generate `src/data/leaks.json`)

```python
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
```

### `package.json`

```json
{
  "name": "india-exam-leak-dashboard",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "chart.js": "^4.4.4",
    "gsap": "^3.12.5",
    "ogl": "^1.0.10",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.0"
  }
}
```

### `vite.config.js`

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
});
```

### `index.html`

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>India Exam Leak Tracker · 2000–2026</title>
    <meta name="description" content="A tracked record of exam paper leaks and cancellations in India, 2000–2026." />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap"
      rel="stylesheet"
    />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

### `src/main.jsx`

```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### `src/index.css`

```css
:root {
  /* ---- Color tokens: pastel blue / white ---- */
  --bg: #f5faff;
  --bg-deep: #eef6ff;
  --surface: #ffffff;
  --surface-soft: #f7fbff;
  --border: #d9e9fa;
  --border-strong: #bcdcf7;

  --accent: #6fa8dc;
  --accent-deep: #3f7cb8;
  --accent-soft: #cfe6fb;
  --accent-rgb: 111, 168, 220;

  --text-primary: #16283b;
  --text-secondary: #4d6a85;
  --text-muted: #83a0b8;

  --confirmed: #4f8fce;
  --alleged: #9cc2e8;
  --denied: #e3b8a0;
  --suspected: #c9d6e3;

  /* ---- Type ---- */
  --font-display: "Fraunces", "Georgia", serif;
  --font-body: "IBM Plex Sans", -apple-system, "Segoe UI", sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, monospace;
}

* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--text-primary);
  font-family: var(--font-body);
  -webkit-font-smoothing: antialiased;
}

#root {
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
}

h1,
h2,
h3 {
  font-family: var(--font-display);
  font-weight: 600;
  letter-spacing: -0.01em;
  margin: 0;
  color: var(--text-primary);
}

p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.55;
}

a {
  color: var(--accent-deep);
}

.mono {
  font-family: var(--font-mono);
}

/* Reduced motion respect */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
    scroll-behavior: auto !important;
  }
}

::selection {
  background: var(--accent-soft);
  color: var(--text-primary);
}

/* Visible keyboard focus */
a:focus-visible,
button:focus-visible,
input:focus-visible,
select:focus-visible,
[tabindex]:focus-visible {
  outline: 2px solid var(--accent-deep);
  outline-offset: 2px;
  border-radius: 4px;
}

::-webkit-scrollbar {
  width: 10px;
}
::-webkit-scrollbar-track {
  background: var(--bg-deep);
}
::-webkit-scrollbar-thumb {
  background: var(--border-strong);
  border-radius: 6px;
}

/* ---- App-level layout ---- */
.rays-backdrop {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.app-shell {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  padding-top: 6.5rem;
}

.charts-sidebar {
  position: fixed;
  right: 1.5rem;
  top: 50%;
  transform: translateY(-50%);
  z-index: 20;
}

@media (max-width: 1180px) {
  .charts-sidebar {
    display: none;
  }
}

.about-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 2.5rem;
  align-items: center;
  padding: 1rem 0 3rem;
}

.about-swap {
  display: flex;
  justify-content: center;
  padding-top: 2rem;
}

@media (max-width: 860px) {
  .about-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  .about-swap {
    padding-top: 0.5rem;
    padding-bottom: 2.5rem;
  }
}

@media (max-width: 640px) {
  .app-shell {
    padding-top: 5.5rem;
  }
}
```

### `src/App.jsx`

```jsx
import { useState } from 'react';
import LightRays from './components/LightRays.jsx';
import CardNav from './components/CardNav.jsx';
import DisclaimerModal from './components/DisclaimerModal.jsx';
import ChartsPage from './pages/ChartsPage.jsx';
import InfoPage from './pages/InfoPage.jsx';
import AboutPage from './pages/AboutPage.jsx';
import data from './data/leaks.json';

function App() {
  const [page, setPage] = useState('charts');

  const navItems = [
    {
      label: 'Charts',
      bgColor: '#eaf3fc',
      textColor: '#16283b',
      links: [
        { label: 'Trends & breakdowns', ariaLabel: 'Go to charts overview', onClick: () => setPage('charts') },
        { label: 'Top exams & states', ariaLabel: 'Go to top exams and states charts', onClick: () => setPage('charts') }
      ]
    },
    {
      label: 'Info',
      bgColor: '#d7e9fa',
      textColor: '#16283b',
      links: [
        { label: 'Browse all incidents', ariaLabel: 'Go to the incident table', onClick: () => setPage('info') },
        { label: 'Filter by status or state', ariaLabel: 'Go to filters', onClick: () => setPage('info') }
      ]
    },
    {
      label: 'About',
      bgColor: '#16283b',
      textColor: '#eaf3fc',
      links: [
        { label: 'Why this exists', ariaLabel: 'Go to the about page', onClick: () => setPage('about') },
        { label: 'Sources used', ariaLabel: 'Go to sources', onClick: () => setPage('about') }
      ]
    }
  ];

  return (
    <>
      <DisclaimerModal />

      <div className="rays-backdrop">
        <LightRays raysOrigin="top-center" raysColor="#bcdcf7" raysSpeed={0.7} lightSpread={1.4} rayLength={1.6} followMouse mouseInfluence={0.06} noiseAmount={0.03} saturation={0.8} />
      </div>

      <CardNav logoText="Exam Leak Tracker" items={navItems} baseColor="#ffffff" menuColor="#16283b" />

      <div className="app-shell">
        {page === 'charts' && <ChartsPage />}
        {page === 'info' && <InfoPage rows={data.rows} />}
        {page === 'about' && <AboutPage />}
      </div>
    </>
  );
}

export default App;
```

### `src/components/LightRays.jsx`

```jsx
import { useRef, useEffect, useState } from 'react';
import { Renderer, Program, Triangle, Mesh } from 'ogl';
import './LightRays.css';

const DEFAULT_COLOR = '#bcdcf7';

const hexToRgb = hex => {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return m ? [parseInt(m[1], 16) / 255, parseInt(m[2], 16) / 255, parseInt(m[3], 16) / 255] : [1, 1, 1];
};

const getAnchorAndDir = (origin, w, h) => {
  const outside = 0.2;
  switch (origin) {
    case 'top-left':
      return { anchor: [0, -outside * h], dir: [0, 1] };
    case 'top-right':
      return { anchor: [w, -outside * h], dir: [0, 1] };
    case 'left':
      return { anchor: [-outside * w, 0.5 * h], dir: [1, 0] };
    case 'right':
      return { anchor: [(1 + outside) * w, 0.5 * h], dir: [-1, 0] };
    case 'bottom-left':
      return { anchor: [0, (1 + outside) * h], dir: [0, -1] };
    case 'bottom-center':
      return { anchor: [0.5 * w, (1 + outside) * h], dir: [0, -1] };
    case 'bottom-right':
      return { anchor: [w, (1 + outside) * h], dir: [0, -1] };
    default: // "top-center"
      return { anchor: [0.5 * w, -outside * h], dir: [0, 1] };
  }
};

const LightRays = ({
  raysOrigin = 'top-center',
  raysColor = DEFAULT_COLOR,
  raysSpeed = 1,
  lightSpread = 1,
  rayLength = 2,
  pulsating = false,
  fadeDistance = 1.0,
  saturation = 1.0,
  followMouse = true,
  mouseInfluence = 0.1,
  noiseAmount = 0.0,
  distortion = 0.0,
  className = ''
}) => {
  const containerRef = useRef(null);
  const uniformsRef = useRef(null);
  const rendererRef = useRef(null);
  const mouseRef = useRef({ x: 0.5, y: 0.5 });
  const smoothMouseRef = useRef({ x: 0.5, y: 0.5 });
  const animationIdRef = useRef(null);
  const meshRef = useRef(null);
  const cleanupFunctionRef = useRef(null);
  const [isVisible, setIsVisible] = useState(false);
  const observerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    observerRef.current = new IntersectionObserver(
      entries => {
        const entry = entries[0];
        setIsVisible(entry.isIntersecting);
      },
      { threshold: 0.1 }
    );

    observerRef.current.observe(containerRef.current);

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
        observerRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!isVisible || !containerRef.current) return;

    if (cleanupFunctionRef.current) {
      cleanupFunctionRef.current();
      cleanupFunctionRef.current = null;
    }

    const initializeWebGL = async () => {
      if (!containerRef.current) return;

      await new Promise(resolve => setTimeout(resolve, 10));

      if (!containerRef.current) return;

      const renderer = new Renderer({
        dpr: Math.min(window.devicePixelRatio, 2),
        alpha: true
      });
      rendererRef.current = renderer;

      const gl = renderer.gl;
      gl.canvas.style.width = '100%';
      gl.canvas.style.height = '100%';

      while (containerRef.current.firstChild) {
        containerRef.current.removeChild(containerRef.current.firstChild);
      }
      containerRef.current.appendChild(gl.canvas);

      const vert = `
attribute vec2 position;
varying vec2 vUv;
void main() {
  vUv = position * 0.5 + 0.5;
  gl_Position = vec4(position, 0.0, 1.0);
}`;

      const frag = `precision highp float;

uniform float iTime;
uniform vec2  iResolution;

uniform vec2  rayPos;
uniform vec2  rayDir;
uniform vec3  raysColor;
uniform float raysSpeed;
uniform float lightSpread;
uniform float rayLength;
uniform float pulsating;
uniform float fadeDistance;
uniform float saturation;
uniform vec2  mousePos;
uniform float mouseInfluence;
uniform float noiseAmount;
uniform float distortion;

varying vec2 vUv;

float noise(vec2 st) {
  return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
}

float rayStrength(vec2 raySource, vec2 rayRefDirection, vec2 coord,
                  float seedA, float seedB, float speed) {
  vec2 sourceToCoord = coord - raySource;
  vec2 dirNorm = normalize(sourceToCoord);
  float cosAngle = dot(dirNorm, rayRefDirection);

  float distortedAngle = cosAngle + distortion * sin(iTime * 2.0 + length(sourceToCoord) * 0.01) * 0.2;

  float spreadFactor = pow(max(distortedAngle, 0.0), 1.0 / max(lightSpread, 0.001));

  float distance = length(sourceToCoord);
  float maxDistance = iResolution.x * rayLength;
  float lengthFalloff = clamp((maxDistance - distance) / maxDistance, 0.0, 1.0);

  float fadeFalloff = clamp((iResolution.x * fadeDistance - distance) / (iResolution.x * fadeDistance), 0.5, 1.0);
  float pulse = pulsating > 0.5 ? (0.8 + 0.2 * sin(iTime * speed * 3.0)) : 1.0;

  float baseStrength = clamp(
    (0.45 + 0.15 * sin(distortedAngle * seedA + iTime * speed)) +
    (0.3 + 0.2 * cos(-distortedAngle * seedB + iTime * speed)),
    0.0, 1.0
  );

  return baseStrength * lengthFalloff * fadeFalloff * spreadFactor * pulse;
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 coord = vec2(fragCoord.x, iResolution.y - fragCoord.y);

  vec2 finalRayDir = rayDir;
  if (mouseInfluence > 0.0) {
    vec2 mouseScreenPos = mousePos * iResolution.xy;
    vec2 mouseDirection = normalize(mouseScreenPos - rayPos);
    finalRayDir = normalize(mix(rayDir, mouseDirection, mouseInfluence));
  }

  vec4 rays1 = vec4(1.0) *
               rayStrength(rayPos, finalRayDir, coord, 36.2214, 21.11349,
                           1.5 * raysSpeed);
  vec4 rays2 = vec4(1.0) *
               rayStrength(rayPos, finalRayDir, coord, 22.3991, 18.0234,
                           1.1 * raysSpeed);

  fragColor = rays1 * 0.5 + rays2 * 0.4;

  if (noiseAmount > 0.0) {
    float n = noise(coord * 0.01 + iTime * 0.1);
    fragColor.rgb *= (1.0 - noiseAmount + noiseAmount * n);
  }

  float brightness = 1.0 - (coord.y / iResolution.y);
  fragColor.x *= 0.1 + brightness * 0.8;
  fragColor.y *= 0.3 + brightness * 0.6;
  fragColor.z *= 0.5 + brightness * 0.5;

  if (saturation != 1.0) {
    float gray = dot(fragColor.rgb, vec3(0.299, 0.587, 0.114));
    fragColor.rgb = mix(vec3(gray), fragColor.rgb, saturation);
  }

  fragColor.rgb *= raysColor;
}

void main() {
  vec4 color;
  mainImage(color, gl_FragCoord.xy);
  gl_FragColor  = color;
}`;

      const uniforms = {
        iTime: { value: 0 },
        iResolution: { value: [1, 1] },

        rayPos: { value: [0, 0] },
        rayDir: { value: [0, 1] },

        raysColor: { value: hexToRgb(raysColor) },
        raysSpeed: { value: raysSpeed },
        lightSpread: { value: lightSpread },
        rayLength: { value: rayLength },
        pulsating: { value: pulsating ? 1.0 : 0.0 },
        fadeDistance: { value: fadeDistance },
        saturation: { value: saturation },
        mousePos: { value: [0.5, 0.5] },
        mouseInfluence: { value: mouseInfluence },
        noiseAmount: { value: noiseAmount },
        distortion: { value: distortion }
      };
      uniformsRef.current = uniforms;

      const geometry = new Triangle(gl);
      const program = new Program(gl, {
        vertex: vert,
        fragment: frag,
        uniforms
      });
      const mesh = new Mesh(gl, { geometry, program });
      meshRef.current = mesh;

      const updatePlacement = () => {
        if (!containerRef.current || !renderer) return;

        renderer.dpr = Math.min(window.devicePixelRatio, 2);

        const { clientWidth: wCSS, clientHeight: hCSS } = containerRef.current;
        renderer.setSize(wCSS, hCSS);

        const dpr = renderer.dpr;
        const w = wCSS * dpr;
        const h = hCSS * dpr;

        uniforms.iResolution.value = [w, h];

        const { anchor, dir } = getAnchorAndDir(raysOrigin, w, h);
        uniforms.rayPos.value = anchor;
        uniforms.rayDir.value = dir;
      };

      const loop = t => {
        if (!rendererRef.current || !uniformsRef.current || !meshRef.current) {
          return;
        }

        uniforms.iTime.value = t * 0.001;

        if (followMouse && mouseInfluence > 0.0) {
          const smoothing = 0.92;

          smoothMouseRef.current.x = smoothMouseRef.current.x * smoothing + mouseRef.current.x * (1 - smoothing);
          smoothMouseRef.current.y = smoothMouseRef.current.y * smoothing + mouseRef.current.y * (1 - smoothing);

          uniforms.mousePos.value = [smoothMouseRef.current.x, smoothMouseRef.current.y];
        }

        try {
          renderer.render({ scene: mesh });
          animationIdRef.current = requestAnimationFrame(loop);
        } catch (error) {
          console.warn('WebGL rendering error:', error);
          return;
        }
      };

      window.addEventListener('resize', updatePlacement);
      updatePlacement();
      animationIdRef.current = requestAnimationFrame(loop);

      cleanupFunctionRef.current = () => {
        if (animationIdRef.current) {
          cancelAnimationFrame(animationIdRef.current);
          animationIdRef.current = null;
        }

        window.removeEventListener('resize', updatePlacement);

        if (renderer) {
          try {
            const canvas = renderer.gl.canvas;
            const loseContextExt = renderer.gl.getExtension('WEBGL_lose_context');
            if (loseContextExt) {
              loseContextExt.loseContext();
            }

            if (canvas && canvas.parentNode) {
              canvas.parentNode.removeChild(canvas);
            }
          } catch (error) {
            console.warn('Error during WebGL cleanup:', error);
          }
        }

        rendererRef.current = null;
        uniformsRef.current = null;
        meshRef.current = null;
      };
    };

    initializeWebGL();

    return () => {
      if (cleanupFunctionRef.current) {
        cleanupFunctionRef.current();
        cleanupFunctionRef.current = null;
      }
    };
  }, [
    isVisible,
    raysOrigin,
    raysColor,
    raysSpeed,
    lightSpread,
    rayLength,
    pulsating,
    fadeDistance,
    saturation,
    followMouse,
    mouseInfluence,
    noiseAmount,
    distortion
  ]);

  useEffect(() => {
    if (!uniformsRef.current || !containerRef.current || !rendererRef.current) return;

    const u = uniformsRef.current;
    const renderer = rendererRef.current;

    u.raysColor.value = hexToRgb(raysColor);
    u.raysSpeed.value = raysSpeed;
    u.lightSpread.value = lightSpread;
    u.rayLength.value = rayLength;
    u.pulsating.value = pulsating ? 1.0 : 0.0;
    u.fadeDistance.value = fadeDistance;
    u.saturation.value = saturation;
    u.mouseInfluence.value = mouseInfluence;
    u.noiseAmount.value = noiseAmount;
    u.distortion.value = distortion;

    const { clientWidth: wCSS, clientHeight: hCSS } = containerRef.current;
    const dpr = renderer.dpr;
    const { anchor, dir } = getAnchorAndDir(raysOrigin, wCSS * dpr, hCSS * dpr);
    u.rayPos.value = anchor;
    u.rayDir.value = dir;
  }, [
    raysColor,
    raysSpeed,
    lightSpread,
    raysOrigin,
    rayLength,
    pulsating,
    fadeDistance,
    saturation,
    mouseInfluence,
    noiseAmount,
    distortion
  ]);

  useEffect(() => {
    const handleMouseMove = e => {
      if (!containerRef.current || !rendererRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;
      mouseRef.current = { x, y };
    };

    if (followMouse) {
      window.addEventListener('mousemove', handleMouseMove);
      return () => window.removeEventListener('mousemove', handleMouseMove);
    }
  }, [followMouse]);

  return <div ref={containerRef} className={`light-rays-container ${className}`.trim()} />;
};

export default LightRays;
```

### `src/components/LightRays.css`

```css
.light-rays-container {
  width: 100%;
  height: 100%;
  position: relative;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}
```

### `src/components/MagicBento.jsx`

```jsx
import { useRef, useEffect, useCallback, useState } from 'react';
import { gsap } from 'gsap';
import './MagicBento.css';

const DEFAULT_PARTICLE_COUNT = 8;
const DEFAULT_SPOTLIGHT_RADIUS = 320;
const DEFAULT_GLOW_COLOR = '111, 168, 220'; // pastel blue, matches --accent-rgb
const MOBILE_BREAKPOINT = 768;

const createParticleElement = (x, y, color = DEFAULT_GLOW_COLOR) => {
  const el = document.createElement('div');
  el.className = 'particle';
  el.style.cssText = `
    position: absolute;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: rgba(${color}, 0.9);
    box-shadow: 0 0 6px rgba(${color}, 0.5);
    pointer-events: none;
    z-index: 100;
    left: ${x}px;
    top: ${y}px;
  `;
  return el;
};

const calculateSpotlightValues = radius => ({
  proximity: radius * 0.5,
  fadeDistance: radius * 0.75
});

const updateCardGlowProperties = (card, mouseX, mouseY, glow, radius) => {
  const rect = card.getBoundingClientRect();
  const relativeX = ((mouseX - rect.left) / rect.width) * 100;
  const relativeY = ((mouseY - rect.top) / rect.height) * 100;

  card.style.setProperty('--glow-x', `${relativeX}%`);
  card.style.setProperty('--glow-y', `${relativeY}%`);
  card.style.setProperty('--glow-intensity', glow.toString());
  card.style.setProperty('--glow-radius', `${radius}px`);
};

/**
 * A single animated bento card. Unlike the original React Bits demo, content
 * is passed in as children (e.g. a chart, a KPI stat, a table) rather than a
 * hardcoded title/description pair.
 */
const BentoCard = ({
  children,
  className = '',
  id,
  disableAnimations = false,
  particleCount = DEFAULT_PARTICLE_COUNT,
  glowColor = DEFAULT_GLOW_COLOR,
  enableTilt = false,
  enableStars = true,
  clickEffect = false,
  enableMagnetism = false
}) => {
  const cardRef = useRef(null);
  const particlesRef = useRef([]);
  const timeoutsRef = useRef([]);
  const isHoveredRef = useRef(false);
  const memoizedParticles = useRef([]);
  const particlesInitialized = useRef(false);
  const magnetismAnimationRef = useRef(null);

  const initializeParticles = useCallback(() => {
    if (particlesInitialized.current || !cardRef.current) return;
    const { width, height } = cardRef.current.getBoundingClientRect();
    memoizedParticles.current = Array.from({ length: particleCount }, () =>
      createParticleElement(Math.random() * width, Math.random() * height, glowColor)
    );
    particlesInitialized.current = true;
  }, [particleCount, glowColor]);

  const clearAllParticles = useCallback(() => {
    timeoutsRef.current.forEach(clearTimeout);
    timeoutsRef.current = [];
    magnetismAnimationRef.current?.kill();

    particlesRef.current.forEach(particle => {
      gsap.to(particle, {
        scale: 0,
        opacity: 0,
        duration: 0.3,
        ease: 'back.in(1.7)',
        onComplete: () => particle.parentNode?.removeChild(particle)
      });
    });
    particlesRef.current = [];
  }, []);

  const animateParticles = useCallback(() => {
    if (!cardRef.current || !isHoveredRef.current || !enableStars) return;
    if (!particlesInitialized.current) initializeParticles();

    memoizedParticles.current.forEach((particle, index) => {
      const timeoutId = setTimeout(() => {
        if (!isHoveredRef.current || !cardRef.current) return;

        const clone = particle.cloneNode(true);
        cardRef.current.appendChild(clone);
        particlesRef.current.push(clone);

        gsap.fromTo(clone, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: 'back.out(1.7)' });
        gsap.to(clone, {
          x: (Math.random() - 0.5) * 80,
          y: (Math.random() - 0.5) * 80,
          rotation: Math.random() * 360,
          duration: 2 + Math.random() * 2,
          ease: 'none',
          repeat: -1,
          yoyo: true
        });
        gsap.to(clone, { opacity: 0.25, duration: 1.5, ease: 'power2.inOut', repeat: -1, yoyo: true });
      }, index * 110);

      timeoutsRef.current.push(timeoutId);
    });
  }, [initializeParticles, enableStars]);

  useEffect(() => {
    if (disableAnimations || !cardRef.current) return;
    const element = cardRef.current;

    const handleMouseEnter = () => {
      isHoveredRef.current = true;
      animateParticles();
      if (enableTilt) {
        gsap.to(element, { rotateX: 3, rotateY: 3, duration: 0.3, ease: 'power2.out', transformPerspective: 1000 });
      }
    };

    const handleMouseLeave = () => {
      isHoveredRef.current = false;
      clearAllParticles();
      if (enableTilt) gsap.to(element, { rotateX: 0, rotateY: 0, duration: 0.3, ease: 'power2.out' });
      if (enableMagnetism) gsap.to(element, { x: 0, y: 0, duration: 0.3, ease: 'power2.out' });
    };

    const handleMouseMove = e => {
      if (!enableTilt && !enableMagnetism) return;
      const rect = element.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      if (enableTilt) {
        const rotateX = ((y - centerY) / centerY) * -6;
        const rotateY = ((x - centerX) / centerX) * 6;
        gsap.to(element, { rotateX, rotateY, duration: 0.1, ease: 'power2.out', transformPerspective: 1000 });
      }
      if (enableMagnetism) {
        const magnetX = (x - centerX) * 0.03;
        const magnetY = (y - centerY) * 0.03;
        magnetismAnimationRef.current = gsap.to(element, { x: magnetX, y: magnetY, duration: 0.3, ease: 'power2.out' });
      }
    };

    const handleClick = e => {
      if (!clickEffect) return;
      const rect = element.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const maxDistance = Math.max(
        Math.hypot(x, y),
        Math.hypot(x - rect.width, y),
        Math.hypot(x, y - rect.height),
        Math.hypot(x - rect.width, y - rect.height)
      );
      const ripple = document.createElement('div');
      ripple.style.cssText = `
        position: absolute;
        width: ${maxDistance * 2}px;
        height: ${maxDistance * 2}px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(${glowColor}, 0.28) 0%, rgba(${glowColor}, 0.12) 30%, transparent 70%);
        left: ${x - maxDistance}px;
        top: ${y - maxDistance}px;
        pointer-events: none;
        z-index: 1000;
      `;
      element.appendChild(ripple);
      gsap.fromTo(
        ripple,
        { scale: 0, opacity: 1 },
        { scale: 1, opacity: 0, duration: 0.7, ease: 'power2.out', onComplete: () => ripple.remove() }
      );
    };

    element.addEventListener('mouseenter', handleMouseEnter);
    element.addEventListener('mouseleave', handleMouseLeave);
    element.addEventListener('mousemove', handleMouseMove);
    element.addEventListener('click', handleClick);

    return () => {
      isHoveredRef.current = false;
      element.removeEventListener('mouseenter', handleMouseEnter);
      element.removeEventListener('mouseleave', handleMouseLeave);
      element.removeEventListener('mousemove', handleMouseMove);
      element.removeEventListener('click', handleClick);
      clearAllParticles();
    };
  }, [animateParticles, clearAllParticles, disableAnimations, enableTilt, enableMagnetism, clickEffect, glowColor]);

  return (
    <div
      ref={cardRef}
      id={id}
      className={`magic-bento-card ${className}`}
      style={{ '--glow-color': glowColor }}
    >
      {children}
    </div>
  );
};

const GlobalSpotlight = ({ gridRef, disableAnimations = false, enabled = true, spotlightRadius = DEFAULT_SPOTLIGHT_RADIUS, glowColor = DEFAULT_GLOW_COLOR }) => {
  const spotlightRef = useRef(null);

  useEffect(() => {
    if (disableAnimations || !gridRef?.current || !enabled) return;

    const spotlight = document.createElement('div');
    spotlight.className = 'global-spotlight';
    spotlight.style.cssText = `
      position: fixed;
      width: 700px;
      height: 700px;
      border-radius: 50%;
      pointer-events: none;
      background: radial-gradient(circle,
        rgba(${glowColor}, 0.10) 0%,
        rgba(${glowColor}, 0.05) 20%,
        rgba(${glowColor}, 0.02) 40%,
        transparent 70%
      );
      z-index: 5;
      opacity: 0;
      transform: translate(-50%, -50%);
    `;
    document.body.appendChild(spotlight);
    spotlightRef.current = spotlight;

    const handleMouseMove = e => {
      if (!spotlightRef.current || !gridRef.current) return;
      const section = gridRef.current.closest('.bento-section');
      const rect = section?.getBoundingClientRect();
      const mouseInside = rect && e.clientX >= rect.left && e.clientX <= rect.right && e.clientY >= rect.top && e.clientY <= rect.bottom;
      const cards = gridRef.current.querySelectorAll('.magic-bento-card');

      if (!mouseInside) {
        gsap.to(spotlightRef.current, { opacity: 0, duration: 0.3, ease: 'power2.out' });
        cards.forEach(card => card.style.setProperty('--glow-intensity', '0'));
        return;
      }

      const { proximity, fadeDistance } = calculateSpotlightValues(spotlightRadius);
      let minDistance = Infinity;

      cards.forEach(card => {
        const cardRect = card.getBoundingClientRect();
        const centerX = cardRect.left + cardRect.width / 2;
        const centerY = cardRect.top + cardRect.height / 2;
        const distance = Math.hypot(e.clientX - centerX, e.clientY - centerY) - Math.max(cardRect.width, cardRect.height) / 2;
        const effectiveDistance = Math.max(0, distance);
        minDistance = Math.min(minDistance, effectiveDistance);

        let glowIntensity = 0;
        if (effectiveDistance <= proximity) glowIntensity = 1;
        else if (effectiveDistance <= fadeDistance) glowIntensity = (fadeDistance - effectiveDistance) / (fadeDistance - proximity);

        updateCardGlowProperties(card, e.clientX, e.clientY, glowIntensity, spotlightRadius);
      });

      gsap.to(spotlightRef.current, { left: e.clientX, top: e.clientY, duration: 0.1, ease: 'power2.out' });

      const targetOpacity =
        minDistance <= proximity ? 0.6 : minDistance <= fadeDistance ? ((fadeDistance - minDistance) / (fadeDistance - proximity)) * 0.6 : 0;
      gsap.to(spotlightRef.current, { opacity: targetOpacity, duration: targetOpacity > 0 ? 0.2 : 0.5, ease: 'power2.out' });
    };

    const handleMouseLeave = () => {
      gridRef.current?.querySelectorAll('.magic-bento-card').forEach(card => card.style.setProperty('--glow-intensity', '0'));
      if (spotlightRef.current) gsap.to(spotlightRef.current, { opacity: 0, duration: 0.3, ease: 'power2.out' });
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseleave', handleMouseLeave);
      spotlightRef.current?.parentNode?.removeChild(spotlightRef.current);
    };
  }, [gridRef, disableAnimations, enabled, spotlightRadius, glowColor]);

  return null;
};

const useMobileDetection = () => {
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= MOBILE_BREAKPOINT);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);
  return isMobile;
};

/**
 * MagicBento grid.
 * `cards`: [{ id, size: 'wide' | 'normal', content: ReactNode }]
 */
const MagicBento = ({
  cards = [],
  enableStars = true,
  enableSpotlight = true,
  enableBorderGlow = true,
  disableAnimations = false,
  spotlightRadius = DEFAULT_SPOTLIGHT_RADIUS,
  particleCount = DEFAULT_PARTICLE_COUNT,
  enableTilt = true,
  glowColor = DEFAULT_GLOW_COLOR,
  clickEffect = false,
  enableMagnetism = true
}) => {
  const gridRef = useRef(null);
  const isMobile = useMobileDetection();
  const shouldDisableAnimations = disableAnimations || isMobile;

  return (
    <>
      {enableSpotlight && (
        <GlobalSpotlight
          gridRef={gridRef}
          disableAnimations={shouldDisableAnimations}
          enabled={enableSpotlight}
          spotlightRadius={spotlightRadius}
          glowColor={glowColor}
        />
      )}

      <div className="card-grid bento-section" ref={gridRef}>
        {cards.map(card => (
          <BentoCard
            key={card.id}
            id={card.id}
            className={`${card.size === 'wide' ? 'magic-bento-card--wide' : ''} ${enableBorderGlow ? 'magic-bento-card--border-glow' : ''}`}
            disableAnimations={shouldDisableAnimations}
            particleCount={particleCount}
            glowColor={glowColor}
            enableTilt={enableTilt}
            enableStars={enableStars}
            clickEffect={clickEffect}
            enableMagnetism={enableMagnetism}
          >
            {card.content}
          </BentoCard>
        ))}
      </div>
    </>
  );
};

export default MagicBento;
```

### `src/components/MagicBento.css`

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.1rem;
  width: 100%;
}

@media (min-width: 900px) {
  .card-grid {
    grid-template-columns: repeat(12, 1fr);
  }
  .magic-bento-card {
    grid-column: span 6;
  }
  .magic-bento-card--wide {
    grid-column: span 12;
  }
}

.magic-bento-card {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 260px;
  padding: 1.4rem 1.5rem;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: var(--surface);
  box-shadow: 0 1px 2px rgba(60, 100, 140, 0.05);
  overflow: hidden;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;

  --glow-x: 50%;
  --glow-y: 50%;
  --glow-intensity: 0;
  --glow-radius: 240px;
}

.magic-bento-card:hover {
  border-color: var(--border-strong);
  box-shadow: 0 10px 30px rgba(63, 124, 184, 0.12);
}

/* Border glow that follows the cursor */
.magic-bento-card--border-glow::after {
  content: '';
  position: absolute;
  inset: 0;
  padding: 1.5px;
  background: radial-gradient(
    var(--glow-radius) circle at var(--glow-x) var(--glow-y),
    rgba(var(--accent-rgb, 111, 168, 220), calc(var(--glow-intensity) * 0.9)) 0%,
    rgba(var(--accent-rgb, 111, 168, 220), calc(var(--glow-intensity) * 0.35)) 45%,
    transparent 70%
  );
  border-radius: inherit;
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  mask-composite: exclude;
  pointer-events: none;
  z-index: 2;
}

.particle {
  will-change: transform, opacity;
}

.global-spotlight {
  mix-blend-mode: normal;
  will-change: transform, opacity;
}

.bento-section {
  position: relative;
  user-select: none;
}

@media (max-width: 767px) {
  .magic-bento-card {
    min-height: 220px;
  }
}
```

### `src/components/LineSidebar.jsx`

```jsx
import { useRef, useState, useCallback, useEffect } from 'react';
import './LineSidebar.css';

const FALLOFF_CURVES = {
  linear: p => p,
  smooth: p => p * p * (3 - 2 * p),
  sharp: p => p * p * p
};

const DEFAULT_ITEMS = ['Overview'];

const LineSidebar = ({
  items = DEFAULT_ITEMS,
  accentColor = '#3f7cb8',
  textColor = '#4d6a85',
  markerColor = '#bcdcf7',
  showIndex = true,
  showMarker = true,
  proximityRadius = 100,
  maxShift = 24,
  falloff = 'smooth',
  markerLength = 44,
  markerGap = 0,
  tickScale = 0.5,
  scaleTick = true,
  itemGap = 22,
  fontSize = 0.95,
  smoothing = 100,
  defaultActive = null,
  onItemClick,
  className = ''
}) => {
  const listRef = useRef(null);
  const itemRefs = useRef([]);
  const targetsRef = useRef([]);
  const currentRef = useRef([]);
  const rafRef = useRef(null);
  const lastRef = useRef(0);
  const activeRef = useRef(defaultActive);
  const smoothingRef = useRef(smoothing);
  const [activeIndex, setActiveIndex] = useState(defaultActive);

  activeRef.current = activeIndex;
  smoothingRef.current = smoothing;

  const runFrame = useCallback(now => {
    const dt = Math.min((now - lastRef.current) / 1000, 0.05);
    lastRef.current = now;
    const tau = Math.max(smoothingRef.current, 1) / 1000;
    const k = 1 - Math.exp(-dt / tau);

    let moving = false;
    const items = itemRefs.current;
    for (let i = 0; i < items.length; i++) {
      const el = items[i];
      if (!el) continue;
      const target = Math.max(targetsRef.current[i] || 0, activeRef.current === i ? 1 : 0);
      const cur = currentRef.current[i] || 0;
      const next = cur + (target - cur) * k;
      const settled = Math.abs(target - next) < 0.0015;
      const value = settled ? target : next;
      currentRef.current[i] = value;
      el.style.setProperty('--effect', value.toFixed(4));
      if (!settled) moving = true;
    }

    rafRef.current = moving ? requestAnimationFrame(runFrame) : null;
  }, []);

  const startLoop = useCallback(() => {
    if (rafRef.current != null) return;
    lastRef.current = performance.now();
    rafRef.current = requestAnimationFrame(runFrame);
  }, [runFrame]);

  const handlePointerMove = useCallback(
    e => {
      const list = listRef.current;
      if (!list) return;
      const rect = list.getBoundingClientRect();
      const pointerY = e.clientY - rect.top;
      const ease = FALLOFF_CURVES[falloff] ?? FALLOFF_CURVES.linear;
      const items = itemRefs.current;
      for (let i = 0; i < items.length; i++) {
        const el = items[i];
        if (!el) continue;
        const center = el.offsetTop + el.offsetHeight / 2;
        const distance = Math.abs(pointerY - center);
        targetsRef.current[i] = ease(Math.max(0, 1 - distance / proximityRadius));
      }
      startLoop();
    },
    [falloff, proximityRadius, startLoop]
  );

  const handlePointerLeave = useCallback(() => {
    targetsRef.current = targetsRef.current.map(() => 0);
    startLoop();
  }, [startLoop]);

  const handleClick = useCallback(
    (index, label) => {
      setActiveIndex(index);
      onItemClick?.(index, label);
    },
    [onItemClick]
  );

  useEffect(() => {
    startLoop();
  }, [activeIndex, startLoop]);

  useEffect(
    () => () => {
      if (rafRef.current != null) cancelAnimationFrame(rafRef.current);
    },
    []
  );

  return (
    <nav
      className={`line-sidebar${showMarker ? ' line-sidebar--markers' : ''}${scaleTick ? ' line-sidebar--scale-tick' : ''}${className ? ` ${className}` : ''}`}
      style={{
        '--accent-color': accentColor,
        '--text-color': textColor,
        '--marker-color': markerColor,
        '--marker-length': `${markerLength}px`,
        '--marker-gap': `${markerGap}px`,
        '--tick-scale': tickScale,
        '--max-shift': `${maxShift}px`,
        '--item-gap': `${itemGap}px`,
        '--font-size': `${fontSize}rem`,
        '--smoothing': `${smoothing}ms`
      }}
    >
      <ul ref={listRef} className="line-sidebar__list" onPointerMove={handlePointerMove} onPointerLeave={handlePointerLeave}>
        {items.map((label, index) => (
          <li
            key={`${label}-${index}`}
            ref={el => {
              itemRefs.current[index] = el;
            }}
            className="line-sidebar__item"
            aria-current={activeIndex === index ? 'true' : undefined}
            onClick={() => handleClick(index, label)}
          >
            {showMarker && <span className="line-sidebar__marker" aria-hidden="true" />}
            <span className="line-sidebar__label">
              {showIndex && <span className="line-sidebar__index">{String(index + 1).padStart(2, '0')}</span>}
              <span className="line-sidebar__text">{label}</span>
            </span>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default LineSidebar;
```

### `src/components/LineSidebar.css`

```css
.line-sidebar {
  --accent-color: #3f7cb8;
  --text-color: #4d6a85;
  --marker-color: #bcdcf7;
  --marker-length: 44px;
  --marker-gap: 0px;
  --tick-scale: 0.5;
  --max-shift: 24px;
  --item-gap: 22px;
  --font-size: 0.95rem;
  --smoothing: 100ms;

  position: relative;
  display: flex;
  justify-content: flex-start;
}

.line-sidebar--markers {
  padding-left: calc(var(--marker-length) + var(--marker-gap));
}

.line-sidebar__list {
  list-style: none;
  margin: 0;
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: var(--item-gap);
}

.line-sidebar__item {
  position: relative;
  cursor: pointer;
}

.line-sidebar__item::before {
  content: '';
  position: absolute;
  inset: -6px -20px;
}

.line-sidebar__label {
  position: relative;
  display: inline-flex;
  align-items: baseline;
  font-family: var(--font-body, 'IBM Plex Sans', sans-serif);
  font-size: var(--font-size);
  line-height: 1.2;
  color: color-mix(in srgb, var(--accent-color) calc(var(--effect, 0) * 100%), var(--text-color));
  transform: translateX(calc(var(--effect, 0) * var(--max-shift)));
}

.line-sidebar__index {
  font-family: var(--font-mono, ui-monospace, monospace);
  margin-right: 0.55rem;
  font-size: 0.8em;
  opacity: calc(0.5 + var(--effect, 0) * 0.5);
}

.line-sidebar__marker {
  position: absolute;
  top: 50%;
  left: calc(-1 * var(--marker-length) - var(--marker-gap));
  height: 1px;
  width: var(--marker-length);
  background-color: color-mix(in srgb, var(--accent-color) calc(var(--effect, 0) * 100%), var(--marker-color));
  transform-origin: left center;
  transform: translateY(-50%) scaleX(calc(0.7 + var(--effect, 0) * 0.5));
}

.line-sidebar--markers .line-sidebar__item:not(:last-child)::after {
  content: '';
  position: absolute;
  top: calc(100% + var(--item-gap) / 2);
  left: calc(-1 * var(--marker-length) - var(--marker-gap));
  height: 1px;
  width: calc(var(--marker-length) * var(--tick-scale));
  background-color: var(--marker-color);
  opacity: 0.6;
  transform: translateY(-50%);
}

.line-sidebar--scale-tick .line-sidebar__item:not(:last-child)::after {
  transform-origin: left center;
  transform: translateY(-50%) scaleX(calc(0.7 + var(--effect, 0) * 0.6));
}
```

### `src/components/CardNav.jsx`

```jsx
import { useLayoutEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import './CardNav.css';

const ArrowIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true" className="nav-card-link-icon">
    <path d="M7 17L17 7M17 7H9M17 7V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

/**
 * items: [{ label, bgColor, textColor, links: [{ label, ariaLabel, onClick }] }]
 * onNavigate(pageId) is called (via each link's onClick) to switch the active page.
 */
const CardNav = ({
  logoText = 'Exam Leak Tracker',
  items,
  className = '',
  ease = 'power3.out',
  baseColor = '#ffffff',
  menuColor = '#16283b',
  ctaLabel,
  onCtaClick
}) => {
  const [isHamburgerOpen, setIsHamburgerOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const navRef = useRef(null);
  const cardsRef = useRef([]);
  const tlRef = useRef(null);

  const calculateHeight = () => {
    const navEl = navRef.current;
    if (!navEl) return 260;

    const isMobile = window.matchMedia('(max-width: 768px)').matches;
    if (isMobile) {
      const contentEl = navEl.querySelector('.card-nav-content');
      if (contentEl) {
        const wasVisible = contentEl.style.visibility;
        const wasPointerEvents = contentEl.style.pointerEvents;
        const wasPosition = contentEl.style.position;
        const wasHeight = contentEl.style.height;

        contentEl.style.visibility = 'visible';
        contentEl.style.pointerEvents = 'auto';
        contentEl.style.position = 'static';
        contentEl.style.height = 'auto';

        contentEl.offsetHeight;

        const topBar = 60;
        const padding = 16;
        const contentHeight = contentEl.scrollHeight;

        contentEl.style.visibility = wasVisible;
        contentEl.style.pointerEvents = wasPointerEvents;
        contentEl.style.position = wasPosition;
        contentEl.style.height = wasHeight;

        return topBar + contentHeight + padding;
      }
    }
    return 220;
  };

  const createTimeline = () => {
    const navEl = navRef.current;
    if (!navEl) return null;

    gsap.set(navEl, { height: 60, overflow: 'hidden' });
    gsap.set(cardsRef.current, { y: 50, opacity: 0 });

    const tl = gsap.timeline({ paused: true });
    tl.to(navEl, { height: calculateHeight, duration: 0.4, ease });
    tl.to(cardsRef.current, { y: 0, opacity: 1, duration: 0.4, ease, stagger: 0.08 }, '-=0.1');
    return tl;
  };

  useLayoutEffect(() => {
    const tl = createTimeline();
    tlRef.current = tl;
    return () => {
      tl?.kill();
      tlRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ease, items]);

  useLayoutEffect(() => {
    const handleResize = () => {
      if (!tlRef.current) return;
      if (isExpanded) {
        const newHeight = calculateHeight();
        gsap.set(navRef.current, { height: newHeight });
        tlRef.current.kill();
        const newTl = createTimeline();
        if (newTl) {
          newTl.progress(1);
          tlRef.current = newTl;
        }
      } else {
        tlRef.current.kill();
        const newTl = createTimeline();
        if (newTl) tlRef.current = newTl;
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isExpanded]);

  const toggleMenu = () => {
    const tl = tlRef.current;
    if (!tl) return;
    if (!isExpanded) {
      setIsHamburgerOpen(true);
      setIsExpanded(true);
      tl.play(0);
    } else {
      setIsHamburgerOpen(false);
      tl.eventCallback('onReverseComplete', () => setIsExpanded(false));
      tl.reverse();
    }
  };

  const closeMenu = () => {
    const tl = tlRef.current;
    if (!tl || !isExpanded) return;
    setIsHamburgerOpen(false);
    tl.eventCallback('onReverseComplete', () => setIsExpanded(false));
    tl.reverse();
  };

  const setCardRef = i => el => {
    if (el) cardsRef.current[i] = el;
  };

  return (
    <div className={`card-nav-container ${className}`}>
      <nav ref={navRef} className={`card-nav ${isExpanded ? 'open' : ''}`} style={{ backgroundColor: baseColor }}>
        <div className="card-nav-top">
          <div
            className={`hamburger-menu ${isHamburgerOpen ? 'open' : ''}`}
            onClick={toggleMenu}
            onKeyDown={e => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleMenu();
              }
            }}
            role="button"
            aria-label={isExpanded ? 'Close menu' : 'Open menu'}
            aria-expanded={isExpanded}
            tabIndex={0}
            style={{ color: menuColor }}
          >
            <div className="hamburger-line" />
            <div className="hamburger-line" />
          </div>

          <div className="logo-container">
            <span className="logo-text">{logoText}</span>
          </div>

          {ctaLabel ? (
            <button type="button" className="card-nav-cta-button" onClick={onCtaClick}>
              {ctaLabel}
            </button>
          ) : (
            <span className="card-nav-spacer" aria-hidden="true" />
          )}
        </div>

        <div className="card-nav-content" aria-hidden={!isExpanded}>
          {(items || []).slice(0, 3).map((item, idx) => (
            <div
              key={`${item.label}-${idx}`}
              className="nav-card"
              ref={setCardRef(idx)}
              style={{ backgroundColor: item.bgColor, color: item.textColor }}
            >
              <div className="nav-card-label">{item.label}</div>
              <div className="nav-card-links">
                {item.links?.map((lnk, i) => (
                  <a
                    key={`${lnk.label}-${i}`}
                    className="nav-card-link"
                    aria-label={lnk.ariaLabel}
                    onClick={() => {
                      lnk.onClick?.();
                      closeMenu();
                    }}
                  >
                    <ArrowIcon />
                    {lnk.label}
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>
      </nav>
    </div>
  );
};

export default CardNav;
```

### `src/components/CardNav.css`

```css
.card-nav-container {
  position: fixed;
  top: 1.1em;
  left: 50%;
  transform: translateX(-50%);
  width: 92%;
  max-width: 760px;
  z-index: 50;
  box-sizing: border-box;
}

.card-nav {
  display: block;
  height: 58px;
  padding: 0;
  background-color: #ffffff;
  border: 1px solid var(--border-strong, #bcdcf7);
  border-radius: 1rem;
  box-shadow: 0 8px 24px rgba(63, 124, 184, 0.14);
  position: relative;
  overflow: hidden;
  will-change: height;
}

.card-nav-top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.5rem 0.5rem 1.1rem;
  z-index: 2;
}

.hamburger-menu {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  gap: 5px;
}

.hamburger-menu:hover .hamburger-line {
  opacity: 0.7;
}

.hamburger-line {
  width: 22px;
  height: 2px;
  background-color: currentColor;
  transition: transform 0.25s ease, opacity 0.2s ease, margin 0.3s ease;
  transform-origin: 50% 50%;
}

.hamburger-menu.open .hamburger-line:first-child {
  transform: translateY(3.5px) rotate(45deg);
}
.hamburger-menu.open .hamburger-line:last-child {
  transform: translateY(-3.5px) rotate(-45deg);
}

.logo-container {
  display: flex;
  align-items: center;
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}

.logo-text {
  font-family: var(--font-display, 'Fraunces', serif);
  font-weight: 600;
  font-size: 1.02rem;
  color: var(--text-primary, #16283b);
  white-space: nowrap;
}

.card-nav-cta-button {
  background-color: var(--accent-deep, #3f7cb8);
  color: #fff;
  border: none;
  border-radius: 0.6rem;
  padding: 0 1rem;
  height: 100%;
  font-family: var(--font-body, sans-serif);
  font-weight: 500;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.card-nav-cta-button:hover {
  background-color: var(--accent, #6fa8dc);
}

.card-nav-spacer {
  width: 22px;
  height: 100%;
}

.card-nav-content {
  position: absolute;
  left: 0;
  right: 0;
  top: 58px;
  bottom: 0;
  padding: 0.5rem;
  display: flex;
  align-items: flex-end;
  gap: 10px;
  visibility: hidden;
  pointer-events: none;
  z-index: 1;
}

.card-nav.open .card-nav-content {
  visibility: visible;
  pointer-events: auto;
}

.nav-card {
  height: 100%;
  flex: 1 1 0;
  min-width: 0;
  border-radius: 0.7rem;
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 0.9rem 1rem;
  gap: 6px;
  user-select: none;
}

.nav-card-label {
  font-family: var(--font-display, 'Fraunces', serif);
  font-weight: 500;
  font-size: 1.2rem;
  letter-spacing: -0.02em;
}

.nav-card-links {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.nav-card-link {
  font-family: var(--font-body, sans-serif);
  font-size: 0.85rem;
  cursor: pointer;
  text-decoration: none;
  transition: opacity 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.nav-card-link:hover {
  opacity: 0.7;
}
.nav-card-link-icon {
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .card-nav-container {
    width: 94%;
    top: 0.8em;
  }
  .card-nav-content {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    padding: 0.5rem;
    bottom: 0;
    justify-content: flex-start;
  }
  .nav-card {
    height: auto;
    min-height: 56px;
    flex: 1 1 auto;
    max-height: none;
  }
  .nav-card-label {
    font-size: 1.05rem;
  }
  .nav-card-link {
    font-size: 0.82rem;
  }
  .logo-text {
    font-size: 0.9rem;
  }
}
```

### `src/components/CardSwap.jsx`

```jsx
import React, { Children, cloneElement, forwardRef, isValidElement, useEffect, useMemo, useRef } from 'react';
import gsap from 'gsap';
import './CardSwap.css';

export const Card = forwardRef(({ customClass, ...rest }, ref) => (
  <div ref={ref} {...rest} className={`card ${customClass ?? ''} ${rest.className ?? ''}`.trim()} />
));
Card.displayName = 'Card';

const makeSlot = (i, distX, distY, total) => ({
  x: i * distX,
  y: -i * distY,
  z: -i * distX * 1.5,
  zIndex: total - i
});
const placeNow = (el, slot, skew) =>
  gsap.set(el, {
    x: slot.x,
    y: slot.y,
    z: slot.z,
    xPercent: -50,
    yPercent: -50,
    skewY: skew,
    transformOrigin: 'center center',
    zIndex: slot.zIndex,
    force3D: true
  });

const CardSwap = ({
  width = 400,
  height = 300,
  cardDistance = 46,
  verticalDistance = 54,
  delay = 3800,
  pauseOnHover = true,
  onCardClick,
  skewAmount = 5,
  easing = 'elastic',
  children
}) => {
  const config =
    easing === 'elastic'
      ? { ease: 'elastic.out(0.6,0.9)', durDrop: 2, durMove: 2, durReturn: 2, promoteOverlap: 0.9, returnDelay: 0.05 }
      : { ease: 'power1.inOut', durDrop: 0.8, durMove: 0.8, durReturn: 0.8, promoteOverlap: 0.45, returnDelay: 0.2 };

  const childArr = useMemo(() => Children.toArray(children), [children]);
  const refs = useMemo(
    () => childArr.map(() => React.createRef()),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [childArr.length]
  );

  const order = useRef(Array.from({ length: childArr.length }, (_, i) => i));
  const tlRef = useRef(null);
  const intervalRef = useRef();
  const container = useRef(null);

  useEffect(() => {
    const total = refs.length;
    if (total === 0) return;
    refs.forEach((r, i) => placeNow(r.current, makeSlot(i, cardDistance, verticalDistance, total), skewAmount));

    const swap = () => {
      if (order.current.length < 2) return;
      const [front, ...rest] = order.current;
      const elFront = refs[front].current;
      const tl = gsap.timeline();
      tlRef.current = tl;

      tl.to(elFront, { y: '+=420', duration: config.durDrop, ease: config.ease });
      tl.addLabel('promote', `-=${config.durDrop * config.promoteOverlap}`);
      rest.forEach((idx, i) => {
        const el = refs[idx].current;
        const slot = makeSlot(i, cardDistance, verticalDistance, refs.length);
        tl.set(el, { zIndex: slot.zIndex }, 'promote');
        tl.to(el, { x: slot.x, y: slot.y, z: slot.z, duration: config.durMove, ease: config.ease }, `promote+=${i * 0.15}`);
      });

      const backSlot = makeSlot(refs.length - 1, cardDistance, verticalDistance, refs.length);
      tl.addLabel('return', `promote+=${config.durMove * config.returnDelay}`);
      tl.call(() => gsap.set(elFront, { zIndex: backSlot.zIndex }), undefined, 'return');
      tl.to(elFront, { x: backSlot.x, y: backSlot.y, z: backSlot.z, duration: config.durReturn, ease: config.ease }, 'return');
      tl.call(() => {
        order.current = [...rest, front];
      });
    };

    swap();
    intervalRef.current = window.setInterval(swap, delay);

    if (pauseOnHover) {
      const node = container.current;
      const pause = () => {
        tlRef.current?.pause();
        clearInterval(intervalRef.current);
      };
      const resume = () => {
        tlRef.current?.play();
        intervalRef.current = window.setInterval(swap, delay);
      };
      node.addEventListener('mouseenter', pause);
      node.addEventListener('mouseleave', resume);
      return () => {
        node.removeEventListener('mouseenter', pause);
        node.removeEventListener('mouseleave', resume);
        clearInterval(intervalRef.current);
      };
    }
    return () => clearInterval(intervalRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cardDistance, verticalDistance, delay, pauseOnHover, skewAmount, easing, refs.length]);

  const rendered = childArr.map((child, i) =>
    isValidElement(child)
      ? cloneElement(child, {
          key: i,
          ref: refs[i],
          style: { width, height, ...(child.props.style ?? {}) },
          onClick: e => {
            child.props.onClick?.(e);
            onCardClick?.(i);
          }
        })
      : child
  );

  return (
    <div ref={container} className="card-swap-container" style={{ width, height }}>
      {rendered}
    </div>
  );
};

export default CardSwap;
```

### `src/components/CardSwap.css`

```css
.card-swap-container {
  position: relative;
  margin: 0 auto;
  transform-origin: center center;
  perspective: 900px;
  overflow: visible;
}

.card {
  position: absolute;
  top: 50%;
  left: 50%;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(155deg, #1b3350 0%, #16283b 100%);
  color: #eaf3fc;
  padding: 1.6rem 1.7rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 20px 45px rgba(22, 40, 59, 0.35);

  transform-style: preserve-3d;
  will-change: transform;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

.card .source-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-family: var(--font-mono, monospace);
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #9cc2e8;
  background: rgba(111, 168, 220, 0.14);
  border: 1px solid rgba(111, 168, 220, 0.3);
  padding: 0.3rem 0.6rem;
  border-radius: 999px;
  width: fit-content;
}

.card .source-name {
  font-family: var(--font-display, 'Fraunces', serif);
  font-size: 1.6rem;
  font-weight: 600;
  margin: 0.9rem 0 0.4rem;
  line-height: 1.15;
}

.card .source-note {
  font-family: var(--font-body, sans-serif);
  font-size: 0.85rem;
  color: #b9cee2;
  line-height: 1.5;
}

@media (max-width: 640px) {
  .card-swap-container {
    transform: scale(0.82);
  }
}
```

### `src/components/ChartCanvas.jsx`

```jsx
import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

const PALETTE = ['#6fa8dc', '#a7c9ea', '#3f7cb8', '#cfe6fb', '#8fb8dd', '#274a68'];

Chart.defaults.font.family = "'IBM Plex Sans', sans-serif";
Chart.defaults.color = '#4d6a85';
Chart.defaults.borderColor = '#e3eefa';

/**
 * type: 'bar' | 'line' | 'doughnut' | 'bar-horizontal'
 * data: Chart.js-style { labels, datasets }
 */
const ChartCanvas = ({ type, data, options = {}, height = 220 }) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const resolvedType = type === 'bar-horizontal' ? 'bar' : type;
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: type === 'bar-horizontal' ? 'y' : 'x',
      plugins: {
        legend: {
          display: type === 'doughnut',
          position: 'bottom',
          labels: { boxWidth: 10, padding: 12, font: { size: 11 } }
        },
        tooltip: {
          backgroundColor: '#16283b',
          titleFont: { family: "'IBM Plex Sans', sans-serif" },
          bodyFont: { family: "'IBM Plex Mono', monospace" },
          padding: 10,
          cornerRadius: 8
        }
      },
      scales:
        type === 'doughnut'
          ? undefined
          : {
              x: { grid: { display: type === 'bar-horizontal' }, ticks: { font: { size: 11 } } },
              y: { grid: { color: '#eef6ff' }, ticks: { font: { size: 11 } }, beginAtZero: true }
            }
    };

    chartRef.current = new Chart(canvasRef.current, {
      type: resolvedType,
      data,
      options: { ...baseOptions, ...options }
    });

    return () => chartRef.current?.destroy();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [type, JSON.stringify(data), JSON.stringify(options)]);

  return (
    <div style={{ position: 'relative', height, width: '100%' }}>
      <canvas ref={canvasRef} />
    </div>
  );
};

export { PALETTE };
export default ChartCanvas;
```

### `src/components/CardHeader.jsx`

```jsx
const CardHeader = ({ eyebrow, title, caveat }) => (
  <div style={{ marginBottom: '0.85rem', position: 'relative', zIndex: 3 }}>
    {eyebrow && (
      <p
        className="mono"
        style={{ fontSize: '0.7rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--accent-deep)', margin: '0 0 0.2rem' }}
      >
        {eyebrow}
      </p>
    )}
    <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>{title}</h3>
    {caveat && <p style={{ fontSize: '0.78rem', marginTop: '0.3rem', color: 'var(--text-muted)' }}>{caveat}</p>}
  </div>
);

export default CardHeader;
```

### `src/components/DataTable.jsx`

```jsx
import { Fragment, useMemo, useState } from 'react';

const COLUMNS = [
  { key: 'date', label: 'Date' },
  { key: 'exam_name', label: 'Exam' },
  { key: 'body_type', label: 'Body' },
  { key: 'area', label: 'Area' },
  { key: 'leak_status', label: 'Status' },
  { key: 'confidence', label: 'Confidence' }
];

const PAGE_SIZE = 20;

const statusColor = status => {
  switch (status) {
    case 'Confirmed':
      return 'var(--confirmed)';
    case 'Alleged':
      return 'var(--alleged)';
    case 'Denied':
      return 'var(--denied)';
    default:
      return 'var(--suspected)';
  }
};

const DataTable = ({ rows }) => {
  const [query, setQuery] = useState('');
  const [sortKey, setSortKey] = useState('date');
  const [sortDir, setSortDir] = useState('desc');
  const [visible, setVisible] = useState(PAGE_SIZE);
  const [expanded, setExpanded] = useState(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let out = rows;
    if (q) {
      out = rows.filter(r =>
        [r.exam_name, r.area, r.conducting_body, r.note].join(' ').toLowerCase().includes(q)
      );
    }
    out = [...out].sort((a, b) => {
      const av = a[sortKey] ?? '';
      const bv = b[sortKey] ?? '';
      const cmp = String(av).localeCompare(String(bv));
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return out;
  }, [rows, query, sortKey, sortDir]);

  const toggleSort = key => {
    if (key === sortKey) {
      setSortDir(d => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  return (
    <div style={{ position: 'relative', zIndex: 3 }}>
      <div style={{ display: 'flex', gap: '0.6rem', marginBottom: '0.9rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Search exam, state, or body..."
          value={query}
          onChange={e => {
            setQuery(e.target.value);
            setVisible(PAGE_SIZE);
          }}
          style={{
            flex: '1 1 240px',
            padding: '0.5rem 0.75rem',
            borderRadius: 8,
            border: '1px solid var(--border-strong)',
            fontFamily: 'var(--font-body)',
            fontSize: '0.85rem',
            background: 'var(--surface-soft)',
            color: 'var(--text-primary)'
          }}
        />
        <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          {filtered.length} of {rows.length} incidents
        </span>
      </div>

      <div style={{ overflowX: 'auto', border: '1px solid var(--border)', borderRadius: 12 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
          <thead>
            <tr style={{ background: 'var(--bg-deep)' }}>
              {COLUMNS.map(col => (
                <th
                  key={col.key}
                  onClick={() => toggleSort(col.key)}
                  style={{
                    textAlign: 'left',
                    padding: '0.6rem 0.75rem',
                    cursor: 'pointer',
                    userSelect: 'none',
                    color: 'var(--text-secondary)',
                    fontWeight: 600,
                    whiteSpace: 'nowrap'
                  }}
                >
                  {col.label}
                  {sortKey === col.key ? (sortDir === 'asc' ? ' \u2191' : ' \u2193') : ''}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, visible).map(r => (
              <Fragment key={r.id}>
                <tr
                  key={r.id}
                  onClick={() => setExpanded(expanded === r.id ? null : r.id)}
                  style={{ borderTop: '1px solid var(--border)', cursor: 'pointer' }}
                >
                  <td className="mono" style={{ padding: '0.55rem 0.75rem', whiteSpace: 'nowrap', color: 'var(--text-muted)' }}>
                    {r.date}
                  </td>
                  <td style={{ padding: '0.55rem 0.75rem', maxWidth: 280 }}>{r.exam_name}</td>
                  <td style={{ padding: '0.55rem 0.75rem' }}>{r.body_type}</td>
                  <td style={{ padding: '0.55rem 0.75rem' }}>{r.area}</td>
                  <td style={{ padding: '0.55rem 0.75rem' }}>
                    <span
                      style={{
                        display: 'inline-block',
                        padding: '0.15rem 0.55rem',
                        borderRadius: 999,
                        fontSize: '0.72rem',
                        color: '#fff',
                        background: statusColor(r.leak_status)
                      }}
                    >
                      {r.leak_status}
                    </span>
                  </td>
                  <td style={{ padding: '0.55rem 0.75rem', color: 'var(--text-muted)' }}>{r.confidence}</td>
                </tr>
                {expanded === r.id && (
                  <tr key={`${r.id}-detail`} style={{ background: 'var(--bg-deep)' }}>
                    <td colSpan={COLUMNS.length} style={{ padding: '0.9rem 1rem', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                      <p style={{ marginBottom: '0.5rem' }}>{r.note}</p>
                      <p className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        Conducting body: {r.conducting_body} · Arrests: {r.arrests || '—'} · Convictions: {r.convictions || '—'} ·
                        Aspirants affected: {r.aspirants_affected ? Number(r.aspirants_affected).toLocaleString('en-IN') : '—'}
                      </p>
                      <p style={{ marginTop: '0.4rem' }}>
                        Source:{' '}
                        <a href={r.source_url} target="_blank" rel="noreferrer">
                          {r.source_name}
                        </a>
                      </p>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {visible < filtered.length && (
        <button
          onClick={() => setVisible(v => v + PAGE_SIZE)}
          style={{
            marginTop: '0.8rem',
            padding: '0.5rem 1rem',
            borderRadius: 8,
            border: '1px solid var(--border-strong)',
            background: 'var(--surface-soft)',
            color: 'var(--accent-deep)',
            fontFamily: 'var(--font-body)',
            fontSize: '0.82rem',
            cursor: 'pointer'
          }}
        >
          Show {Math.min(PAGE_SIZE, filtered.length - visible)} more
        </button>
      )}
    </div>
  );
};

export default DataTable;
```

### `src/components/DisclaimerModal.jsx`

```jsx
import { useState } from 'react';

const DisclaimerModal = () => {
  const [open, setOpen] = useState(true);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="disclaimer-title"
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(22, 40, 59, 0.45)',
        backdropFilter: 'blur(2px)',
        zIndex: 200,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.2rem'
      }}
    >
      <div
        style={{
          background: 'var(--surface)',
          borderRadius: 18,
          border: '1px solid var(--border)',
          maxWidth: 460,
          width: '100%',
          padding: '1.6rem 1.6rem 1.4rem',
          boxShadow: '0 30px 70px rgba(22, 40, 59, 0.3)'
        }}
      >
        <p className="mono" style={{ fontSize: '0.7rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--accent-deep)', marginBottom: '0.4rem' }}>
          Before you dig in
        </p>
        <h2 id="disclaimer-title" style={{ fontSize: '1.25rem', marginBottom: '0.7rem' }}>
          Compiled with AI assistance
        </h2>
        <p style={{ fontSize: '0.88rem', marginBottom: '0.7rem' }}>
          This dataset and dashboard were researched and assembled with the help of an AI assistant (Claude), drawing
          on openly published news articles, government statements, and retrospective reports.
        </p>
        <p style={{ fontSize: '0.88rem', marginBottom: '1.1rem' }}>
          Some entries are confirmed by courts or official probes; others are allegations that were later disputed,
          denied, or never conclusively resolved. Confidence levels are noted per incident, but nothing here should be
          treated as a verified legal record. Please cross-check anything decision-critical against the linked
          primary sources.
        </p>
        <button
          onClick={() => setOpen(false)}
          style={{
            width: '100%',
            padding: '0.65rem',
            borderRadius: 10,
            border: 'none',
            background: 'var(--accent-deep)',
            color: '#fff',
            fontFamily: 'var(--font-body)',
            fontSize: '0.9rem',
            fontWeight: 500,
            cursor: 'pointer'
          }}
        >
          Understood, continue
        </button>
      </div>
    </div>
  );
};

export default DisclaimerModal;
```

### `src/pages/ChartsPage.jsx`

```jsx
import MagicBento from '../components/MagicBento.jsx';
import LineSidebar from '../components/LineSidebar.jsx';
import ChartCanvas, { PALETTE } from '../components/ChartCanvas.jsx';
import CardHeader from '../components/CardHeader.jsx';
import data from '../data/leaks.json';

const SECTION_IDS = ['kpis', 'trend', 'eras', 'body-type', 'leak-status', 'top-exams', 'top-states', 'actions'];
const SECTION_LABELS = ['Overview', 'Yearly trend', 'By administration', 'Central vs state', 'Leak status', 'Top exams', 'Top states', 'Actions taken'];

const KpiCard = ({ label, value }) => (
  <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 14, padding: '1rem 1.1rem' }}>
    <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>{label}</p>
    <p className="mono" style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--text-primary)' }}>{value}</p>
  </div>
);

const ChartsPage = () => {
  const { kpis, yearly_counts, era_data, body_type_counts, leak_status_counts, action_data, top_states, top_exams } = data;

  const yearlyTrend = {
    labels: Object.keys(yearly_counts),
    datasets: [{ label: 'Incidents', data: Object.values(yearly_counts), backgroundColor: '#a7c9ea', borderColor: '#3f7cb8', borderRadius: 4 }]
  };

  const eraChart = {
    labels: era_data.map(e => e.pm),
    datasets: [
      { label: 'Incidents per year in office', data: era_data.map(e => e.rate_per_year), backgroundColor: PALETTE, borderRadius: 6 }
    ]
  };

  const bodyTypeChart = {
    labels: Object.keys(body_type_counts),
    datasets: [{ data: Object.values(body_type_counts), backgroundColor: ['#6fa8dc', '#cfe6fb'] }]
  };

  const leakStatusChart = {
    labels: Object.keys(leak_status_counts),
    datasets: [{ data: Object.values(leak_status_counts), backgroundColor: ['#4f8fce', '#9cc2e8', '#e3b8a0', '#c9d6e3'] }]
  };

  const actionChart = {
    labels: action_data.map(a => a.label),
    datasets: [{ label: 'Incidents', data: action_data.map(a => a.count), backgroundColor: '#8fb8dd', borderRadius: 4 }]
  };

  const topExamsChart = {
    labels: top_exams.map(e => (e.exam_name.length > 34 ? e.exam_name.slice(0, 34) + '…' : e.exam_name)),
    datasets: [{ label: 'Aspirants affected', data: top_exams.map(e => e.aspirants_affected), backgroundColor: '#6fa8dc', borderRadius: 4 }]
  };

  const topStatesChart = {
    labels: top_states.map(s => s.state),
    datasets: [{ label: 'Incidents', data: top_states.map(s => s.count), backgroundColor: '#a7c9ea', borderRadius: 4 }]
  };

  const cards = [
    {
      id: 'trend',
      size: 'wide',
      content: (
        <>
          <CardHeader eyebrow="2000–2026" title="Leaks per year" caveat="COVID-era dips likely reflect fewer exams held, not fewer leaks." />
          <ChartCanvas type="bar" data={yearlyTrend} height={240} />
        </>
      )
    },
    {
      id: 'eras',
      content: (
        <>
          <CardHeader eyebrow="Normalized" title="Incidents per year in office" caveat="Raw totals would mislead — these three terms cover very different lengths of time." />
          <ChartCanvas type="bar-horizontal" data={eraChart} height={200} />
        </>
      )
    },
    {
      id: 'body-type',
      content: (
        <>
          <CardHeader eyebrow="Scope" title="Central vs. state bodies" caveat="Counts incidents, not exams held — central bodies run far fewer, larger exams." />
          <ChartCanvas type="doughnut" data={bodyTypeChart} height={200} />
        </>
      )
    },
    {
      id: 'leak-status',
      content: (
        <>
          <CardHeader eyebrow="Verification" title="Confirmed, alleged, denied" caveat="A meaningful share were later denied or downgraded by investigators." />
          <ChartCanvas type="doughnut" data={leakStatusChart} height={200} />
        </>
      )
    },
    {
      id: 'top-exams',
      content: (
        <>
          <CardHeader eyebrow="Where known" title="Top exams by aspirants affected" caveat="Many rows have no public estimate — this ranks reported numbers, not true scale." />
          <ChartCanvas type="bar-horizontal" data={topExamsChart} height={230} />
        </>
      )
    },
    {
      id: 'top-states',
      content: (
        <>
          <CardHeader eyebrow="Geography" title="Top states by incident count" caveat="Likely reflects reporting intensity as much as underlying leak frequency." />
          <ChartCanvas type="bar-horizontal" data={topStatesChart} height={230} />
        </>
      )
    },
    {
      id: 'actions',
      size: 'wide',
      content: (
        <>
          <CardHeader eyebrow="Response" title="Action taken breakdown" caveat="Parsed from a free-text field — treat as an approximate categorization." />
          <ChartCanvas type="bar" data={actionChart} height={220} />
        </>
      )
    }
  ];

  return (
    <section style={{ maxWidth: 1080, margin: '0 auto', padding: '0 1.2rem 3rem' }}>
      <div id="kpis">
        <p className="mono" style={{ fontSize: '0.7rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--accent-deep)' }}>
          Charts
        </p>
        <h1 style={{ fontSize: 'clamp(1.5rem, 4vw, 2rem)', marginBottom: '0.4rem' }}>India exam leak tracker, 2000–2026</h1>
        <p style={{ fontSize: '0.9rem', marginBottom: '1.2rem', maxWidth: 640 }}>
          {kpis.total_incidents} incidents logged. Not exhaustive — see the About tab for what this dataset does and doesn't capture.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.8rem', marginBottom: '1.6rem' }}>
          <KpiCard label="Total incidents" value={kpis.total_incidents} />
          <KpiCard label="Confirmed" value={`${kpis.confirmed_pct}%`} />
          <KpiCard label="Total arrests" value={kpis.total_arrests.toLocaleString('en-IN')} />
          <KpiCard label="States / UTs hit" value={kpis.distinct_states} />
        </div>
      </div>

      <MagicBento cards={cards} />

      <aside className="charts-sidebar" aria-label="Jump to chart section">
        <LineSidebar
          items={SECTION_LABELS}
          showIndex
          onItemClick={index => {
            document.getElementById(SECTION_IDS[index])?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }}
        />
      </aside>
    </section>
  );
};

export default ChartsPage;
```

### `src/pages/InfoPage.jsx`

```jsx
import { useMemo, useState } from 'react';
import DataTable from '../components/DataTable.jsx';

const Select = ({ label, value, onChange, options }) => (
  <label style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
    {label}
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      style={{
        padding: '0.45rem 0.6rem',
        borderRadius: 8,
        border: '1px solid var(--border-strong)',
        background: 'var(--surface-soft)',
        color: 'var(--text-primary)',
        fontFamily: 'var(--font-body)',
        fontSize: '0.82rem'
      }}
    >
      <option value="">All</option>
      {options.map(o => (
        <option key={o} value={o}>
          {o}
        </option>
      ))}
    </select>
  </label>
);

const InfoPage = ({ rows }) => {
  const [status, setStatus] = useState('');
  const [bodyType, setBodyType] = useState('');
  const [pm, setPm] = useState('');
  const [confidence, setConfidence] = useState('');

  const statusOptions = useMemo(() => [...new Set(rows.map(r => r.leak_status))].sort(), [rows]);
  const bodyTypeOptions = useMemo(() => [...new Set(rows.map(r => r.body_type))].sort(), [rows]);
  const pmOptions = useMemo(() => [...new Set(rows.map(r => r.pm))], [rows]);
  const confidenceOptions = useMemo(() => [...new Set(rows.map(r => r.confidence))].sort(), [rows]);

  const filtered = useMemo(
    () =>
      rows.filter(
        r =>
          (!status || r.leak_status === status) &&
          (!bodyType || r.body_type === bodyType) &&
          (!pm || r.pm === pm) &&
          (!confidence || r.confidence === confidence)
      ),
    [rows, status, bodyType, pm, confidence]
  );

  const resetFilters = () => {
    setStatus('');
    setBodyType('');
    setPm('');
    setConfidence('');
  };

  return (
    <section style={{ maxWidth: 1080, margin: '0 auto', padding: '0 1.2rem' }}>
      <p className="mono" style={{ fontSize: '0.7rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--accent-deep)' }}>
        Info
      </p>
      <h1 style={{ fontSize: 'clamp(1.5rem, 4vw, 2rem)', marginBottom: '0.5rem' }}>Browse the raw dataset</h1>
      <p style={{ fontSize: '0.9rem', marginBottom: '1.2rem', maxWidth: 640 }}>
        Every row from the underlying CSV, filterable by status, conducting body, administration, and source
        confidence. Click any row to expand its full note and source link.
      </p>

      <div
        style={{
          display: 'flex',
          gap: '0.9rem',
          flexWrap: 'wrap',
          alignItems: 'flex-end',
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 14,
          padding: '1rem 1.1rem',
          marginBottom: '1.2rem'
        }}
      >
        <Select label="Leak status" value={status} onChange={setStatus} options={statusOptions} />
        <Select label="Conducting body" value={bodyType} onChange={setBodyType} options={bodyTypeOptions} />
        <Select label="Administration" value={pm} onChange={setPm} options={pmOptions} />
        <Select label="Confidence" value={confidence} onChange={setConfidence} options={confidenceOptions} />
        <button
          onClick={resetFilters}
          style={{
            padding: '0.5rem 0.9rem',
            borderRadius: 8,
            border: '1px solid var(--border-strong)',
            background: 'var(--surface-soft)',
            color: 'var(--accent-deep)',
            fontFamily: 'var(--font-body)',
            fontSize: '0.8rem',
            cursor: 'pointer'
          }}
        >
          Reset filters
        </button>
      </div>

      <DataTable rows={filtered} />
    </section>
  );
};

export default InfoPage;
```

### `src/pages/AboutPage.jsx`

```jsx
import CardSwap, { Card } from '../components/CardSwap.jsx';

const SOURCES = [
  { name: 'The Tribune', note: 'Contemporaneous reporting since 2004, plus the 2026 two-decade retrospective this project started from.' },
  { name: 'Careers360', note: 'The single largest source of incident-level detail: arrest counts, dates, and candidate numbers.' },
  { name: 'Newslaundry', note: 'Investigative analysis of ~89 leak cases over a decade, with party- and state-level breakdowns.' },
  { name: 'The Wire', note: 'In-depth coverage of the 2024 NEET-UG leak and its Supreme Court proceedings.' },
  { name: 'Press Trust of India (PTI)', note: 'Wire-service reporting syndicated across most Indian news outlets cited here.' },
  { name: 'ThePrint', note: 'Coverage of UPPSC, JPSC, and other state recruitment-exam leaks.' },
  { name: 'Deccan Herald', note: 'Archival coverage reaching back to some of the earliest 2000s-era incidents.' },
  { name: 'Wikipedia', note: 'Background on the Vyapam scam and the unfolding 2026 NEET controversy.' }
];

const AboutPage = () => (
  <section style={{ maxWidth: 1080, margin: '0 auto', padding: '0 1.2rem' }}>
    <div className="about-grid">
      <div className="about-text">
        <p className="mono" style={{ fontSize: '0.7rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--accent-deep)' }}>
          About
        </p>
        <h1 style={{ fontSize: 'clamp(1.6rem, 4vw, 2.3rem)', marginBottom: '0.9rem', lineHeight: 1.15 }}>
          Why this exists
        </h1>
        <p style={{ fontSize: '0.95rem', marginBottom: '0.9rem' }}>
          Exam paper leaks in India rarely get tracked in one place. Each one is covered locally, gets a news cycle,
          and then scatters across hundreds of state and national outlets. When the 2026 NEET-UG leak set off protests
          in Delhi, it became clear there was no single, browsable record of how often this has happened, to which
          exams, under which administrations, and with what consequences.
        </p>
        <p style={{ fontSize: '0.95rem', marginBottom: '0.9rem' }}>
          This project pulls that scattered coverage into one dataset: 129 incidents from 2000 to 2026, spanning
          national entrance exams, state recruitment tests, and school board exams. It leans on an AI research
          assistant to do the searching, cross-checking, and structuring at a scale that would take a person weeks
          to do by hand.
        </p>
        <p style={{ fontSize: '0.95rem', marginBottom: '0.9rem' }}>
          That speed comes with a real tradeoff: the underlying research was not independently fact-checked
          incident-by-incident against primary court records. Confidence levels are recorded per row, several
          allegations were later denied by investigators, and coverage skews toward whichever states and years have
          the most searchable English-language press. Treat this as a starting point for further reporting or
          research, not a definitive record.
        </p>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Every incident links back to its original source in the Info tab — that's the place to verify anything you
          plan to rely on.
        </p>
      </div>

      <div className="about-swap">
        <CardSwap width={300} height={230} cardDistance={40} verticalDistance={46} delay={3600} pauseOnHover>
          {SOURCES.map(s => (
            <Card key={s.name}>
              <span className="source-eyebrow">Source</span>
              <h3 className="source-name">{s.name}</h3>
              <p className="source-note">{s.note}</p>
            </Card>
          ))}
        </CardSwap>
      </div>
    </div>
  </section>
);

export default AboutPage;
```

---

## 7. Notes on the React Bits components

All four React Bits components (`LightRays`, `MagicBento`, `LineSidebar`, `CardNav`, `CardSwap`) keep their original animation logic (GSAP timelines, the WebGL ray shader, the proximity-based sidebar easing) unchanged. What changed is styling and integration:

- **LightRays**: `raysColor` defaults to pastel blue (`#bcdcf7`), and the container's CSS `z-index` was dropped from `3` to `0` so it always stays behind content when placed in the `.rays-backdrop` fixed wrapper.
- **MagicBento**: the original demo hardcoded six cards with a title/description/label. This version takes a `cards` prop (`{ id, size, content }[]`) so each card can hold a real Chart.js canvas instead of placeholder text, and the color palette/dark background was replaced with the pastel/white theme.
- **LineSidebar**: functionally identical; only the default colors changed, and `onItemClick` is wired to `scrollIntoView` on a matching section `id`.
- **CardNav**: swapped the image `logo` prop for a `logoText` wordmark (no logo asset was supplied), made the CTA button optional, and each card's `links` call `onNavigate`-style callbacks that switch the active page instead of pointing to external URLs.
- **CardSwap**: logic untouched; only `Card` styling changed, to the dark-navy-on-pastel look from the reference screenshot.

## 8. Known limitations to flag to anyone using this

- The production bundle is ~612 KB gzipped to ~198 KB, mostly `gsap` + `ogl` + `chart.js`. Fine for a small research dashboard; if it ever needs to be leaner, code-splitting the `About` page's GSAP-heavy components with `React.lazy` would be the first move.
- No automated tests were written for this handoff — `npm run build` was used as the correctness check (it compiles and type-checks JSX, but doesn't verify runtime behavior in a real browser).
- The disclaimer modal shows on every load by design (per your spec); if you'd rather it only show once per visitor, swap the `useState(true)` in `DisclaimerModal.jsx` for a `localStorage` check.
