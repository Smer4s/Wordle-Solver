from src.wordle.game import WordleGame, GameStatus, GameEndedError
WORDS_PATH = 'src/data/allowed_words.txt'
MAX_ATTEMPTS = 6


def main():
    print('Hello to WORDLE Game!')

    allowed_words = read_words(WORDS_PATH)
    game = WordleGame(allowed_words, max_attempts=MAX_ATTEMPTS)

    print('The WORD was guessed. Now it\'s your turn to make a GUESS')

    while game.status == GameStatus.IN_PROGRESS:
        guess = input(f'Guess #{game.current_attempt}: ')
        try:
            result = game.submit_guess(guess)
            print('Feedback:', result.feedback)
        except ValueError as e:
            msg = ' '.join([str(arg) for arg in e.args])
            print(f'ERROR: {msg}')
        except GameEndedError as e:
            print('Game ended!', e.message)
            break


def read_words(path: str) -> list[str]:
    with open(path) as f:
        return [line.strip() for line in f.readlines()]


if __name__ == "__main__":
    main()
