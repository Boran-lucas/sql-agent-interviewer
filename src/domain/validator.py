import sqlite3

import pandas as pd

from src.domain.models import ValidationResult


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reindex(sorted(df.columns), axis=1)
    return df.sort_values(by=list(df.columns)).reset_index(drop=True)


def _dataframes_match(candidate_df: pd.DataFrame, expected_df: pd.DataFrame) -> bool:
    if set(candidate_df.columns) != set(expected_df.columns):
        return False
    return _normalize(candidate_df).equals(_normalize(expected_df))


def validate_answer(
    conn: sqlite3.Connection, candidate_sql: str, expected_sql: str
) -> ValidationResult:
    try:
        candidate_df = pd.read_sql_query(candidate_sql, conn)
    except Exception as exc:
        return ValidationResult(
            correct=False,
            candidate_row_count=0,
            expected_row_count=0,
            message=f"Your query failed to execute: {exc}",
        )

    expected_df = pd.read_sql_query(expected_sql, conn)
    correct = _dataframes_match(candidate_df, expected_df)
    return ValidationResult(
        correct=correct,
        candidate_row_count=len(candidate_df),
        expected_row_count=len(expected_df),
        message="Correct!" if correct else "Your result doesn't match the expected output.",
    )
