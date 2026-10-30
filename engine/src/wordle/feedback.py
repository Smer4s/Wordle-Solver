
def get_feedback(answer: str, guess: str) -> tuple[int, ...]:
    """
    Compare a guess against the hidden word.

    Returns:
        Tuple of five integers:
        0 - absent
        1 - present, wrong position
        2 - correct position

    Raises:
        ValueError: if the input format is invalid.
    """
    validate(guess)
    validate(answer)

    return compare(answer, guess)


def compare(answer: str, guess: str) -> tuple[int, ...]:
    guess = guess.lower()
    answer = answer.lower()
    idx: dict[int, int] = {i: 0 for i in range(len(guess))}
    found_idx: set[int] = set()

    for i in range(len(guess)):
        if guess[i] == answer[i]:
            idx[i] = 2
            found_idx.add(i)

    for i in range(len(guess)):
        if idx[i] != 0:
            continue
        found_index = 0
        try_to_find = True
        while try_to_find:
            found_index = answer.find(guess[i], found_index)
            try_to_find = False
            if found_index == -1:
                continue
            if found_idx.__contains__(found_index) is False:
                idx[i] = 1
                found_idx.add(found_index)
            else:
                found_index += 1
                try_to_find = True

    return tuple(idx.values())


def validate(guess: str) -> None:
    if len(guess) != 5:
        raise ValueError('Guess len is not 5')
    if guess.isalpha() is False:
        raise ValueError('Guess contains not only letters')
