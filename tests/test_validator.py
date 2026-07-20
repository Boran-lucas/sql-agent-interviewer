from src.domain.validator import validate_answer
from src.infrastructure.database.connection import create_seeded_db


def test_correct_query_returns_correct_true():
    conn = create_seeded_db()
    result = validate_answer(conn, "SELECT * FROM departments", "SELECT * FROM departments")
    assert result.correct is True


def test_row_order_does_not_matter():
    conn = create_seeded_db()
    result = validate_answer(
        conn,
        "SELECT * FROM departments ORDER BY id DESC",
        "SELECT * FROM departments ORDER BY id ASC",
    )
    assert result.correct is True


def test_wrong_query_returns_correct_false():
    conn = create_seeded_db()
    result = validate_answer(
        conn,
        "SELECT * FROM departments WHERE id = 1",
        "SELECT * FROM departments",
    )
    assert result.correct is False


def test_invalid_sql_does_not_raise():
    conn = create_seeded_db()
    result = validate_answer(conn, "SELECT * FROM not_a_table", "SELECT * FROM departments")
    assert result.correct is False
    assert "failed" in result.message.lower()
