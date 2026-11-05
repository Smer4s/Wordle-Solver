
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
        letter_dict: dict[str, int] = {letter: 0 for letter in word}

        for candidate in candidates:
            for (letter, freq) in letter_dict.items():
                if letter in candidate:
                    freq += 1

                letter_dict.update({letter: freq})

        return sum(letter_dict.values())

    def score_words(self, candidates: str) -> dict[str, int]:
        scores = {word: self.score_word(word, candidates)
                  for word in candidates}

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

        sorted_scores = {letter: score for letter, score in sorted(
            scores.items(), key=lambda item: (-item[1], item[0]))}
        return list(sorted_scores.keys())[0]
