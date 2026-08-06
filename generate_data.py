"""
Generate realistic mock university data for the dashboard.

Produces two CSVs in ./data:
  - metrics.csv    one row per (year, department) with enrollment, admissions,
                   academic performance, and finance/operations metrics.
  - students.csv   a student-level sample used for drill-down views.

Deterministic: a fixed seed means the same data every run, so the dashboard
is reproducible for a capstone demo.
"""

from __future__ import annotations

import os
import numpy as np
import pandas as pd

SEED = 42
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

YEARS = list(range(2015, 2026))  # 2015..2025 inclusive
DEPARTMENTS = {
    "Engineering": ["Computer Science", "Mechanical", "Electrical", "Civil"],
    "Business": ["Finance", "Marketing", "Accounting", "Management"],
    "Arts & Sciences": ["Biology", "Psychology", "History", "Mathematics"],
    "Education": ["Elementary Ed", "Special Ed", "Curriculum"],
    "Nursing": ["Nursing BSN", "Public Health"],
    "Law": ["JD Program", "Legal Studies"],
}
CLASS_LEVELS = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
GENDERS = ["Female", "Male", "Other"]
RESIDENCY = ["In-State", "Out-of-State", "International"]
TERMS = ["Fall", "Spring"]
COURSE_LEVELS = [100, 200, 300, 400, 500]  # 500 = graduate

# Subject-code prefix per major (used to build course codes like "CS-201").
MAJOR_PREFIX = {
    "Computer Science": "CS", "Mechanical": "ME", "Electrical": "EE", "Civil": "CE",
    "Finance": "FIN", "Marketing": "MKT", "Accounting": "ACC", "Management": "MGT",
    "Biology": "BIO", "Psychology": "PSY", "History": "HIS", "Mathematics": "MAT",
    "Elementary Ed": "EDU", "Special Ed": "SPED", "Curriculum": "CUR",
    "Nursing BSN": "NUR", "Public Health": "PUB", "JD Program": "LAW", "Legal Studies": "LGL",
}
# Generic title fragments to compose plausible course names per level.
TITLE_BY_LEVEL = {
    100: ["Introduction to {m}", "Foundations of {m}", "Principles of {m}"],
    200: ["Intermediate {m}", "{m} Methods", "Applied {m}"],
    300: ["Advanced {m}", "{m} Theory", "Topics in {m}"],
    400: ["{m} Capstone", "Senior Seminar in {m}", "{m} Research"],
    500: ["Graduate {m}", "{m} Practicum", "{m} Thesis Studio"],
}
INSTRUCTORS = [
    "Dr. Cohen", "Dr. Levin", "Prof. Schwartz", "Dr. Friedman", "Prof. Goldberg",
    "Dr. Katz", "Prof. Rosen", "Dr. Weiss", "Dr. Klein", "Prof. Adler",
    "Dr. Shapiro", "Prof. Mandel", "Dr. Bram", "Prof. Stern", "Dr. Halpern",
]

# Per-department baseline scale (relative size of each college).
DEPT_SCALE = {
    "Engineering": 1.4,
    "Business": 1.3,
    "Arts & Sciences": 1.6,
    "Education": 0.7,
    "Nursing": 0.6,
    "Law": 0.4,
}


def _growth(year: int) -> float:
    """A gentle upward enrollment trend with a COVID-era dip."""
    base = 1.0 + (year - 2015) * 0.025
    if year in (2020, 2021):
        base *= 0.93
    return base


