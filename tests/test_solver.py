import pytest
from wordle_solver.solver import WordleSolver

WORDS = {
    "crane",
    "brave",
    "grape",
    "plane",
    "trace",
    "crate",
    "slate",
}


def build_solver(word_list: set[str]) -> WordleSolver:
    solver = WordleSolver(word_list)
    return solver


def test_solver_basic():
    words = {
        "crane",
        "brave",
        "grape",
        "plane",
        "trace",
        "crate",
        "slate",
    }

    solver = build_solver(words)

    solver.update("slate", (0, 0, 2, 0, 2))

    assert solver.get_candidates() == {"crane", "brave", "grape"}


def test_solver_multiple_updates():
    words = {
        "crane",
        "brave",
        "grape",
        "plane",
        "trace",
        "crate",
        "slate",
    }

    solver = build_solver(words)

    solver.update("slate", (0, 0, 2, 0, 2))
    solver.update("crane", (0, 1, 2, 0, 2))

    assert solver.get_candidates() == set()


def test_solver_duplicate_letters():
    words = {
        "apple",
        "ample",
        "addle",
        "angle",
        "allee",
        "barry",
        "cream",
        "allye",
        "aplee",
        "apbye",
        "alpye"
    }

    solver = build_solver(words)

    solver.update("allee", (2, 1, 0, 0, 2))

    assert solver.get_candidates() == {"apple", "ample", "addle", "angle"}


def test_solver_reset():
    words = {"crane", "slate", "grape"}

    solver = build_solver(words)
    solver.update("crane", (2, 2, 2, 2, 2))

    assert solver.get_candidates() == {"crane"}

    solver.reset()

    assert solver.get_candidates() == {
        "crane",
        "slate",
        "grape",
    }


def test_solver_encapsulation():
    words = {"crane", "slate"}
    solver = build_solver(words)

    candidates = solver.get_candidates()
    candidates.clear()

    assert solver.get_candidates() == {
        "crane",
        "slate",
    }


@pytest.mark.parametrize("words", [set(), 'abcdefg', 'aaaёa', 'aa12d'])
def test_solver_invalid_initialization(words: set[str]):
    with pytest.raises(ValueError):
        _ = build_solver(words)


def test_solver_invalid_guess():
    words = set({'apple'})
    solver = build_solver(words)
    with pytest.raises(ValueError):
        solver.update('12345', (0, 0, 0, 0, 0))


@pytest.mark.parametrize("feedback", [(1, 2, 3, 4, 5), (0, 0, 0, 0, 0, 0, 0, 0, 0), (True, 0, 0, 0, 0), (0, 0, 0, 0, 0.5), ("0", "0", "0", "0", "0"), None, [0, 0, 0, 0, 0]])
def test_solver_invalid_feedback(feedback: tuple[int, ...]):
    words = set({'apple'})
    solver = build_solver(words)
    with pytest.raises(ValueError):
        solver.update('apple', feedback)


def test_impossible():
    solver = WordleSolver({"crane", "slate"})

    solver.update("crane", (2, 2, 2, 2, 2))
    solver.update("slate", (2, 2, 2, 2, 2))

    assert solver.get_candidates() == set()
