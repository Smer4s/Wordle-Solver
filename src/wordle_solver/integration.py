from .cli import WORDS_PATH, read_words
from .game import WordleGame, GameStatus
from .solver import WordleSolver
from .strategies.strategy import Strategy
from .strategies.risk_aware import RiskAwareStrategy
from .strategies.entropy import EntropyStrategy
from .strategies.probe_entropy import ProbeEntropyStrategy
from time import perf_counter
from random import randint, seed, sample
from dataclasses import dataclass
from math import fsum

MAX_ATTEMPTS = 2
TRIES_COUNT = 100


def pick_random_words(words: list[str], word_count: int) -> set[str]:
    return set(sample(words, word_count))


def game_test():
    words = list(read_words(WORDS_PATH))
    word_counts = [5, 10, 20, 50]

    results: list[tuple[int, type, int, float]] = []
    for z in range(MAX_ATTEMPTS):
        for j in range(len(word_counts)):

            for strategy_type in [EntropyStrategy, ProbeEntropyStrategy, RiskAwareStrategy]:
                (wins, fails) = (0, 0)
                for _ in range(TRIES_COUNT):
                    random_seed = randint(1, 1000)
                    word_count = word_counts[j]
                    random_words = pick_random_words(words, word_count)
                    strategy = get_strategy(strategy_type, random_words)
                    # print(f'Started {strategy_type.__name__} Strategy')
                    seed(random_seed)
                    result = play_with_strategy(random_words, strategy, z + 1)
                    if result[0] == GameStatus.WON:
                        wins += 1
                    if result[0] == GameStatus.LOST:
                        fails += 1
                    if result[0] == GameStatus.IN_PROGRESS:
                        raise ValueError()

                win_rate = wins / (wins + fails)

                result_tuple = (z + 1, strategy_type, word_counts[j], win_rate)
                results.append(result_tuple)

    for (attempts, strategy_type, word_count, win_rate) in results:
        print()
        print(f'Results for {strategy_type.__name__} Strategy:')
        print(f'Attempts left: {attempts}')
        print(f'Words count: {word_count}')
        print(f'Win rate: {win_rate*100:.0f}')


def get_strategy(strategy_type: type, words: set[str]) -> Strategy:
    if strategy_type == EntropyStrategy:
        return EntropyStrategy()
    if strategy_type == ProbeEntropyStrategy:
        return ProbeEntropyStrategy(words)
    if strategy_type == RiskAwareStrategy:
        return RiskAwareStrategy(words)
    raise ValueError()


def play_with_strategy(random_words: set[str], strategy: Strategy, attempts_count: int) -> tuple[GameStatus, int, float, int]:
    (game, solver) = init_game(random_words, attempts_count)
    times: list[float] = []
    for _ in range(MAX_ATTEMPTS):
        attempt = game.get_attempts()
        candidates = solver.get_candidates()
        start_time = perf_counter()
        if type(strategy) == RiskAwareStrategy:
            guess = strategy.select_guess(
                candidates, MAX_ATTEMPTS - (attempt-1))
        else:
            guess = strategy.select_guess(candidates)
        end_time = perf_counter()
        times.append(end_time-start_time)
        result = game.submit_guess(guess)
        status = game.get_status()
        if status != GameStatus.IN_PROGRESS:
            avg_time = fsum(times) / len(times)
            return (status, attempt, avg_time, len(random_words))
        solver.update(guess, result.feedback)


def init_game(words: set[str], attempts_count: int) -> tuple[WordleGame, WordleSolver]:
    game = WordleGame(words, max_attempts=attempts_count)
    solver = WordleSolver(words)

    return (game, solver)


def main():
    game_test()
    # candidates = {
    #     "bight", "fight", "light", "might",
    #     "night", "right", "sight", "tight",
    # }

    # allowed_guesses = candidates | {'turns'}

    # strategy = RiskAwareStrategy(allowed_guesses)

    # print(strategy._calculate_win_probabilities(allowed_guesses, 2))
    
    # strategy = EntropyStrategy()
    
    # print(strategy.calculate_entropies(allowed_guesses))


if __name__ == "__main__":
    main()
