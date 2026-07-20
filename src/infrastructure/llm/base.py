from abc import ABC, abstractmethod

from src.domain.models import Difficulty, Question


class QuestionProvider(ABC):
    @abstractmethod
    def get_question(self, difficulty: Difficulty) -> Question:
        ...
