from .cli import WORDS_PATH, MAX_ATTEMPTS, read_words
from .game import WordleGame, GameStatus
from .solver import WordleSolver
from .strategies import FrequencyStrategy
from time import perf_counter


def benchmark():
    print('COUNT', 'TIME (ms)')
    counts = [10, 100, 200, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
    for count in counts:
        allowed_words = read_words(WORDS_PATH, count)
        solver = WordleSolver(allowed_words)
        strategy = FrequencyStrategy()
        candidates = solver.get_candidates()
        start_time = perf_counter()
        _ = strategy.select_guess(candidates)
        end_time = perf_counter()

        print(count, "{:.2f}".format((end_time - start_time)*1000))


def main():
    allowed_words = read_words(WORDS_PATH)
    print('Read:', len(allowed_words), 'words')
    game = WordleGame(allowed_words, max_attempts=MAX_ATTEMPTS)
    print('Started game with', MAX_ATTEMPTS, 'attempts')
    solver = WordleSolver(allowed_words)
    print('Initialized solver with', len(allowed_words), 'words')
    strategy = FrequencyStrategy()

    for _ in range(MAX_ATTEMPTS):
        candidates = solver.get_candidates()
        start_time = perf_counter()
        guess = strategy.select_guess(candidates)
        print('Attempt number:', game.get_attempts(), 'Got', len(candidates),
              'candidates from solver.', 'Selected guess:', guess, 'in', perf_counter() - start_time, 's')
        result = game.submit_guess(guess)
        print('Feedback:', result.feedback, 'Guess:', guess)
        status = game.get_status()
        if status != GameStatus.IN_PROGRESS:
            print('Game ended with status:', status, 'The word was:',
                  game.get_answer())
            break
        solver.update(guess, result.feedback)


if __name__ == "__main__":
    main()
