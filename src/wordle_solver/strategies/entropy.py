from ..feedback import validate, get_feedback
from math import log2, isclose, fsum
from .strategy import Strategy


class EntropyStrategy(Strategy):
    def calculate_entropy(
        self,
        guess: str,
        candidates: set[str],
    ) -> float:
        """
        Calculate the entropy of the feedback
        distribution for a given guess.
        """

        if len(candidates) == 0:
            raise ValueError("Expected candidates to not be empty")

        validate(guess)
        for candidate in candidates:
            validate(candidate)

        feedbacks = self._get_candidate_feedbacks(candidates, guess)

        entropy = self._calculate_entropy(candidates, feedbacks)

        return entropy

    def _calculate_entropy(self, candidates: set[str], feedbacks: dict[tuple[int, ...], list[str]]):
        freqs: list[float] = [len(group) / len(candidates)
                              for (_, group) in feedbacks.items()]

        entropy = fsum([freq*log2(freq) for freq in freqs])

        entropy = -entropy
        return entropy

    def calculate_entropies(self,
                            candidates: set[str]) -> dict[str, float]:
        if len(candidates) == 0:
            raise ValueError("Expected candidates to not be empty")
        for candidate in candidates:
            validate(candidate)

        entropies: dict[str, float] = dict()
        for guess in candidates:
            feedbacks = self._get_candidate_feedbacks(candidates, guess)
            entropy = self._calculate_entropy(candidates, feedbacks)

            entropies.update({guess: entropy})

        return entropies

    def _get_candidate_feedbacks(self, candidates: set[str], guess: str) -> dict[tuple[int, ...], list[str]]:
        feedbacks: dict[tuple[int, ...], list[str]] = dict()
        for candidate in candidates:
            feedback = get_feedback(candidate, guess)
            group = feedbacks.get(feedback, [])
            group.append(candidate)
            feedbacks.update({feedback: group})

        return feedbacks

    @staticmethod
    def are_almost_equal(a, b, rel_tol=1e-15, abs_tol=1e-15):
        return isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

    def select_guess(
        self,
        candidates: set[str],
    ) -> str:
        """
        Select the guess with maximum entropy.
        """
        if len(candidates) == 0:
            raise ValueError("Expected candidates to not be empty")

        entropies = self.calculate_entropies(candidates)

        return self.select_guess_with_max_entropy(entropies)

    def select_guess_with_max_entropy(
        self,
        entropies: dict[str, float],
    ) -> str:
        if not entropies:
            raise ValueError("Entropies cannot be empty")

        max_pair = next(iter(entropies.items()))

        for guess, entropy in entropies.items():
            if entropy > max_pair[1]:
                max_pair = (guess, entropy)

            elif entropy == max_pair[1] and guess < max_pair[0]:
                max_pair = (guess, entropy)

        return max_pair[0]
