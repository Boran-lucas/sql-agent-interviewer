import sqlite3

import pytest

from src.infrastructure.database.connection import create_seeded_db


def test_returns_connection():
    conn = create_seeded_db()
    assert isinstance(conn, sqlite3.Connection)


def test_departments_table_seeded():
    conn = create_seeded_db()
    count = conn.execute("SELECT COUNT(*) FROM departments").fetchone()[0]
    assert count >= 3


def test_employees_table_seeded():
    conn = create_seeded_db()
    count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    assert count >= 6


def test_ceo_has_no_manager():
    conn = create_seeded_db()
    rows = conn.execute(
        "SELECT * FROM employees WHERE manager_id IS NULL"
    ).fetchall()
    assert len(rows) >= 1


def test_foreign_keys_are_enforced():
    conn = create_seeded_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO employees (id, name, department_id, manager_id, salary, hire_date) "
            "VALUES (99, 'Ghost', 999, NULL, 50000.0, '2022-01-01')"
        )
