
from dataclasses import dataclass
from enum import Enum
from random import choice
from .feedback import get_feedback

class GameStatus(Enum):
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


@dataclass(frozen=True)
class GuessResult:
    guess: str
    feedback: tuple[int, ...]
    attempt_number: int


class GameEndedError(Exception):
    def __init__(self, *args):
        self.message = ' '.join([str(arg) for arg in args])
        super().__init__(args)


class WordleGame:
    def __init__(
            self,
            allowed_words: set[str],
            max_attempts: int = 6) -> None:
        if max_attempts <= 0:
            raise ValueError(f'Expected max_attempts greater than 0, but got: {max_attempts}')
        self.max_attempts = max_attempts
        self.allowed_words = allowed_words.copy()
        answer = choice(list(self.allowed_words))
        self._answer = answer
        self._status = GameStatus.IN_PROGRESS
        self.history: list[GuessResult] = []

    def get_answer(self) -> str:
        return self._answer

    def get_attempts(self) -> int:
        return 1 + len(self.history)
    
    def get_status(self) -> GameStatus:
        return self._status

    def submit_guess(self, guess: str) -> GuessResult:
        result = self._submit_guess(guess=guess)
        self.history.append(result)
        return result

    def _submit_guess(self, guess: str) -> GuessResult:
        if self._status != GameStatus.IN_PROGRESS:
            raise GameEndedError('Game status is', self._status)
        current_attempt = self.get_attempts()
        if current_attempt > self.max_attempts:
            raise GameEndedError('Ended attempts:', 'current:',
                                 current_attempt, 'max:', self.max_attempts)

        feedback = get_feedback(self._answer, guess, self.allowed_words)
        if feedback == tuple(2 for _ in guess):
            self._status = GameStatus.WON
            return GuessResult(guess, feedback, current_attempt)
        if current_attempt == self.max_attempts:
            self._status = GameStatus.LOST
            return GuessResult(guess, feedback, current_attempt)

        return GuessResult(guess, feedback, current_attempt)