def build_metrics(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for dept, scale in DEPT_SCALE.items():
        for year in YEARS:
            g = _growth(year)
            applications = int(rng.normal(2500, 200) * scale * g)
            admit_rate = float(np.clip(rng.normal(0.55, 0.08), 0.25, 0.9))
            admits = int(applications * admit_rate)
            yield_rate = float(np.clip(rng.normal(0.42, 0.06), 0.2, 0.75))
            new_enrolled = int(admits * yield_rate)

            total_enrollment = int(new_enrolled * rng.uniform(3.6, 4.4))
            retention_rate = float(np.clip(rng.normal(0.86, 0.05), 0.65, 0.98))
            grad_rate = float(np.clip(rng.normal(0.78, 0.07), 0.5, 0.97))
            avg_gpa = float(np.clip(rng.normal(3.15, 0.18), 2.4, 3.95))
            pass_rate = float(np.clip(rng.normal(0.91, 0.04), 0.7, 0.995))
            avg_class_size = float(np.clip(rng.normal(28, 6), 8, 60))
            avg_test_score = int(np.clip(rng.normal(1220, 70), 950, 1550))

            faculty_count = max(8, int(total_enrollment / rng.uniform(14, 22)))
            student_faculty_ratio = round(total_enrollment / faculty_count, 1)
            tuition_per_student = rng.uniform(28000, 46000)
            tuition_revenue = int(total_enrollment * tuition_per_student)
            operating_budget = int(tuition_revenue * rng.uniform(0.85, 1.15))

            rows.append(
                {
                    "year": year,
                    "department": dept,
                    # admissions
                    "applications": applications,
                    "admits": admits,
                    "admit_rate": round(admit_rate, 3),
                    "new_enrolled": new_enrolled,
                    "yield_rate": round(yield_rate, 3),
                    "avg_test_score": avg_test_score,
                    # enrollment
                    "total_enrollment": total_enrollment,
                    "retention_rate": round(retention_rate, 3),
                    "grad_rate": round(grad_rate, 3),
                    # academics
                    "avg_gpa": round(avg_gpa, 2),
                    "pass_rate": round(pass_rate, 3),
                    "avg_class_size": round(avg_class_size, 1),
                    # finance / ops
                    "faculty_count": faculty_count,
                    "student_faculty_ratio": student_faculty_ratio,
                    "tuition_revenue": tuition_revenue,
                    "operating_budget": operating_budget,
                }
            )
    return pd.DataFrame(rows)


def build_students(rng: np.random.Generator, metrics: pd.DataFrame) -> pd.DataFrame:
    """A sampled student-level table sized to ~3% of total enrollment per row."""
    rows = []
    sid = 100000
    for _, m in metrics.iterrows():
        sample_n = max(15, int(m["total_enrollment"] * 0.03))
        majors = DEPARTMENTS[m["department"]]
        for _ in range(sample_n):
            gpa = float(np.clip(rng.normal(m["avg_gpa"], 0.45), 0.0, 4.0))
            status = rng.choice(
                ["Enrolled", "Graduated", "Withdrawn", "On Leave"],
                p=[0.78, 0.13, 0.06, 0.03],
            )
            rows.append(
                {
                    "student_id": sid,
                    "year": int(m["year"]),
                    "department": m["department"],
                    "major": rng.choice(majors),
                    "class_level": rng.choice(
                        CLASS_LEVELS, p=[0.26, 0.24, 0.22, 0.20, 0.08]
                    ),
                    "gender": rng.choice(GENDERS, p=[0.52, 0.46, 0.02]),
                    "residency": rng.choice(RESIDENCY, p=[0.6, 0.28, 0.12]),
                    "gpa": round(gpa, 2),
                    "status": status,
                }
            )
            sid += 1
    return pd.DataFrame(rows)


def build_courses(rng: np.random.Generator, metrics: pd.DataFrame) -> pd.DataFrame:
    """Course-level offerings, one row per (year, term, course section)."""
    rows = []
    cid = 10000
    for _, m in metrics.iterrows():
        dept_gpa = m["avg_gpa"]
        for term in TERMS:
            for major in DEPARTMENTS[m["department"]]:
                prefix = MAJOR_PREFIX[major]
                n_courses = int(rng.integers(2, 5))  # 2-4 courses per major/term
                for _ in range(n_courses):
                    level = int(rng.choice(COURSE_LEVELS, p=[0.3, 0.28, 0.22, 0.12, 0.08]))
                    number = level + int(rng.integers(1, 60))
                    title = rng.choice(TITLE_BY_LEVEL[level]).format(m=major)
                    capacity = int(np.clip(rng.normal(m["avg_class_size"] * 1.25, 8), 10, 90))
                    fill = float(np.clip(rng.normal(0.82, 0.15), 0.2, 1.0))
                    enrolled = int(min(capacity, capacity * fill))
                    # Higher-level & grad courses skew to higher grades.
                    lvl_bump = (level - 100) / 400 * 0.25
                    avg_grade = float(np.clip(rng.normal(dept_gpa + lvl_bump, 0.3), 1.0, 4.0))
                    pass_rate = float(np.clip(rng.normal(0.92, 0.05), 0.6, 1.0))
                    credits = int(rng.choice([3, 3, 3, 4], p=[0.5, 0.2, 0.1, 0.2]))
                    rows.append(
                        {
                            "course_id": cid,
                            "year": int(m["year"]),
                            "term": term,
                            "department": m["department"],
                            "major": major,
                            "course_code": f"{prefix}-{number}",
                            "course_title": title,
                            "level": level,
                            "instructor": rng.choice(INSTRUCTORS),
                            "enrolled": enrolled,
                            "capacity": capacity,
                            "fill_rate": round(enrolled / capacity, 3),
                            "credits": credits,
                            "avg_grade": round(avg_grade, 2),
                            "pass_rate": round(pass_rate, 3),
                        }
                    )
                    cid += 1
    return pd.DataFrame(rows)


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    rng = np.random.default_rng(SEED)
    metrics = build_metrics(rng)
    students = build_students(rng, metrics)
    courses = build_courses(rng, metrics)
    metrics.to_csv(os.path.join(DATA_DIR, "metrics.csv"), index=False)
    students.to_csv(os.path.join(DATA_DIR, "students.csv"), index=False)
    courses.to_csv(os.path.join(DATA_DIR, "courses.csv"), index=False)
    print(
        f"Wrote {len(metrics):,} metric rows, {len(students):,} student rows, "
        f"and {len(courses):,} course rows to {DATA_DIR}"
    )


if __name__ == "__main__":
    main()
