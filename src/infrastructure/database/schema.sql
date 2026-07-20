-- ============================================================
-- Phase 1 — Schema for the mock interview database
-- ============================================================
-- Classic employees/departments schema: supports JOINs, self-joins
-- (manager_id references employees itself), GROUP BY + aggregates,
-- and NULL handling (top of the org chart has no manager).
-- ============================================================

CREATE TABLE departments (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE employees (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    manager_id    INTEGER,
    salary        REAL NOT NULL,
    hire_date     TEXT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (manager_id) REFERENCES employees(id)
);
