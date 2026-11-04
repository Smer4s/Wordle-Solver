from game import WordleGame, GameStatus, GameEndedError
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
WORDS_PATH = os.path.join(dir_path, '../data/allowed_words.txt')
MAX_ATTEMPTS = 6


def main():
    print('Hello to WORDLE Game!')

    allowed_words = read_words(WORDS_PATH)
    game = WordleGame(allowed_words, max_attempts=MAX_ATTEMPTS)

    print('The WORD was guessed. Now it\'s your turn to make a GUESS')

    while game.get_status() == GameStatus.IN_PROGRESS:
        current_attempt = game.get_attempts()
        guess = input(f'Guess #{current_attempt}: ')
        try:
            result = game.submit_guess(guess)
            print('Feedback:', result.feedback)
            if game.get_status() != GameStatus.IN_PROGRESS:
                if game.get_status() == GameStatus.WON:
                    print('You WON in', current_attempt, 'attempts!')
                else:
                    print('You LOST. The WORD was:', game.get_answer())
        except ValueError as e:
            msg = ' '.join([str(arg) for arg in e.args])
            print(f'ERROR: {msg}')
        except GameEndedError as e:
            print('Game ended!', e.message)
            break


def read_words(path: str) -> set[str]:
    with open(path) as f:
        return set((line.strip() for line in f.readlines()))


if __name__ == "__main__":
    main()
