# Yeshiva University — Institutional Data Dashboard

An interactive Streamlit dashboard, branded for **Yeshiva University** (navy/gold theme),
over mock university data covering: **enrollment**, **academic performance**, **course-level
offerings**, **admissions**, and **finance/operations**.

## Features
- **Sidebar filters** — year-range slider, department multiselect, residency, gender, and term filters.
- **KPI cards** — headline metrics with year-over-year deltas.
- **Six tabs** — Enrollment, Academics, **Courses**, Admissions, Finance & Ops, and a Data/Drill-down view.
- **Course-level view** — sections by term & level, fill rates, enrollment-vs-grade scatter, and a searchable catalog.
- **Drill-down** — pick a department to break it down by major, enrollment status, and top course sections.
- **Date/range sliders** — scrub the year range and snapshot the admissions funnel by year.
- **Export** — download filtered metrics, students, and course catalog as CSV.

## Branding
- Theme colors live in `.streamlit/config.toml` (YU navy `#0033A0`, gold accent).
- A branded header banner and YU color palette are applied to all charts in `app.py`.

## Setup
```bash
cd project_1
python -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
streamlit run app.py
```

The first run auto-generates the mock data into `./data` (via `generate_data.py`).
To regenerate manually:
```bash
python generate_data.py
```

## Files
| File | Purpose |
|------|---------|
| `app.py` | The Streamlit dashboard |
| `generate_data.py` | Deterministic mock-data generator |
| `data/metrics.csv` | One row per (year, department) — all aggregate metrics |
| `data/students.csv` | Student-level sample for drill-down |
| `data/courses.csv` | Course-level sections (year, term, course, fill rate, grades) |
| `.streamlit/config.toml` | Yeshiva University brand theme |
| `requirements.txt` | Python dependencies |

> Data is synthetic and for demonstration only.
