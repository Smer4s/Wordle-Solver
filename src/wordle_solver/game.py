
from dataclasses import dataclass
from enum import Enum
from random import choice, seed
from .feedback import get_feedback, validate, normalize

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
            max_attempts: int = 6,
            answer: str | None = None) -> None:
        if type(max_attempts) is not int:
            raise ValueError(f'Expected type of max_attempts to be int, but got: {type(max_attempts)}')
        if max_attempts <= 0:
            raise ValueError(f'Expected max_attempts greater than 0, but got: {max_attempts}')
        
        self.max_attempts = max_attempts
        if len(allowed_words) == 0:
            raise ValueError('allowed_words must not be empty')
        for word in allowed_words:
            validate(word)
        self._allowed_words = allowed_words.copy()
        if type(answer) == None:
            answer = choice(list(self._allowed_words))
        self._answer = answer
        self._status = GameStatus.IN_PROGRESS
        self._history: list[GuessResult] = []

    def get_allowed_words(self) -> set[str]:
        return self._allowed_words.copy()
    
    def get_history(self) -> list[GuessResult]:
        return self._history.copy()
    
    def get_answer(self) -> str:
        return self._answer

    def get_attempts(self) -> int:
        return 1 + len(self._history)
    
    def get_status(self) -> GameStatus:
        return self._status

    def submit_guess(self, guess: str) -> GuessResult:
        guess = normalize(guess)
        result = self._submit_guess(guess)
        self._history.append(result)
        return result


    def _submit_guess(self, guess: str) -> GuessResult:
        if self._status != GameStatus.IN_PROGRESS:
            raise GameEndedError('Game status is', self._status)
        current_attempt = self.get_attempts()
        if current_attempt > self.max_attempts:
            raise GameEndedError('Ended attempts:', 'current:',
                                 current_attempt, 'max:', self.max_attempts)

        feedback = get_feedback(self._answer, guess, self._allowed_words)
        if feedback == tuple(2 for _ in guess):
            self._status = GameStatus.WON
            return GuessResult(guess, feedback, current_attempt)
        if current_attempt == self.max_attempts:
            self._status = GameStatus.LOST
            return GuessResult(guess, feedback, current_attempt)

        return GuessResult(guess, feedback, current_attempt)
