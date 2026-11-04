from string import printable


def get_feedback(answer: str, guess: str, allowed_words: set[str] = ()) -> tuple[int, ...]:
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

    validate(guess, allowed_words)
    validate(answer, allowed_words)

    return compare(answer, guess)


def normalize(word: str) -> str:
    return word.lower()


def compare(answer: str, guess: str) -> tuple[int, ...]:
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
            if found_index not in found_idx:
                idx[i] = 1
                found_idx.add(found_index)
            else:
                found_index += 1
                try_to_find = True

    return tuple(idx.values())


def validate(word: str, allowed_words: set[str] = ()) -> None:
    if word.isalpha() is False:
        raise ValueError(f'Word: {word} contains not only letters')
    if normalize(word) != word:
        raise ValueError(f'Word: {word} is not normalized')
    if is_latin(word) is False:
        raise ValueError(f'Word: {word} contains not only latin letters')
    if len(word) != 5:
        raise ValueError(f'Word: {word} len is not 5')
    if len(allowed_words) != 0:
        if word not in allowed_words:
            raise ValueError(f'Word: {word} is not allowed word')


def is_latin(text):
    return not bool(set(text) - set(printable))
