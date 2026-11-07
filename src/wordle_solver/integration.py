from .cli import WORDS_PATH, MAX_ATTEMPTS, read_words
from .game import WordleGame, GameStatus
from .solver import WordleSolver
from .strategies.strategy import Strategy
from .strategies.frequency import FrequencyStrategy
from .strategies.entropy import EntropyStrategy
from time import perf_counter
from random import randint, seed, sample
from dataclasses import dataclass

TRIES_COUNT = 100
WORD_COUNT = 1000


@dataclass
class BenchmarkResult:
    win_rate: float
    avg_attempts: float
    failures: int
    avg_decision_time: float
    min_attempts: int
    max_attempts: int


def benchmark_loop(strategy: Strategy, tries_count: int, word_count: int, seeds: list[int], words: list[str]) -> BenchmarkResult:
    (min_attempts, max_attempts) = (6, 0)
    (wins, failures) = (0, 0)
    total_attempts: list[float] = []
    decision_times: list[float] = []
    for i in range(tries_count):
        seed = seeds[i]
        (game, solver) = init_game(word_count, words, seed)
        answer: str = ''
        status: GameStatus = GameStatus.IN_PROGRESS
        for _ in range(MAX_ATTEMPTS):
            candidates = solver.get_candidates()
            start_time = perf_counter()
            guess = strategy.select_guess(candidates)
            end_time = perf_counter()
            decision_times.append(end_time - start_time)
            result = game.submit_guess(guess)
            status = game.get_status()
            if status != GameStatus.IN_PROGRESS:
                answer = game.get_answer()
                if status == GameStatus.WON:
                    wins += 1
                    attempts = game.get_attempts() - 1
                    total_attempts.append(attempts)
                    if attempts > max_attempts:
                        max_attempts = attempts
                    if attempts < min_attempts:
                        min_attempts = attempts
                else:
                    failures += 1
                break
            solver.update(guess, result.feedback)

        print(f'{type(strategy).__name__}: try #{i+1} of {TRIES_COUNT} tries ended with status: {status}',
              'Answer:', answer)

    win_rate = wins / tries_count
    avg_decision_time = sum(decision_times) / len(decision_times)
    if len(total_attempts) == 0:
        avg_attempts = 0
    else:
        avg_attempts = sum(total_attempts) / len(total_attempts)

    return BenchmarkResult(win_rate, avg_attempts, failures, avg_decision_time, min_attempts, max_attempts)


def init_game(word_count: int, words: list[str], seed: int) -> tuple[WordleGame, WordleSolver]:
    allowed_words = pick_random_words(words, word_count)

    game = WordleGame(
        allowed_words, max_attempts=MAX_ATTEMPTS, rand_seed=seed)
    solver = WordleSolver(allowed_words)

    return (game, solver)


def pick_random_words(words: list[str], word_count: int) -> set[str]:
    return set(sample(words, word_count))


def winrate_benchmark():
    strategies = [FrequencyStrategy(), EntropyStrategy()]
    seed(-1)
    seeds = [randint(1, 10000) for _ in range(TRIES_COUNT)]
    words = list(read_words(WORDS_PATH))
    results: dict[Strategy, BenchmarkResult] = {}
    for strategy in strategies:
        start_time = perf_counter()
        result = benchmark_loop(strategy, TRIES_COUNT,
                                WORD_COUNT, seeds, words)
        end_time = perf_counter()
        results.update({strategy: result})
        print()
        print('Ended benchmark for:', type(strategy).__name__, )
        print(f'Total benchmark time: {(end_time-start_time):.5f}s')
        print()

    for (strategy, result) in results.items():
        print()
        print('Benchmark result for:', type(strategy).__name__)
        print(f'Loops count: {TRIES_COUNT}')
        print(f'Word count: {WORD_COUNT}')
        print(f'Win rate: {result.win_rate * 100}%')
        print(f'Average attempts: {result.avg_attempts}')
        print(f'Failure count: {result.failures}')
        print(
            f'Average Decision Time of `select_guess`: {result.avg_decision_time:.5f}s')
        print(f'Maximum attempts: {result.max_attempts}')
        print(f'Minimum attempts: {result.min_attempts}')
        print()


def time_benchmark():
    strategies: list[Strategy] = [FrequencyStrategy(), EntropyStrategy()]
    word_counts = [10, 20, 50, 100, 250, 500, 1000, 2000, 3000, 4000, 5000]
    for strategy in strategies:
        print()
        print('Benchmark result for:', type(strategy).__name__)
        print('WORD_COUNT', 'TIME')
        for word_count in word_counts:
            words = read_words(WORDS_PATH, word_count)
            time_diff = 0.0
            start_time = perf_counter()
            strategy.select_guess(words)
            end_time = perf_counter()
            time_diff = end_time - start_time
            print(word_count, format(time_diff, ".4f"))


def main():
    # time_benchmark()
    winrate_benchmark()
    # candidates = {
    #     "bobby",
    #     "bimbo",
    #     "bingo",
    #     "bongo",
    #     "beefy",
    #     "peppy",
    #     "berry",
    #     "biker",
    # }

    # freq = FrequencyStrategy()
    # entr = EntropyStrategy()

    # print(freq.score_words(candidates))
    # print(entr.calculate_entropies(candidates))

    # print(freq.select_guess(candidates))
    # print(entr.select_guess(candidates))


if __name__ == "__main__":
    main()
