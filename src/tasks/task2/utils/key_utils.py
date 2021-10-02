from typing import Callable, List, Literal, Tuple

from bitarray import bitarray
from bitarray.util import parity

from src.tasks.task2.config import CYCLIC_SHIFT, SUBKEY_PERMUTATION
from src.tasks.task2.utils.bitarray_utils import permute, split_by_block_length


def generate_oddity_bit(block: bitarray) -> int:
    return 1 - parity(block)


def add_additional_bits(
    key: bitarray,
    calculate_additional_bit: Callable[[bitarray], int] = generate_oddity_bit,
) -> bitarray:
    if len(key) % 7 != 0:
        raise ValueError('The length of the key must be a multiple of 7.')

    blocks = split_by_block_length(key, 7)

    extended_key = bitarray()
    for block in blocks:
        block.append(calculate_additional_bit(block))
        extended_key += block

    return extended_key


def cyclic_shift(block: Tuple, bias: int, direction: Literal['left', 'right'] = 'left'):
    if bias < 0:
        raise ValueError('Bias must not be negative.')

    if direction == 'right':
        bias = len(block) - bias

    right = block[bias::]
    left = block[:bias:]
    return right + left


def generate_subkeys(key: bitarray) -> List[bitarray]:
    c_block = key[: len(key) // 2]
    d_block = key[len(key) // 2 :]

    subkeys = []
    for bias in CYCLIC_SHIFT:
        c_block = cyclic_shift(c_block, bias)
        d_block = cyclic_shift(d_block, bias)
        subkeys.append(permute(c_block + d_block, SUBKEY_PERMUTATION))

    return subkeys
