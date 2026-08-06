"""
Interactive University Data Dashboard (Streamlit).

Run:
    pip install -r requirements.txt
    streamlit run app.py

Data is generated automatically on first run via generate_data.py.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
METRICS_CSV = os.path.join(DATA_DIR, "metrics.csv")
STUDENTS_CSV = os.path.join(DATA_DIR, "students.csv")
COURSES_CSV = os.path.join(DATA_DIR, "courses.csv")

# --- Yeshiva University brand palette ---
YU_NAVY = "#0033A0"
YU_LIGHT = "#4A7AD6"
YU_GOLD = "#C8A45C"
YU_SEQ = ["#0033A0", "#4A7AD6", "#C8A45C", "#1B4F9C", "#7FA3E0", "#9E7B2E", "#003366"]

st.set_page_config(
    page_title="Yeshiva University — Data Dashboard",
    page_icon="🎓",
    layout="wide",
)

# Apply brand colors to every Plotly chart by default.
px.defaults.color_discrete_sequence = YU_SEQ
px.defaults.template = "plotly_white"

# Branded header banner.
st.markdown(
    f"""
    <style>
      .yu-banner {{
        background: linear-gradient(90deg, {YU_NAVY} 0%, #001F66 100%);
        padding: 18px 26px; border-radius: 10px; margin-bottom: 8px;
        border-bottom: 4px solid {YU_GOLD};
      }}
      .yu-banner h1 {{ color: #FFFFFF; margin: 0; font-size: 1.7rem; letter-spacing: .5px; }}
      .yu-banner p  {{ color: #C9D7F2; margin: 2px 0 0 0; font-size: .95rem; }}
      [data-testid="stMetricValue"] {{ color: {YU_NAVY}; }}
    </style>
    <div class="yu-banner">
      <h1>🎓 Yeshiva University · Institutional Data Dashboard</h1>
      <p>Enrollment · Academics · Courses · Admissions · Finance &amp; Operations</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #
@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    needed = [METRICS_CSV, STUDENTS_CSV, COURSES_CSV]
    if not all(os.path.exists(p) for p in needed):
        # Generate on first run (or after adding new tables).
        subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__), "generate_data.py")],
            check=True,
        )
    metrics = pd.read_csv(METRICS_CSV)
    students = pd.read_csv(STUDENTS_CSV)
    courses = pd.read_csv(COURSES_CSV)
    return metrics, students, courses


metrics, students, courses = load_data()


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


# --------------------------------------------------------------------------- #
# Sidebar filters
# --------------------------------------------------------------------------- #
st.sidebar.title("🎓 Filters")

yr_min, yr_max = int(metrics["year"].min()), int(metrics["year"].max())
year_range = st.sidebar.slider(
    "Academic year range",
    min_value=yr_min,
    max_value=yr_max,
    value=(yr_min, yr_max),
)

all_depts = sorted(metrics["department"].unique())
sel_depts = st.sidebar.multiselect(
    "Departments / Colleges",
    options=all_depts,
    default=all_depts,
)

sel_residency = st.sidebar.multiselect(
    "Student residency (drill-down views)",
    options=sorted(students["residency"].unique()),
    default=sorted(students["residency"].unique()),
)

sel_gender = st.sidebar.multiselect(
    "Gender (drill-down views)",
    options=sorted(students["gender"].unique()),
    default=sorted(students["gender"].unique()),
)

sel_terms = st.sidebar.multiselect(
    "Term (course views)",
    options=sorted(courses["term"].unique()),
    default=sorted(courses["term"].unique()),
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Mock data, deterministically generated. "
    "Use the tabs to explore enrollment, academics, admissions, and finance."
)

# Apply filters.
if not sel_depts:
    sel_depts = all_depts  # guard against empty selection

m = metrics[
    metrics["year"].between(*year_range) & metrics["department"].isin(sel_depts)
].copy()

s = students[
    students["year"].between(*year_range)
    & students["department"].isin(sel_depts)
    & students["residency"].isin(sel_residency or sorted(students["residency"].unique()))
    & students["gender"].isin(sel_gender or sorted(students["gender"].unique()))
].copy()

c = courses[
    courses["year"].between(*year_range)
    & courses["department"].isin(sel_depts)
    & courses["term"].isin(sel_terms or sorted(courses["term"].unique()))
].copy()


# --------------------------------------------------------------------------- #
# Header + KPI cards
# --------------------------------------------------------------------------- #
st.caption(
    f"Showing **{year_range[0]}–{year_range[1]}** across "
    f"**{len(sel_depts)}** of {len(all_depts)} departments."
)

latest_year = m["year"].max()
prev_year = latest_year - 1
cur = m[m["year"] == latest_year]
prv = m[m["year"] == prev_year]


def delta(metric_col: str, agg: str = "sum") -> str | None:
    if prv.empty:
        return None
    cur_v = getattr(cur[metric_col], agg)()
    prv_v = getattr(prv[metric_col], agg)()
    if prv_v == 0:
        return None
    return f"{(cur_v - prv_v) / prv_v * 100:+.1f}% vs {prev_year}"


k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total enrollment", f"{int(cur['total_enrollment'].sum()):,}", delta("total_enrollment"))
k2.metric("Applications", f"{int(cur['applications'].sum()):,}", delta("applications"))
k3.metric(
    "Avg admit rate",
    pct(cur["admit_rate"].mean()) if not cur.empty else "—",
    delta("admit_rate", "mean"),
)
k4.metric("Avg GPA", f"{cur['avg_gpa'].mean():.2f}" if not cur.empty else "—", delta("avg_gpa", "mean"))
k5.metric(
    "Tuition revenue",
    f"${cur['tuition_revenue'].sum() / 1e6:,.0f}M" if not cur.empty else "—",
    delta("tuition_revenue"),
)

st.markdown("---")

tab_enroll, tab_acad, tab_course, tab_admis, tab_fin, tab_data = st.tabs(
    ["📈 Enrollment", "🎯 Academics", "📚 Courses", "📝 Admissions",
     "💰 Finance & Ops", "🔎 Data / Drill-down"]
)


# --------------------------------------------------------------------------- #
# Enrollment
# --------------------------------------------------------------------------- #
with tab_enroll:
    c1, c2 = st.columns(2)
    by_year = m.groupby("year", as_index=False)["total_enrollment"].sum()
    fig = px.area(
        by_year, x="year", y="total_enrollment",
        title="Total enrollment over time", markers=True,
    )
    c1.plotly_chart(fig, use_container_width=True)

    by_dept = m.groupby(["year", "department"], as_index=False)["total_enrollment"].sum()
    fig = px.bar(
        by_dept, x="year", y="total_enrollment", color="department",
        title="Enrollment by department",
    )
    c2.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    ret = m.groupby("year", as_index=False)[["retention_rate", "grad_rate"]].mean()
    fig = px.line(
        ret, x="year", y=["retention_rate", "grad_rate"],
        title="Retention vs graduation rate", markers=True,
    )
    fig.update_yaxes(tickformat=".0%")
    c3.plotly_chart(fig, use_container_width=True)

    # Class-level mix from the student sample.
    if not s.empty:
        mix = s.groupby("class_level", as_index=False)["student_id"].count()
        fig = px.pie(mix, names="class_level", values="student_id", title="Class-level mix (sample)")
        c4.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------------------------------- #
# Academics
# --------------------------------------------------------------------------- #
with tab_acad:
    c1, c2 = st.columns(2)
    gpa = m.groupby(["year", "department"], as_index=False)["avg_gpa"].mean()
    fig = px.line(gpa, x="year", y="avg_gpa", color="department", title="Average GPA trend", markers=True)
    c1.plotly_chart(fig, use_container_width=True)

    pr = m.groupby("department", as_index=False)["pass_rate"].mean().sort_values("pass_rate")
    fig = px.bar(pr, x="pass_rate", y="department", orientation="h", title="Average pass rate by department")
    fig.update_xaxes(tickformat=".0%")
    c2.plotly_chart(fig, use_container_width=True)

    st.subheader("GPA distribution (student sample)")
    if not s.empty:
        fig = px.histogram(s, x="gpa", nbins=30, color="department", marginal="box",
                           title="GPA distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No students match the current filters.")


# --------------------------------------------------------------------------- #
# Courses (course-level)
# --------------------------------------------------------------------------- #
with tab_course:
    if c.empty:
        st.info("No course sections match the current filters.")
    else:
        ck1, ck2, ck3, ck4 = st.columns(4)
        ck1.metric("Sections offered", f"{len(c):,}")
        ck2.metric("Total seats filled", f"{int(c['enrolled'].sum()):,}")
        ck3.metric("Avg fill rate", pct(c["fill_rate"].mean()))
        ck4.metric("Avg course grade", f"{c['avg_grade'].mean():.2f}")

        c1, c2 = st.columns(2)
        offered = c.groupby(["year", "term"], as_index=False)["course_id"].count()
        fig = px.bar(
            offered, x="year", y="course_id", color="term", barmode="group",
            title="Course sections offered by term", labels={"course_id": "sections"},
        )
        c1.plotly_chart(fig, use_container_width=True)

        by_level = c.groupby("level", as_index=False).agg(
            sections=("course_id", "count"), avg_fill=("fill_rate", "mean")
        )
        fig = px.bar(by_level, x="level", y="sections", title="Sections by course level",
                     hover_data=["avg_fill"])
        fig.update_xaxes(type="category")
        c2.plotly_chart(fig, use_container_width=True)

        c3, c4 = st.columns(2)
        fill_dept = c.groupby("department", as_index=False)["fill_rate"].mean().sort_values("fill_rate")
        fig = px.bar(fill_dept, x="fill_rate", y="department", orientation="h",
                     title="Average fill rate (enrolled ÷ capacity) by department")
        fig.update_xaxes(tickformat=".0%")
        c3.plotly_chart(fig, use_container_width=True)

        fig = px.scatter(
            c, x="enrolled", y="avg_grade", color="department", size="capacity",
            hover_data=["course_code", "course_title", "instructor", "year", "term"],
            title="Enrollment vs average grade (one point per section)",
        )
        c4.plotly_chart(fig, use_container_width=True)

        st.subheader("Course catalog — filtered")
        only_full = st.checkbox("Show only near-full sections (fill ≥ 90%)", value=False)
        cat = c[c["fill_rate"] >= 0.9] if only_full else c
        st.dataframe(
            cat[
                ["year", "term", "department", "major", "course_code", "course_title",
                 "level", "instructor", "enrolled", "capacity", "fill_rate", "credits",
                 "avg_grade", "pass_rate"]
            ].sort_values(["year", "term", "course_code"]),
            use_container_width=True, height=320,
        )
        st.download_button(
            "⬇️ Download filtered course catalog (CSV)",
            data=to_csv_bytes(cat),
            file_name="courses_filtered.csv",
            mime="text/csv",
        )


# --------------------------------------------------------------------------- #
# Admissions
# --------------------------------------------------------------------------- #
with tab_admis:
    c1, c2 = st.columns(2)
    funnel = m.groupby("year", as_index=False)[["applications", "admits", "new_enrolled"]].sum()
    fig = px.line(
        funnel, x="year", y=["applications", "admits", "new_enrolled"],
        title="Admissions funnel over time", markers=True,
    )
    c1.plotly_chart(fig, use_container_width=True)

    rates = m.groupby("year", as_index=False)[["admit_rate", "yield_rate"]].mean()
    fig = px.line(rates, x="year", y=["admit_rate", "yield_rate"],
                  title="Admit rate vs yield rate", markers=True)
    fig.update_yaxes(tickformat=".0%")
    c2.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    sel_year = c3.select_slider(
        "Funnel snapshot year", options=sorted(m["year"].unique()),
        value=int(m["year"].max()),
    )
    snap = m[m["year"] == sel_year][["applications", "admits", "new_enrolled"]].sum()
    fig = px.funnel(
        x=[snap["applications"], snap["admits"], snap["new_enrolled"]],
        y=["Applied", "Admitted", "Enrolled"],
        title=f"Funnel — {sel_year}",
    )
    c3.plotly_chart(fig, use_container_width=True)

    score = m.groupby("department", as_index=False)["avg_test_score"].mean().sort_values("avg_test_score")
    fig = px.bar(score, x="avg_test_score", y="department", orientation="h",
                 title="Avg admitted test score by department")
    c4.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------------------------------- #
# Finance & Ops
# --------------------------------------------------------------------------- #
with tab_fin:
    c1, c2 = st.columns(2)
    fin = m.groupby("year", as_index=False)[["tuition_revenue", "operating_budget"]].sum()
    fig = px.line(fin, x="year", y=["tuition_revenue", "operating_budget"],
                  title="Tuition revenue vs operating budget", markers=True)
    c1.plotly_chart(fig, use_container_width=True)

    ratio = m.groupby("department", as_index=False)["student_faculty_ratio"].mean()
    fig = px.bar(ratio, x="department", y="student_faculty_ratio",
                 title="Student-to-faculty ratio by department", color="student_faculty_ratio")
    c2.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    rev_dept = m.groupby("department", as_index=False)["tuition_revenue"].sum()
    fig = px.pie(rev_dept, names="department", values="tuition_revenue",
                 title="Tuition revenue share by department", hole=0.4)
    c3.plotly_chart(fig, use_container_width=True)

    fac = m.groupby("year", as_index=False)["faculty_count"].sum()
    fig = px.bar(fac, x="year", y="faculty_count", title="Faculty headcount over time")
    c4.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------------------------------- #
# Data / Drill-down
# --------------------------------------------------------------------------- #
with tab_data:
    st.subheader("Drill into a department")
    drill_dept = st.selectbox("Department", options=sel_depts)

    dd = s[s["department"] == drill_dept]
    mm = m[m["department"] == drill_dept]

    if dd.empty:
        st.info("No student records match the current filters for this department.")
    else:
        d1, d2 = st.columns(2)
        major_mix = dd.groupby("major", as_index=False)["student_id"].count()
        fig = px.bar(major_mix, x="major", y="student_id", title=f"{drill_dept}: students by major")
        d1.plotly_chart(fig, use_container_width=True)

        status_mix = dd.groupby("status", as_index=False)["student_id"].count()
        fig = px.pie(status_mix, names="status", values="student_id",
                     title=f"{drill_dept}: enrollment status")
        d2.plotly_chart(fig, use_container_width=True)

    # Course-level drill-down for the chosen department.
    cdd = c[c["department"] == drill_dept]
    if not cdd.empty:
        st.markdown(f"**{drill_dept}: top course sections by enrollment**")
        top = cdd.sort_values("enrolled", ascending=False).head(10)
        fig = px.bar(
            top, x="enrolled", y="course_code", orientation="h", color="major",
            hover_data=["course_title", "year", "term", "instructor", "fill_rate"],
            title=f"{drill_dept}: top 10 sections",
        )
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Filtered metrics table")
    st.dataframe(m, use_container_width=True, height=300)

    dl1, dl2, dl3 = st.columns(3)
    dl1.download_button(
        "⬇️ Metrics (CSV)",
        data=to_csv_bytes(m),
        file_name="metrics_filtered.csv",
        mime="text/csv",
    )
    dl2.download_button(
        "⬇️ Students (CSV)",
        data=to_csv_bytes(s),
        file_name="students_filtered.csv",
        mime="text/csv",
    )
    dl3.download_button(
        "⬇️ Courses (CSV)",
        data=to_csv_bytes(c),
        file_name="courses_filtered.csv",
        mime="text/csv",
    )
