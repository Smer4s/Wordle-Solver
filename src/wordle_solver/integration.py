from .cli import WORDS_PATH, MAX_ATTEMPTS, read_words
from .game import WordleGame, GameStatus
from .solver import WordleSolver
from .strategies.strategy import Strategy
from .strategies.frequency import FrequencyStrategy
from .strategies.entropy import EntropyStrategy
from .strategies.probe_entropy import ProbeEntropyStrategy
from time import perf_counter
from random import randint, seed, sample
from dataclasses import dataclass
from math import fsum

TRIES_COUNT = 10


def pick_random_words(words: list[str], word_count: int) -> set[str]:
    return set(sample(words, word_count))


def time_entropy_benchmark(words: list[str]):
    word_counts = [10, 25, 50]
    strategy = EntropyStrategy()
    print()
    print('Benchmark result for:', type(strategy).__name__)
    print('WORD_COUNT', 'TIME')
    for word_count in word_counts:
        times: list[float] = []
        for _ in range(TRIES_COUNT):
            candidates = set(words[:word_count])
            start_time = perf_counter()
            strategy.select_guess(candidates)
            end_time = perf_counter()
            time_diff = end_time - start_time
            times.append(time_diff)

        avg_time = fsum(times) / len(times)
        print(word_count, format(avg_time, ".4f"))


def time_probe_benchmark(words: list[str]):

    params = [
        (10, 10), (10, 100), (25, 100), (50, 100)]
    print()
    print('Benchmark result for:', ProbeEntropyStrategy.__name__)
    print('WORD_COUNT', 'TIME')
    for (candidates_count, guess_count) in params:
        times: list[float] = []
        for _ in range(TRIES_COUNT):
            allowed_guesses = set(words[:guess_count])
            strategy = ProbeEntropyStrategy(allowed_guesses)
            candidates = set(words[:candidates_count])
            start_time = perf_counter()
            strategy.select_guess(candidates)
            end_time = perf_counter()
            time_diff = end_time - start_time
            times.append(time_diff)

            avg_time = fsum(times) / len(times)
        print((candidates_count, guess_count), format(avg_time, ".4f"))


def time_benchmark():
    seed(-1)
    words = list(read_words(WORDS_PATH))
    random_words = list(pick_random_words(words, 100))
    time_entropy_benchmark(random_words)
    time_probe_benchmark(random_words)


def game_test():
    words = list(read_words(WORDS_PATH))

    entropies_results: list[tuple[GameStatus, int]] = []
    probes_results: list[tuple[GameStatus, int]] = []
    for i in range(TRIES_COUNT):
        random_seed = randint(1, 1000)
        print(f'Iteration #{i+1}:')
        random_words = pick_random_words(words, 1000)
        print()
        print('Started entropy game')
        seed(random_seed)
        entropies_results.append(play_entropy(random_words))
        print()
        print('Started probe game')
        seed(random_seed)
        probes_results.append(play_probe(random_words))
        print()

    print('Entropy results:')
    print_results(entropies_results)
    print()

    print('Probe results:')
    print_results(probes_results)
    print()


def print_results(results: list[tuple[GameStatus, int]]):
    total_games = len(results)
    (wins, failures) = (0, 0)
    win_attempts: list[int] = []
    for result in results:
        if result[0] == GameStatus.WON:
            wins += 1
            win_attempts.append(result[1])
        else:
            failures += 1

    win_rate: float = wins * 100 / total_games
    avg_attempts = sum(win_attempts) / wins
    print('Total games:', total_games)
    print(f'Win-Rate: {win_rate:.1f}%')
    print('Failures:', failures)
    print('Avg attempts (wins):', avg_attempts)


def play_probe(random_words: set[str]) -> tuple[GameStatus, int]:
    strategy = ProbeEntropyStrategy(random_words)
    (game, solver) = init_game(random_words)
    for _ in range(MAX_ATTEMPTS):
        attempt = game.get_attempts()
        candidates = solver.get_candidates()
        guess = strategy.select_guess(candidates)
        result = game.submit_guess(guess)
        status = game.get_status()
        if status != GameStatus.IN_PROGRESS:
            return (status, attempt)
        solver.update(guess, result.feedback)


def play_entropy(random_words: set[str]) -> tuple[GameStatus, int]:
    strategy = EntropyStrategy()
    (game, solver) = init_game(random_words)
    for _ in range(MAX_ATTEMPTS):
        attempt = game.get_attempts()
        candidates = solver.get_candidates()
        guess = strategy.select_guess(candidates)
        result = game.submit_guess(guess)
        status = game.get_status()
        if status != GameStatus.IN_PROGRESS:
            return (status, attempt)
        solver.update(guess, result.feedback)


def init_game(words: set[str],) -> tuple[WordleGame, WordleSolver]:
    game = WordleGame(words, max_attempts=MAX_ATTEMPTS)
    solver = WordleSolver(words)

    return (game, solver)


def main():
    # time_benchmark()
    game_test()


if __name__ == "__main__":
    main()
