from .cli import WORDS_PATH, read_words
from .game import WordleGame, GameStatus, GuessResult
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
TRIES_COUNT = 2


def pick_random_words(words: list[str], word_count: int) -> set[str]:
    return set(sample(words, word_count))


def game_test():
    words = list(sorted(read_words(WORDS_PATH)))
    word_counts = [5, 10, 20, 50]
    seed(-1)
    allowed_words = pick_random_words(words, 100)

    candidates_list: list[set[str]] = [
        pick_random_words(list(allowed_words), count) for count in word_counts]

    print(f'Allowed Words: {allowed_words}\n')

    strategy_types = [EntropyStrategy, ProbeEntropyStrategy, RiskAwareStrategy]
    # key: str_type, N attempts, words count. value: wins / fails
    results: dict[tuple[type, int, int], tuple[int, int]] = {}
    for i in range(MAX_ATTEMPTS):
        max_attempts = i + 1
        print(f'N attempts: {max_attempts}')
        for candidates in candidates_list:
            print(f'Candidates: {candidates}')
            for answer in candidates:
                print(f'Answer: {answer}')
                for strategy_type in strategy_types:
                    (game, solver) = init_game(
                        allowed_words, candidates, max_attempts, answer)

                    strategy = get_strategy(strategy_type, allowed_words)

                    while game.get_status() == GameStatus.IN_PROGRESS:
                        attempts_left = max_attempts + 1 - game.get_attempts()
                        loop_candidates = solver.get_candidates()
                        if strategy_type == RiskAwareStrategy:
                            guess = strategy.select_guess(
                                loop_candidates, attempts_left)
                        else:
                            guess = strategy.select_guess(loop_candidates)
                        guess_result = game.submit_guess(guess)
                        status = game.get_status()
                        if status != GameStatus.IN_PROGRESS:
                            print(game.get_history())
                            key = (strategy_type, max_attempts, len(candidates))
                            (wins, fails) = results.get(key, (0, 0))
                            if status == GameStatus.WON:
                                wins += 1
                            elif status == GameStatus.LOST:
                                fails += 1
                            results.update({key: (wins, fails)})
                            break
                        solver.update(guess, guess_result.feedback)
                print()
        print()

    print('Win-Rate Results:')
    for (strategy_type, max_attempts, word_count), (wins, fails) in results.items():
        win_rate = (wins / (wins + fails)) * 100

        print(f'N attempts: {max_attempts}')
        print(f'Type: {strategy_type.__name__}')
        print(f'Words: {word_count}')
        print(f'Win-Rate: {win_rate:.0f}%')
        print()


def get_strategy(strategy_type: type, words: set[str]) -> Strategy:
    if strategy_type == EntropyStrategy:
        return EntropyStrategy()
    if strategy_type == ProbeEntropyStrategy:
        return ProbeEntropyStrategy(words)
    if strategy_type == RiskAwareStrategy:
        return RiskAwareStrategy(words)
    raise ValueError()


def init_game(words: set[str], candidates: set[str], attempts_count: int, answer: str) -> tuple[WordleGame, WordleSolver]:
    game = WordleGame(words, max_attempts=attempts_count, answer=answer)
    solver = WordleSolver(candidates)

    return (game, solver)


def main():
    game_test()


if __name__ == "__main__":
    main()
