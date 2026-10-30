
from dataclasses import dataclass
from enum import Enum


class GameStatus(Enum):
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


@dataclass(frozen=True)
class GuessResult:
    guess: str
    feedback: tuple[int, ...]
    attempt_number: int


class WordleGame:
    def __init__(
        self,
        answer: str,
        allowed_words: set[str],
        max_attempts: int = 6,
    ) -> None:
        raise NotImplementedError

    def submit_guess(self, guess: str) -> GuessResult:
        raise NotImplementedError
