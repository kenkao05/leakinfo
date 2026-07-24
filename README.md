# India Exam Leak Tracker

A browsable dataset and dashboard of alleged and confirmed exam paper leaks and cancellations in India, 2000–2026 — spanning national entrance exams, central and state recruitment tests, and school board exams.

Exam leaks in India rarely get tracked in one place. Each one is covered locally, gets a news cycle, and then scatters across hundreds of state and national outlets. This project pulls that scattered coverage into a single dataset and a small dashboard to explore it.

**[Live site → Click Here](https://leakinfo.vercel.app/)**

---

## What's here

- **Charts** — a KPI strip and a grid of charts: yearly trend, incidents-per-year-in-office by administration, central-vs-state split, leak-status breakdown, top exams by aspirants affected, top states by incident count, and action-taken breakdown. Each chart carries an inline methodology caveat.
- **Info** — the full dataset as a filterable, sortable, searchable table. Filter by leak status, conducting-body type, administration, or confidence. Click a row to expand its full note and source link.
- **About** — why the project exists, plus a cycling stack of the major sources used.

## The dataset

`india_exam_leaks_master.csv` contains **129 incidents** from 2000–2026, covering NEET, JEE, CUET, CTET, UGC-NET, SSC, UPSC, Railways, KVS, ONGC, ASRB, Army recruitment, state police/PSC/teacher-eligibility exams, and CBSE/state board exams.

### Schema

| Column                          | Description                                                                                                                            |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `incident_id`                   | Stable ID, `PL-0001`...`PL-0129`                                                                                                       |
| `date`                          | Best-known date (`YYYY-MM-DD`); some are year-only placeholders where sources didn't give an exact date                                |
| `era`                           | Coarse original bucket (`NDA (1998-2004)`, `UPA (2004-May2014)`, `NDA (May2014-now)`)                                                  |
| `pm_of_year_exact`              | PM in office on the _exact_ incident date, computed from real transition dates — use this instead of `era` for anything date-sensitive |
| `ruling_party_centre_exact`     | Ruling party/coalition at the Centre, same exact-date basis                                                                            |
| `exam_name`                     | Name of the exam and year/session                                                                                                      |
| `conducting_body`               | Organisation that ran the exam                                                                                                         |
| `body_type`                     | `Central` or `State`                                                                                                                   |
| `area`                          | State/UT or "All India"                                                                                                                |
| `leak_status`                   | `Confirmed`, `Alleged`, `Denied`, or `Suspected`                                                                                       |
| `action_taken`                  | `+`-joined tags, e.g. `Exam cancelled + Arrests-FIR + Probe (CBI)`                                                                     |
| `note`                          | Free-text summary, with named officials/arrest counts where known                                                                      |
| `arrests` / `convictions`       | Plain integers where reported, blank otherwise                                                                                         |
| `aspirants_affected`            | Plain integer where a specific number was reported — sparse, don't treat as a complete census of scale                                 |
| `linked_deaths` / `deaths_note` | Only populated for cases with documented deaths connected to the investigation (e.g. Vyapam)                                           |
| `source_name` / `source_url`    | Attribution                                                                                                                            |
| `confidence`                    | `High` / `Medium` / `Low` — reflects how well-corroborated the row is, not how serious the incident was                                |

### Known caveats

- **Not exhaustive.** There is no official, complete registry of exam leaks in India. This is a research compilation from openly published English-language news coverage, so it under-represents incidents that only got regional-language or purely local coverage.
- **The underlying research was not independently fact-checked** incident-by-incident against primary court records. Several allegations were later denied by investigators — check the `confidence` and `leak_status` columns, not just the presence of a row.
- **`era` and `pm_of_year_exact` can disagree at the edges** — e.g. `PL-0001` is bucketed under `UPA` but the exact PM in office that day was Vajpayee (NDA), since Manmohan Singh's government only took office 22 May 2004.
- **Raw incident counts by administration are misleading** without normalizing for years in office and for how much better documentation/social-media leak detection has gotten over the 2000–2026 window. The dashboard normalizes for this; if you build your own charts from the CSV, do the same.
- **`aspirants_affected` is sparse.** Ranking exams by this field ranks "biggest reported number," not "biggest actual leak."

This dataset was researched with AI assistance from open sources. Treat it as a starting point for further reporting or research, not a definitive record — every incident links back to its original source, which is the place to verify anything you plan to rely on.

## Tech stack

- **Vite + React 18**
- **Chart.js** for the charts
- **GSAP** for animation (nav, card-fan transitions)
- **ogl** (lightweight WebGL) for the background shader
- Plain CSS — no Tailwind, no CSS-in-JS
- No backend. The dataset is baked into the app at build time as a static JSON file generated from the CSV.

## Running locally

```bash
# Clone and enter the project
git clone https://github.com/kenkao05/leakinfo leakinfo
cd leakinfo

# Install dependencies
npm install

# Generate src/data/leaks.json from the CSV
python3 prep_data.py

# Start the dev server
npm run dev
# -> open http://localhost:5173

# Build for production
npm run build
npm run preview
```

If you edit `india_exam_leaks_master.csv`, re-run `python3 prep_data.py` and restart the dev server — `src/data/leaks.json` is generated and shouldn't be hand-edited.

## Deploying

- Push the repo to GitHub.
- Import it at [vercel.com/new](https://vercel.com/new).
- Vercel auto-detects Vite: build command `npm run build`, output directory `dist`.
- No environment variables needed — it's fully static, no backend.

## Project structure

```
leakinfo/
├── india_exam_leaks_master.csv     ← the dataset
├── prep_data.py                    ← CSV → src/data/leaks.json converter
├── package.json
├── vite.config.js
├── index.html
└── src/
    ├── main.jsx
    ├── index.css                   ← design tokens + global/layout CSS
    ├── App.jsx                     ← WebGL backdrop, top nav, page switch
    ├── data/
    │   └── leaks.json              ← generated, do not hand-edit
    ├── components/
    │   ├── LightRays.jsx / .css    ← WebGL background
    │   ├── MagicBento.jsx / .css   ← animated chart-card grid
    │   ├── LineSidebar.jsx / .css  ← right-side chart jump-nav (desktop only)
    │   ├── CardNav.jsx / .css      ← top pill nav
    │   ├── CardSwap.jsx / .css     ← About-page source cards
    │   ├── ChartCanvas.jsx         ← Chart.js wrapper used by every chart
    │   ├── CardHeader.jsx          ← title + caveat header used inside chart cards
    │   ├── DataTable.jsx           ← searchable/sortable table (Info page)
    │   └── DisclaimerModal.jsx     ← AI/sourcing disclaimer, shown on every load
    └── pages/
        ├── ChartsPage.jsx
        ├── InfoPage.jsx
        └── AboutPage.jsx
```

## Sources

Careers360, The Tribune, Newslaundry, The Wire, Press Trust of India (PTI), ThePrint, Deccan Herald, and Wikipedia (for background on the Vyapam scam and the 2026 NEET controversy). Full per-incident attribution is in the `source_name` / `source_url` columns and in the Info tab of the app.

## Known limitations

- No automated tests — `npm run build` is used as the correctness check (compiles/type-checks JSX, doesn't verify runtime behavior in a browser).
- Production bundle is roughly 612 KB gzipped to ~198 KB, mostly `gsap` + `ogl` + `chart.js`. Fine for a small research dashboard; code-splitting the About page's GSAP-heavy components with `React.lazy` would be the first move if that ever needs to shrink.
- The disclaimer modal shows on every page load by design. Swap the `useState(true)` in `DisclaimerModal.jsx` for a `localStorage` check if you'd rather it show once per visitor.

## License

Code (everything under `src/`, `prep_data.py`, config files) is licensed under [MIT](LICENSE).

The dataset (`india_exam_leaks_master.csv`, `src/data/leaks.json`) is licensed under [CC-BY-4.0](LICENSE-DATA) — you're free to use, share, and adapt it, including commercially, as long as you credit this project as the compiler.

The underlying news coverage cited in `source_url` remains the copyright of the original publishers (The Tribune, Careers360, Newslaundry, The Wire, PTI, ThePrint, Deccan Herald, Wikipedia, and others). This repo holds only the structured summary and attribution — not reproduced article text.
