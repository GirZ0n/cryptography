from collections import Counter
from math import floor, sqrt
from typing import List, Set, Tuple


def get_lengths(ciphertext: str, segment_length: int) -> List[int]:
    lengths = []
    for i in range(len(ciphertext) - segment_length + 1):
        for j in range(i + 1, len(ciphertext) - segment_length + 1):
            if ciphertext[i:(i + segment_length)] == ciphertext[j:(j + segment_length)]:
                lengths.append(j - i)

    return lengths


def get_divisors(number: int) -> Set[int]:
    divisors = set()
    for i in range(1, floor(sqrt(number) + 1)):
        if number % i == 0:
            divisors.add(i)
            divisors.add(number // i)

    return divisors


def find_possible_key_lengths(ciphertext: str, segment_length: int = 2, top: int = 10) -> List[Tuple[int, int]]:
    lengths = get_lengths(ciphertext, segment_length)

    counter = Counter()
    for length in lengths:
        divisors = get_divisors(length)
        counter.update(divisors)

    return counter.most_common(top)


def main() -> None:
    with open('input.txt') as f:
        possible_key_lengths = find_possible_key_lengths(f.read(), 3)

    for key_length, number in possible_key_lengths:
        print(f'{key_length}: {number}')


if __name__ == '__main__':
    main()
