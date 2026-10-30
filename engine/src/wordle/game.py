
from dataclasses import dataclass
from enum import Enum
from random import randint
from src.wordle.feedback import get_feedback


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
        self.allowed_words = allowed_words.copy()
        answer = self.allowed_words[randint(0, len(allowed_words))]
        self.answer = answer
        self.max_attempts = max_attempts
        self.current_attempt = 1
        self.status = GameStatus.IN_PROGRESS

    def submit_guess(self, guess: str) -> GuessResult:
        if self.current_attempt > self.max_attempts:
            raise GameEndedError('Ended attempts:', 'current:',
                                 self.current_attempt, 'max:', self.max_attempts)

        if self.allowed_words.__contains__(guess) is False:
            raise ValueError(guess, 'is not allowed word')
        feedback = get_feedback(self.answer, guess)
        if feedback == tuple(2 for _ in guess):
            self.status = GameStatus.WON
            raise GameEndedError(
                'You WON in', self.current_attempt, 'attempts!')
        if self.current_attempt == self.max_attempts:
            self.status = GameStatus.LOST
            raise GameEndedError(
                'You LOST. The WORD was:', self.answer)
        self.current_attempt += 1
        return GuessResult(guess, feedback, self.current_attempt)
