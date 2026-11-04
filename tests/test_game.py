import pytest
from random import choice
from src.wordle_solver.game import WordleGame, GameStatus, GameEndedError

MAX_ATTEMPTS = 6

TEST_WORDS = {"crane", "slate", "apple", "grape"}


@pytest.fixture
def get_game() -> WordleGame:
    allowed_words = TEST_WORDS
    return WordleGame(allowed_words, max_attempts=MAX_ATTEMPTS)


def get_wrong_guess(game: WordleGame) -> str:
    wrong_guess: str = choice(list(game.get_allowed_words()))
    answer = game.get_answer()
    while wrong_guess == answer:
        wrong_guess = choice(list(game.get_allowed_words()))

    return wrong_guess


def test_win_first_attempt(get_game):
    guess = get_game.get_answer()
    _ = get_game.submit_guess(guess)
    assert get_game.get_status() == GameStatus.WON
    assert get_game.get_attempts() == 2


def test_loss_at_six_attempts(get_game):
    wrong_guess = get_wrong_guess(get_game)
    try:
        for _ in range(get_game.max_attempts):
            _ = get_game.submit_guess(wrong_guess)

        assert get_game.get_status() == GameStatus.LOST
        assert get_game.get_attempts() == 7
    except GameEndedError:
        pytest.fail('Unexpected GameEndedError')

def test_invalid_guess_does_not_consume_attempt(get_game):
    initial = get_game.get_attempts()
    wrong_word = 'ab123'
    with pytest.raises(ValueError):
        get_game.submit_guess(wrong_word)
    
    assert initial == get_game.get_attempts()
    

def test_win_at_last_attempt(get_game):
    wrong_guess = get_wrong_guess(get_game)
    answer = get_game.get_answer()

    for i in range(get_game.max_attempts):
        if i == 5:
            _ = get_game.submit_guess(answer)
        else:
            _ = get_game.submit_guess(wrong_guess)

    assert get_game.get_status() == GameStatus.WON
    assert get_game.get_attempts() == 7


def test_not_present_word(get_game):
    with pytest.raises(ValueError):
        get_game.submit_guess('aaaaa')


def test_wrong_word_len(get_game):
    with pytest.raises(ValueError):
        get_game.submit_guess('aaaaaa')


def test_try_after_game_end(get_game):
    wrong_guess = get_wrong_guess(get_game)
    for _ in range(get_game.max_attempts):
        _ = get_game.submit_guess(wrong_guess)

    with pytest.raises(GameEndedError):
        get_game.submit_guess(wrong_guess)


def test_change_word_set():
    allowed_words = TEST_WORDS
    game = WordleGame(allowed_words, max_attempts=MAX_ATTEMPTS)
    word: str = 'aaaaa'
    allowed_words.add(word)

    assert len(allowed_words) == len(game.get_allowed_words()) + 1
    assert word not in game.get_allowed_words()
