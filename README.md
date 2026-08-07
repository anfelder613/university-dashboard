# YU Institutional Data Dashboard

> **What does a full-breadth university analytics dashboard look like, end to end?**

A branded Streamlit dashboard covering enrollment, academic performance, course-level
offerings, admissions, and finance/operations for a university, 2015–2025.

**Live:** Runs locally (Streamlit — see [Running it](#running-it))
**Status:** Prototype complete
**Stack:** Streamlit · Python · Pandas

---

## Scope — read this first

**All data in this project is synthetic.** It is generated deterministically by
`generate_data.py` and is for demonstration purposes only. No figure here describes
Yeshiva University or any real institution.

This is the warm-up project of the capstone series — built to exercise dashboard breadth,
layout, filtering, and branding before the later projects narrowed to a single sharp
question each on **real IPEDS data**. The sibling projects listed below take the opposite
approach: one measure, verified against public federal data, with a hard no-synthetic-data
rule.

Read this one as a UI/UX exercise, not as an analysis.

## What it shows

Six tabs over a shared filter state:

| Tab | Contents |
|---|---|
| **Enrollment** | Headcount trends by year, department, residency, and gender |
| **Academics** | Academic performance metrics and distributions |
| **Courses** | Sections by term and level, fill rates, enrollment-vs-grade scatter, searchable catalog |
| **Admissions** | Applications → admits → enrolled funnel, snapshot by year |
| **Finance & Ops** | Tuition revenue, faculty counts, student-faculty ratio |
| **Data** | Drill-down by department (major, enrollment status, top sections) and CSV export |

Plus:

- **Sidebar filters** — year-range slider, department multiselect, residency, gender, term.
- **KPI cards** — headline metrics with year-over-year deltas.
- **Export** — download filtered metrics, students, and course catalog as CSV.

## The data

Three synthetic tables, regenerated deterministically from a fixed seed:

| File | Grain | Contents |
|---|---|---|
| `data/metrics.csv` | One row per (year, department) | Enrollment, admissions funnel, faculty, revenue |
| `data/students.csv` | Student-level sample | ~3% of total enrollment per department-year, for drill-down |
| `data/courses.csv` | Course-section level | Year, term, course, capacity, fill rate, grades |

The generator models a gentle upward enrollment trend with a COVID-era dip, and derives
faculty counts, student-faculty ratio, and tuition revenue from enrollment so the tables stay
internally consistent.

**Year range:** 2015–2025.

## Branding

Themed for Yeshiva University — navy `#0033A0` with a gold accent. Theme colors live in
`.streamlit/config.toml`; the branded header banner and the chart color palette are applied
in `app.py`.

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py          # http://localhost:8501
```

The first run auto-generates the mock data into `./data`. To regenerate manually:

```bash
python generate_data.py
```

> **Note:** this dashboard cannot be hosted on GitHub Pages. Pages serves static files only,
> and this is a Streamlit app. Hosting it publicly would require a Python host such as
> Streamlit Community Cloud.

## Repo layout

```
app.py                    # the dashboard
generate_data.py          # deterministic synthetic-data generator
/data                     # generated CSVs
.streamlit/config.toml    # YU brand theme
```

## Related projects

Sibling capstone dashboards. Unlike this one, each uses **real IPEDS data** and answers a
single narrow question:

- [YU PhD Completions Dashboard](https://github.com/anfelder613/yu-enrollment-dashboard) — Completions component
- [YU Institutional Resources Dashboard](https://github.com/anfelder613/yu-institutional-resources-dashboard) — Finance component
- [YU Peer Tuition Dashboard](https://github.com/anfelder613/yu-tuition-dashboard) — Cost component

Part of the [capstone portfolio](https://anfelder613.github.io/) — an index of all four dashboards.
