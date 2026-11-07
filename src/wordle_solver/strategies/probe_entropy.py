from .strategy import Strategy
from .entropy import EntropyStrategy


class ProbeEntropyStrategy(Strategy):

    def __init__(
            self,
            allowed_guesses: set[str]):
        self._allowed_guesses = allowed_guesses.copy()

    def calculate_entropy(
        self,
        guess: str,
        candidates: set[str],
    ) -> float:
        entropyStrategy = EntropyStrategy()

        return entropyStrategy.calculate_entropy(guess, candidates)

    def select_guess(
        self,
        candidates: set[str],
    ) -> str:
        entropyStrategy = EntropyStrategy()
        
        if not candidates.issubset(self._allowed_guesses):
            raise ValueError("Expected candidates to be in allowed guesses")
        
        entropies = entropyStrategy.calculate_entropies(self._allowed_guesses)

        guess = entropyStrategy.select_guess_with_max_entropy(entropies)
        
        guess_entropy = entropies[guess]
        
        for (word, entropy) in entropies.items():
            if entropy == guess_entropy and word in candidates:
                if guess in candidates and word < guess:
                    guess = word
            
        return guess

