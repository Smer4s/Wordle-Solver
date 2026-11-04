from dataclasses import dataclass, field
from .feedback import validate

@dataclass
class LetterRestriction(object):
    max_count: int = 5
    """Maximum count restrictions for letter to present in candidate. e.g. ``max_count`` = 1 means that candidate MUST contain only MAXIMUM one letter. Default value is 5"""
    min_count: int = 0
    """Minimum count restrictions for letter to present in candidate. e.g. ``min_count`` = 1 means that candidate MUST contain AT LEAST one letter. Default value is 0"""
    must_present: list[int] = field(default_factory=list)
    """0-based indexes for letter to be in candidate. e.g. ``must_present`` = [0, 2] means that candidate MUST contain this letter at these positions"""
    must_absent: list[int] = field(default_factory=list)
    """0-based indexes for letter NOT to be in candidate. e.g. ``must_absent`` = [0, 2] means that candidate MUST NOT contain this letter at these positions"""


@dataclass
class IndexFeedback(object):
    index: int
    feedback: int


class WordleSolver:
    def __init__(self, possible_answers: set[str]) -> None:
        """
        Initialize solver with all possible answers.
        """
        if len(possible_answers) == 0:
            raise ValueError('possible_answers must not be empty')
        for answer in possible_answers:
            validate(answer)
        self._possible_answers = possible_answers.copy()
        self._candidates = self._possible_answers.copy()

    def update(
        self,
        guess: str,
        feedback: tuple[int, ...],
    ) -> None:
        """
        Remove candidates inconsistent with the observation.
        """
        validate(guess)
        WordleSolver._validate_feedback(feedback)
        restrictions = self._get_restrictions(guess, feedback)
        self._apply_restrictions(restrictions)
        print(self._candidates)
        
    @staticmethod
    def _validate_feedback(feedback: tuple[int,...]) -> None:
        if len(feedback) != 5:
            raise ValueError('Expected feedback\'s length to be equal to 5')
        
        for f in feedback:
            if f < 0 or f > 2:
                raise ValueError('Expected feedback\'s values to be in range [0,2]')

    def _apply_restrictions(self, restrictions: dict[str, LetterRestriction]) -> None:
        new_candidates: set[str] = set()

        for candidate in self._candidates:
            if WordleSolver._should_add_candidate(candidate, restrictions):
                new_candidates.add(candidate)
            print(candidate,  new_candidates)

        self._candidates = new_candidates.copy()

    @staticmethod
    def _should_add_candidate(candidate: str, restrictions: dict[str, LetterRestriction]) -> bool:
        for (letter, restriction) in restrictions.items():
            print(candidate, letter, restriction, candidate.count(letter))
            c_count = candidate.count(letter)
            if c_count > restriction.max_count or c_count < restriction.min_count:
                return False
            for i in restriction.must_absent:
                if candidate[i] == letter:
                    return False
            for i in restriction.must_present:
                if candidate[i] != letter:
                    return False

        return True

    @staticmethod
    def _get_restrictions(guess: str, feedback: tuple[int, ...]) -> dict[str, LetterRestriction]:
        letter_dict: dict[str, list[IndexFeedback]
                          ] = WordleSolver._get_letter_dict(guess, feedback)

        restrictions: dict[str, LetterRestriction] = {
            letter: LetterRestriction() for letter in guess}

        for (letter, feedbacks) in letter_dict.items():
            restriction = restrictions[letter]
            (positive, neutral, negative) = (0, 0, 0)
            for f in feedbacks:
                if f.feedback == 2:
                    restriction.must_present.append(f.index)
                    positive += 1
                if f.feedback == 0:
                    restriction.must_absent.append(f.index)
                    negative += 1
                if f.feedback == 1:
                    restriction.must_absent.append(f.index)
                    neutral += 1

            if negative == 0:
                # restriction.max_count = 5
                restriction.min_count = neutral + positive
            else:
                restriction.max_count = restriction.min_count = neutral + positive

        return restrictions

    @staticmethod
    def _get_letter_dict(guess: str, feedback: tuple[int, ...]) -> dict[str, list[IndexFeedback]]:
        result: dict[str, list[IndexFeedback]] = {}

        for i in range(len(feedback)):
            letter = guess[i]
            feedbacks = result.get(letter, [])
            feedbacks.append(IndexFeedback(i, feedback[i]))
            result.update({letter: feedbacks})

        return result

    def get_candidates(self) -> set[str]:
        """
        Return a copy of remaining candidates.
        """
        return self._candidates.copy()

    def reset(self) -> None:
        """
        Restore the original candidate set.
        """
        self._candidates = self._possible_answers.copy()
