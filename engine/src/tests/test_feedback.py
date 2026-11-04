import pytest
from engine.src.wordle.feedback import get_feedback


@pytest.mark.parametrize("answer,guess,expected", [("apple", "allee",
                                                    (2, 1, 0, 0, 2)),
                                                   ("crane", "slate",
                                                    (0, 0, 2, 0, 2)),
                                                   ("crane", "crane",
                                                    (2, 2, 2, 2, 2)),
                                                   ("crane", "rebut",
                                                    (1, 1, 0, 0, 0)),
                                                   ("cigar", "civic",
                                                    (2, 2, 0, 0, 0)),
                                                   ("level", "hello",
                                                    (0, 2, 1, 1, 0)),
                                                   ("eerie", "eeeee",
                                                    (2, 2, 0, 0, 2)),
                                                   ("abbey", "babes",
                                                    (1, 1, 2, 2, 0)),
                                                   ("aaaaa", "aaaab",
                                                    (2, 2, 2, 2, 0)),
                                                   ("abcde", "fghij",
                                                    (0, 0, 0, 0, 0))])
def test_feedback(answer, guess, expected):
    assert get_feedback(answer, guess) == expected


@pytest.mark.parametrize("answer,guess", [('hello', 'cat'), ('hello', 'python'), ('hello', 'ab12e'), ('hello', 'helo!'), ('hello', '')])
def test_feedback_negative(answer, guess):
    with pytest.raises(ValueError):
        get_feedback(answer, guess)
