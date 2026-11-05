import pytest
from wordle_solver.strategies import FrequencyStrategy


def test_frequency_scoring():
    candidates = {
        "crane",
        "crate",
        "trace",
        "grace",
        "grape",
    }

    strategy = FrequencyStrategy()

    scores = strategy.score_words(candidates)

    assert scores == {"crane": 20, "crate": 21,
                      "trace": 21, "grace": 21, "grape": 18}


def test_select_guess():
    candidates = {
        "crane",
        "crate",
        "trace",
        "grace",
        "grape",
    }

    strategy = FrequencyStrategy()

    assert strategy.select_guess(candidates) == "crate"


def test_duplicate_letters():
    candidates = {
        "apple",
        "ample",
        "apply",
    }

    strategy = FrequencyStrategy()

    scores = strategy.score_words(candidates)

    assert scores == {"apple": 11, "ample": 12, "apply": 10}
    
def test_empty_candidates():
    with pytest.raises(ValueError):
        strategy = FrequencyStrategy()
        strategy.select_guess(set())
        strategy.score_word("apple", set())
        
def test_single_candidate():
    candidates = {
        "crane",
    }

    strategy = FrequencyStrategy()

    assert strategy.select_guess(candidates) == "crane"
    
def test_determinism():
    candidates = {
        "crane",
        "crate",
        "trace",
        "grace",
        "grape",
    }
    
    diff_order_candidates = {
        "trace",
        "grape",
        "crate",
        "grace",
        "crane",
    }

    strategy = FrequencyStrategy()

    assert strategy.score_words(candidates) == strategy.score_words(diff_order_candidates)
    assert strategy.select_guess(candidates) == strategy.select_guess(diff_order_candidates)
