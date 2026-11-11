import pytest
from wordle_solver.strategies.risk_aware import RiskAwareStrategy
from random import choice, seed
from wordle_solver.feedback import get_feedback
from wordle_solver.solver import WordleSolver
from wordle_solver.game import WordleGame, GameStatus


def test_last_try():
    candidates = {"bight", "fight"}

    allowed_guesses = candidates | {"turns"}

    strategy = RiskAwareStrategy(allowed_guesses)

    assert strategy.select_guess(
        candidates, attempts_left=1
    ) == "bight"

    assert strategy.calculate_win_probability(
        "bight", candidates, 1
    ) == pytest.approx(0.5)

    assert strategy.calculate_win_probability(
        "turns", candidates, 1
    ) == pytest.approx(0.0)


def test_two_tries():
    candidates = {
        "bight", "fight", "light", "might",
        "night", "right", "sight", "tight",
    }

    allowed_guesses = candidates | {"turns"}

    strategy = RiskAwareStrategy(allowed_guesses)

    assert strategy.calculate_win_probability(
        "bight", candidates, 2
    ) == pytest.approx(0.25)

    assert strategy.calculate_win_probability(
        "turns", candidates, 2
    ) == pytest.approx(0.625)

    assert strategy.select_guess(
        candidates, 2
    ) == "turns"


def test_last_candidate():
    candidates = {"crane"}

    strategy = RiskAwareStrategy(candidates)

    assert strategy.select_guess(
        candidates, attempts_left=1
    ) == "crane"

    assert strategy.select_guess(
        candidates, attempts_left=2
    ) == "crane"


def test_validation():
    # empty set guesses
    with pytest.raises(ValueError):
        RiskAwareStrategy(set())

    # empty set candidates
    with pytest.raises(ValueError):
        candidates = {"turns"}
        strategy = RiskAwareStrategy(candidates)
        strategy.select_guess(set(), 1)

    # candidate not from guesses
    with pytest.raises(ValueError):
        candidates = {"turns"}
        strategy = RiskAwareStrategy(candidates)
        strategy.select_guess({"bight"}, 1)

    # wrong attempt numbers
    with pytest.raises(ValueError):
        candidates = {"turns"}
        strategy = RiskAwareStrategy(candidates)
        strategy.select_guess(candidates, 0)
    with pytest.raises(ValueError):
        candidates = {"turns"}
        strategy = RiskAwareStrategy(candidates)
        strategy.select_guess(candidates, 7)

    # invalid words
    with pytest.raises(ValueError):
        candidates = {"abcdefg"}
        strategy = RiskAwareStrategy(candidates)
    with pytest.raises(ValueError):
        candidates = {"abc12"}
        strategy = RiskAwareStrategy(candidates)


def test_property_testing_last_try():
    words = {
        "bight", "fight", "light", "might",
        "night", "right", "sight", "tight",
    }

    answer: str = choice(list(words))

    (wins, fails) = (0, 0)

    for word in words:
        if word == answer:
            wins += 1
        else:
            fails += 1

    win_rate = wins / (fails + wins)

    strategy = RiskAwareStrategy(words)

    assert strategy.calculate_win_probability(answer, words, 1) == win_rate


def test_property_testing():
    candidates = {
        "bight", "fight", "light", "might",
        "night", "right", "sight", "tight",
    }

    words = candidates | {"turns"}
    solver = WordleSolver(words)
    strategy = RiskAwareStrategy(words)

    stats: dict[str, tuple[int, int]] = {word: (0, 0) for word in words}

    for answer in candidates:
        for guess in words:
            solver.reset()
            feedback = get_feedback(answer, guess, words)
            if feedback == (2, 2, 2, 2, 2):
                # win
                (wins, fails) = stats[guess]
                wins += 1
                stats.update({guess: (wins, fails)})
                continue
            else:
                solver.update(guess, feedback)
                new_candidates = solver.get_candidates()
                last_guess = min(new_candidates)
                feedback = get_feedback(answer, last_guess, words)
                if feedback == (2, 2, 2, 2, 2):
                    # win
                    (wins, fails) = stats[guess]
                    wins += 1
                    stats.update({guess: (wins, fails)})
                else:
                    # lose
                    (wins, fails) = stats[guess]
                    fails += 1
                    stats.update({guess: (wins, fails)})

    win_rates: dict[str, float] = {
        word: wins / (fails + wins) for (word, (wins, fails)) in stats.items()}

    assert win_rates == {
        "bight": 0.25, "fight": 0.25, "light": 0.25, "might": 0.25,
        "night": 0.25, "right": 0.25, "sight": 0.25, "tight": 0.25, "turns": 0.625
    }

    for (word, win_rate) in win_rates.items():
        assert strategy.calculate_win_probability(
            word, candidates, 2) == win_rate
