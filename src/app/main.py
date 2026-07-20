from fastapi import Depends, FastAPI, HTTPException

from src.domain.models import AnswerSubmission, Difficulty, Question, ValidationResult
from src.domain.validator import validate_answer
from src.infrastructure.database.connection import create_seeded_db
from src.infrastructure.llm.base import QuestionProvider
from src.infrastructure.llm.mock_provider import MockQuestionProvider

app = FastAPI(title="SQL Agent Interviewer")

_db_conn = create_seeded_db()
_questions: dict[int, Question] = {}


def get_question_provider() -> QuestionProvider:
    return MockQuestionProvider()


@app.get("/questions", response_model=Question)
def get_question(
    difficulty: Difficulty = Difficulty.EASY,
    provider: QuestionProvider = Depends(get_question_provider),
) -> Question:
    question = provider.get_question(difficulty)
    _questions[question.id] = question
    return question


@app.post("/answers", response_model=ValidationResult)
def submit_answer(submission: AnswerSubmission) -> ValidationResult:
    question = _questions.get(submission.question_id)
    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Unknown question_id — call GET /questions first",
        )
    return validate_answer(_db_conn, submission.candidate_sql, question.expected_sql)
