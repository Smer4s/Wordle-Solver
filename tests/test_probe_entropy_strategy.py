import pytest
from wordle_solver.strategies.probe_entropy import ProbeEntropyStrategy


def test_probe_guess_over_candidates():
    candidates = {
        "bight", "fight", "light", "might",
        "night", "right", "sight", "tight",
    }

    allowed_guesses = candidates | {"turns"}

    strategy = ProbeEntropyStrategy(allowed_guesses)

    assert strategy.calculate_entropy(
        "turns", candidates
    ) == pytest.approx(2.0)

    assert strategy.calculate_entropy(
        "bight", candidates
    ) == pytest.approx(0.543564, abs=1e-5)

    assert strategy.select_guess(candidates) == "turns"


def test_probe_single_candidate():
    candidates = {"bight"}
    allowed_guesses = {"bight", "turns"}

    strategy = ProbeEntropyStrategy(allowed_guesses)

    assert strategy.select_guess(candidates) == "bight"


def test_probe_candidates_only():
    candidates = {
        "bight", "fight", "light", "might",
        "night", "right", "sight", "tight",
    }

    strategy = ProbeEntropyStrategy(candidates)

    assert strategy.select_guess(candidates) == "bight"


def test_validation():
    with pytest.raises(ValueError):
        ProbeEntropyStrategy(set())
    with pytest.raises(ValueError):
        ProbeEntropyStrategy({'abc12'})
    with pytest.raises(ValueError):
        ProbeEntropyStrategy({'abcdef'})
    with pytest.raises(ValueError):
        ProbeEntropyStrategy('set')

    candidates = {"bight"}
    allowed_guesses = {"turns"}
    strategy = ProbeEntropyStrategy(allowed_guesses)

    with pytest.raises(ValueError):
        strategy.select_guess(candidates)
    
    with pytest.raises(ValueError):
        strategy.select_guess(set())


def test_candidate_priority():
    candidates = {"bight", "fight"}

    allowed_guesses = {
        "aback", "bight", "fight"
    }
    
    strategy = ProbeEntropyStrategy(allowed_guesses)
    
    assert strategy.select_guess(candidates) == 'bight'
