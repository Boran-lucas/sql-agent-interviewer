from enum import Enum

from pydantic import BaseModel


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Question(BaseModel):
    id: int
    prompt: str
    difficulty: Difficulty
    expected_sql: str


class AnswerSubmission(BaseModel):
    question_id: int
    candidate_sql: str


class ValidationResult(BaseModel):
    correct: bool
    candidate_row_count: int
    expected_row_count: int
    message: str
