
class FrequencyStrategy:
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
        
        letter_dict: dict[str, int] = {letter: 0 for letter in word}

        for candidate in candidates:
            for (letter, freq) in letter_dict.items():
                if letter in candidate:
                    freq += 1

                letter_dict.update({letter: freq})

        return sum(letter_dict.values())

    def score_words(self, candidates: list[str]) -> dict[str, int]:
        if len(candidates) == 0:
            raise ValueError("Expected candidates to not be empty")

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
