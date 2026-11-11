from .entropy import EntropyStrategy
from .probe_entropy import ProbeEntropyStrategy
from .frequency import FrequencyStrategy
from .strategy import Strategy
from random import choice


class RiskAwareStrategy(Strategy):
    def __init__(
        self,
        allowed_guesses: set[str],
    ):
        self._entropy = EntropyStrategy()
        self._probe_entropy = ProbeEntropyStrategy(allowed_guesses)
        self._allowed_guesses = allowed_guesses.copy()

    def select_guess(
        self,
        candidates: set[str],
        attempts_left: int,
    ) -> str:
        """
        Select a guess based on the remaining
        number of attempts.
        """
        self._validate_attempts(attempts_left)
        self._validate_candidates(candidates)

        if len(candidates) == 1: 
            guess = next(iter(candidates))
            return guess

        guess: str = ''
        match attempts_left:
            case 1: guess = self._pick_random_answer(candidates)
            case 2: guess = self._pick_max_win_probability(candidates, attempts_left)
            case attempts_left if attempts_left in [3, 4, 5, 6]:
                guess = self._probe_entropy.select_guess(candidates)
            case _: raise ValueError("Expected attempts to be in range [1,6]")

        return guess

    def calculate_win_probability(
        self,
        guess: str,
        candidates: set[str],
        attempts_left: int,
    ) -> float:
        """
        Estimate or calculate the probability
        of winning within the remaining attempts.
        """
        self._validate_attempts(attempts_left, max_attempts=2)
        self._validate_candidates(candidates)

        if attempts_left == 1:
            return self._calculate_basic_win_probability(
                candidates, attempts_left, guess)

        # attempts_left is 2

        return self._calculate_probability(candidates, guess)

    # Calculations

    def _calculate_win_probabilities(self, candidates: set[str], attempts_left: int) -> set[tuple[str, float]]:
        self._validate_attempts(attempts_left, 2)

        if attempts_left == 1:
            return self._calculate_basic_win_probability(candidates, attempts_left)

        probs: set[tuple[str, float]] = set()
        for guess in candidates:
            probability = self._calculate_probability(candidates, guess)
            probs.add((guess, probability))

        return probs

    def _calculate_probability(self, candidates: set[str], guess: str) -> float:
        feedbacks = self._entropy.get_candidate_feedbacks(
            candidates, guess)
        k = len(feedbacks.keys())
        n = len(candidates)
        probability = k / n

        return probability

    def _calculate_basic_win_probability(self, candidates: set[str], attempts_left: int, guess: str | None) -> float:
        self._validate_attempts(attempts_left, max_attempts=1)

        if guess is not None and guess not in candidates:
            return 0.0

        return 1 / len(candidates)

    # Choice policy

    def _pick_max_win_probability(self, candidates: set[str], attempts_left: int) -> str:
        probs = self._calculate_win_probabilities(
            self._allowed_guesses, attempts_left)

        (max_guess, max_prob) = next(iter(probs))

        for (guess, probability) in probs:
            replace = False
            if probability > max_prob:
                replace = True
            if probability == max_prob and guess in candidates:
                replace = True
            if guess in candidates == max_guess in candidates:
                if guess < max_guess:
                    replace = True

            if replace:
                (max_guess, max_prob) = (guess, probability)
                
        return max_guess

    def _pick_random_answer(self, candidates: set[str]) -> str:
        return min(candidates)

    # Validation

    def _validate_attempts(self, attempts_left: int, max_attempts: int = 6) -> None:
        if attempts_left > max_attempts or attempts_left < 1:
            raise ValueError(
                f"Expected attempts to be in range [1, {max_attempts}]")

    def _validate_candidates(self, candidates: set[str]) -> None:
        if not candidates:
            raise ValueError("Expected candidates to not be empty")

        if not candidates.issubset(self._allowed_guesses):
            raise ValueError("Expected candidates to be in allowed guesses")
