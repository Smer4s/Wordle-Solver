from .strategy import Strategy
from .entropy import EntropyStrategy
from ..feedback import validate


class ProbeEntropyStrategy(Strategy):

    def __init__(
            self,
            allowed_guesses: set[str]):
        if not allowed_guesses:
            raise ValueError('Expected allowed guesses not to be empty')

        if type(allowed_guesses) is not set:
            raise ValueError('Expected allowed guesses to be set')

        for guess in allowed_guesses:
            validate(guess)
        self._allowed_guesses = allowed_guesses.copy()

    def calculate_entropy(
        self,
        guess: str,
        candidates: set[str],
    ) -> float:
        if not candidates.issubset(self._allowed_guesses):
            raise ValueError("Expected candidates to be in allowed guesses")
        if guess not in self._allowed_guesses:
            raise ValueError("Expected guess to be in allowed guesses")

        entropyStrategy = EntropyStrategy()

        return entropyStrategy.calculate_entropy(guess, candidates)

    def select_guess(
        self,
        candidates: set[str],
    ) -> str:
        if not candidates:
            raise ValueError("Expected candidates to not be empty")
        if not candidates.issubset(self._allowed_guesses):
            raise ValueError("Expected candidates to be in allowed guesses")

        if len(candidates) == 1:
            guess = next(iter(candidates))
            return guess

        entropyStrategy = EntropyStrategy()

        entropies: dict[str, float] = dict()
        for guess in self._allowed_guesses:
            feedbacks = entropyStrategy.get_candidate_feedbacks(
                candidates, guess)
            entropy = entropyStrategy.calculate_entropy_feedbacks(
                candidates, feedbacks)

            entropies.update({guess: entropy})

        guess = entropyStrategy.select_guess_with_max_entropy(entropies)

        guess_entropy = entropies[guess]

        for (word, entropy) in entropies.items():
            if (guess_entropy == entropy) and ((guess not in candidates and word in candidates) or (guess in candidates and word in candidates and word < guess)):
                guess = word
                guess_entropy = entropies[guess]

        return guess
