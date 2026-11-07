import pytest
from wordle_solver.strategies.entropy import EntropyStrategy


def test_basic_entropy():
    candidates = {
        "crane",
        "crate",
        "trace",
        "grace",
        "grape",
    }

    strategy = EntropyStrategy()

    assert pytest.approx(strategy.calculate_entropy(
        "crane", candidates), rel=1e-5) == 1.921928
    assert pytest.approx(strategy.calculate_entropy(
        "crate", candidates), rel=1e-5) == 2.321928
    assert pytest.approx(strategy.calculate_entropy(
        "trace", candidates), rel=1e-5) == 2.321928
    assert pytest.approx(strategy.calculate_entropy(
        "grace", candidates), rel=1e-5) == 1.921928
    assert pytest.approx(strategy.calculate_entropy(
        "grape", candidates), rel=1e-5) == 1.370951


def test_selection_tie_breaking():
    candidates = {
        "crane",
        "crate",
        "trace",
        "grace",
        "grape",
    }

    strategy = EntropyStrategy()

    assert strategy.select_guess(candidates) == "crate"


def test_entropy_duplicate_letters():
    candidates = {
        "apple",
        "ample",
        "apply",
    }
    strategy = EntropyStrategy()

    for candidate in candidates:
        assert pytest.approx(strategy.calculate_entropy(
            candidate, candidates), rel=1e-5) == 1.584963

    assert strategy.select_guess(candidates) == "ample"


def test_entropy_single_candidate():
    strategy = EntropyStrategy()

    assert strategy.calculate_entropy("crane", {"crane"}) == pytest.approx(0.0)
    assert strategy.select_guess({"crane"}) == "crane"


def test_entropy_validation():
    strategy = EntropyStrategy()

    with pytest.raises(ValueError):
        strategy.select_guess(set())
    with pytest.raises(ValueError):
        strategy.select_guess({"bad"})
    with pytest.raises(ValueError):
        strategy.calculate_entropy("apple", set())
    with pytest.raises(ValueError):
        strategy.calculate_entropy("bad", {"apple"})
    with pytest.raises(ValueError):
        strategy.calculate_entropy("bad", {"bad"})


def test_entropy_antisymmetric():
    candidates = {
        "coops", "elmer", "passe", "skied", "spawn"
    }

    strategy = EntropyStrategy()

    assert strategy.select_guess(candidates) == 'passe'

    assert pytest.approx(strategy.calculate_entropy(
        'coops', candidates), rel=1e-5) == 1.921928
    assert pytest.approx(strategy.calculate_entropy(
        "elmer", candidates), rel=1e-5) == 1.921928
    assert pytest.approx(strategy.calculate_entropy(
        "passe", candidates), rel=1e-5) == 2.321928
    assert pytest.approx(strategy.calculate_entropy(
        "skied", candidates), rel=1e-5) == 2.321928
    assert pytest.approx(strategy.calculate_entropy(
        "spawn", candidates), rel=1e-5) == 2.321928


def test_max_entropy():
    strategy = EntropyStrategy()

    assert strategy.select_guess_with_max_entropy({
        "zebra": 2.0,
        "apple": 2.0 - 5e-16,
    }) == "zebra"

    assert strategy.select_guess_with_max_entropy({
        "zebra": 2.0,
        "apple": 2.0,
    }) == "apple"

    assert strategy.select_guess_with_max_entropy({
        "apple": 2.0,
        "zebra": 2.0,
    }) == "apple"
