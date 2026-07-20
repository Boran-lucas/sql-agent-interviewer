import itertools
import random

from src.domain.models import Difficulty, Question
from src.infrastructure.llm.base import QuestionProvider

_ID_COUNTER = itertools.count(1)

_BANK: dict[Difficulty, list[tuple[str, str]]] = {
    Difficulty.EASY: [
        (
            "List all employees in the Engineering department.",
            "SELECT * FROM employees WHERE department_id = 1",
        ),
        (
            "List the names of every department.",
            "SELECT name FROM departments",
        ),
    ],
    Difficulty.MEDIUM: [
        (
            "Count how many employees are in each department, showing the department name.",
            "SELECT d.name, COUNT(*) AS employee_count "
            "FROM employees e JOIN departments d ON e.department_id = d.id "
            "GROUP BY d.name",
        ),
    ],
    Difficulty.HARD: [
        (
            "List each employee alongside their manager's name (NULL if they have none).",
            "SELECT e.name AS employee, m.name AS manager "
            "FROM employees e LEFT JOIN employees m ON e.manager_id = m.id",
        ),
    ],
}


class MockQuestionProvider(QuestionProvider):
    """Placeholder for the real LLM-backed provider wired up in Phase 3.

    Same interface (QuestionProvider) so main.py won't change when it's swapped.
    """

    def get_question(self, difficulty: Difficulty) -> Question:
        prompt, expected_sql = random.choice(_BANK[difficulty])
        return Question(
            id=next(_ID_COUNTER),
            prompt=prompt,
            difficulty=difficulty,
            expected_sql=expected_sql,
        )
