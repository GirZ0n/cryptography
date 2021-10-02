from operator import xor
from typing import Callable, List

from bitarray import bitarray
from bitarray.util import int2ba

from src.tasks.task2.config import BASIC_CONVERSION_TABLES, EXPANSION_TABLE, FINAL_PERMUTATION
from src.tasks.task2.utils.bitarray_utils import permute, split_by_block_length


def feistel_function(block: bitarray, key: bitarray) -> bitarray:
    extended_block = permute(block, EXPANSION_TABLE)
    extended_block = xor(extended_block, key)

    encrypted_block = bitarray()
    blocks = split_by_block_length(extended_block, 6)
    for index, current_block in enumerate(blocks):
        i = int(f'{current_block[0]}{current_block[-1]}', 2)
        j = int(current_block[1:-1].to01(), 2)
        encrypted_block += int2ba(BASIC_CONVERSION_TABLES[index][i][j], length=4)

    return permute(encrypted_block, FINAL_PERMUTATION)


def feistel_transformations(
    block: bitarray,
    keys: List[bitarray],
    encryption_function: Callable[[bitarray, bitarray], bitarray] = feistel_function,
) -> bitarray:
    if len(block) % 2 != 0:
        raise ValueError('The block must have an even size.')

    left_part, right_part = block[: len(block) // 2], block[len(block) // 2 :]

    for key in keys:
        left_part, right_part = right_part, xor(left_part, encryption_function(right_part, key))

    return right_part + left_part
