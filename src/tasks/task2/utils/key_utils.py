from typing import Callable, List, Literal, Tuple

from bitarray import bitarray
from bitarray.util import parity

from src.tasks.task2.config import CYCLIC_SHIFT, FILL_SYMBOL, SUBKEY_PERMUTATION
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


def generate_subkeys(shuffled_key: bitarray) -> List[bitarray]:
    subkeys = []
    c_block = shuffled_key[: int(len(shuffled_key) / 2)]
    d_block = shuffled_key[int(len(shuffled_key) / 2) :]
    for i in range(16):
        c_block = cyclic_shift(c_block, CYCLIC_SHIFT[i])
        d_block = cyclic_shift(d_block, CYCLIC_SHIFT[i])
        subkeys.append(permute(c_block + d_block, SUBKEY_PERMUTATION))
    return subkeys
