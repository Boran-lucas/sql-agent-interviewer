import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    schema_sql = SCHEMA_PATH.read_text()
    conn.executescript(schema_sql)
    conn.commit()


def seed_data(conn: sqlite3.Connection) -> None:
    departments = [
        (1, "Engineering"),
        (2, "Sales"),
        (3, "HR"),
    ]
    conn.executemany(
        "INSERT INTO departments (id, name) VALUES (?, ?)", departments
    )

    employees = [
        # id, name,            department_id, manager_id, salary,  hire_date
        (1, "Alice Martin",    1,             None,       145000.0, "2015-01-12"),
        (2, "Bruno Girard",    1,             1,          98000.0,  "2018-03-04"),
        (3, "Chloe Dubois",    1,             1,          102000.0, "2019-07-21"),
        (4, "David Nguyen",    2,             1,          110000.0, "2016-11-02"),
        (5, "Emma Laurent",    2,             4,          78000.0,  "2021-02-15"),
        (6, "Farid Bensaid",   3,             1,          85000.0,  "2020-09-30"),
    ]
    conn.executemany(
        """
        INSERT INTO employees (id, name, department_id, manager_id, salary, hire_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        employees,
    )
    conn.commit()


def create_seeded_db() -> sqlite3.Connection:
    conn = get_connection()
    init_schema(conn)
    seed_data(conn)
    return conn
