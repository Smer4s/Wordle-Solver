from .feedback import validate, get_feedback
from .solver import WordleSolver
from math import log2
from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def select_guess(
        self,
        candidates: set[str],
    ) -> str:
        ...


class FrequencyStrategy(Strategy):
    def score_word(
        self,
        word: str,
        candidates: set[str],
    ) -> int:
        """
        Calculate a frequency-based score.

        Higher score means a better guess.
        """
        if len(candidates) == 0:
            raise ValueError("Expected candidates to not be empty")

        if word not in candidates:
            raise ValueError("Expected word to be in candidates")

        validate(word)
        for candidate in candidates:
            validate(candidate)

        letter_dict: dict[str, int] = {letter: 0 for letter in word}

        for candidate in candidates:
            for (letter, freq) in letter_dict.items():
                if letter in candidate:
                    freq += 1

                letter_dict.update({letter: freq})

        return sum(letter_dict.values())

    def score_words(self, candidates: set[str]) -> dict[str, int]:
        if len(candidates) == 0:
            raise ValueError("Expected candidates to not be empty")

        for candidate in candidates:
            validate(candidate)

        letter_freq: dict[str, int] = {}
        letters: set[str] = set()
        for word in candidates:
            for letter in word:
                letters.add(letter)

        for word in candidates:
            for letter in letters:
                if letter in word:
                    freq = letter_freq.get(letter, 0)
                    freq += 1
                    letter_freq.update({letter: freq})

        scores: dict[str, int] = {}
        for word in candidates:
            score = 0
            for (letter, freq) in letter_freq.items():
                if letter in word:
                    score += freq
            scores.update({word: score})

        return scores

    def select_guess(
        self,
        candidates: set[str],
    ) -> str:
        """
        Select the best next guess.
        """
        if len(candidates) == 0:
            raise ValueError("Expected candidates to not be empty")

        scores = self.score_words(candidates)

        max_score: tuple[str, int] = list(scores.items())[0]

        for (word, score) in scores.items():
            if score > max_score[1]:
                max_score = (word, score)
            elif score >= max_score[1] and word < max_score[0]:
                max_score = (word, score)

        return max_score[0]


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

        if guess not in candidates:
            raise ValueError("Expected word to be in candidates")

        validate(guess)
        for candidate in candidates:
            validate(candidate)

        feedbacks: dict[tuple[int, ...], list[str]] = dict()
        for candidate in candidates:
            feedback = get_feedback(guess, candidate, candidates)
            group = feedbacks.get(feedback, [])
            group.append(candidate)
            feedbacks.update({feedback: group})

        freqs: list[float] = [len(group) / len(candidates)
                              for (_, group) in feedbacks.items()]

        entropy = 0
        for freq in freqs:
            member = freq * log2(freq)
            entropy += member

        entropy = -entropy

        return entropy

    def calculate_entropies(self,
                            candidates: set[str]) -> dict[str, float]:

        entropies: dict[str, float] = dict()
        group_feedbacks = []
        for guess in candidates:
            feedbacks: dict[tuple[int, ...], list[str]] = dict()
            for candidate in candidates:
                feedback = get_feedback(guess, candidate, candidates)
                group = feedbacks.get(feedback, [])
                group.append(candidate)
                feedbacks.update({feedback: group})
            group_feedbacks.append((guess, feedbacks))
            freqs: list[float] = [len(group) / len(candidates)
                                  for (_, group) in feedbacks.items()]

            entropy = 0
            for freq in freqs:
                member = freq * log2(freq)
                entropy += member

            entropy = -entropy

            entropies.update({guess: entropy})

        return entropies

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

        max_pair = (list(candidates)[0], 0.0)

        for (guess, entropy) in entropies.items():
            if entropy > max_pair[1]:
                max_pair = (guess, entropy)
            if entropy == max_pair[1] and guess < max_pair[0]:
                max_pair = (guess, entropy)

        return max_pair[0]
