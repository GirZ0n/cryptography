from operator import xor
from typing import Callable

from bitarray import bitarray
from bitarray.util import int2ba

from src.tasks.task2.config import BASIC_CONVERSION_TABLES, EXPANSION_TABLE, FILL_SYMBOL, FINAL_PERMUTATION
from src.tasks.task2.utils.bitarray_utils import convert_key_to_bitarray, permute, split_by_block_length


def feistel_function(block: bitarray, key: bitarray) -> bitarray:
    extended_block = permute(block, EXPANSION_TABLE)
    extended_block = xor(extended_block, key)

    encrypted_block = bitarray()
    blocks = split_by_block_length(extended_block, 6, FILL_SYMBOL)
    for index, current_block in enumerate(blocks):
        i = int((bitarray(str(current_block[0])) + bitarray(str(current_block[-1]))).to01(), 2)
        j = int(current_block[1:-1].to01(), 2)
        encrypted_block += int2ba(BASIC_CONVERSION_TABLES[index][i][j], length=4)

    encrypted_block = permute(encrypted_block, FINAL_PERMUTATION)

    return encrypted_block


def feistel_transformation(
    block: bitarray,
    key: bitarray,
    encryption_function: Callable[[bitarray, bitarray], bitarray] = feistel_function,
) -> bitarray:
    if len(block) % 2 != 0:
        raise ValueError('The block must have an even size.')

    left_part, right_part = block[: int(len(block) / 2)], block[int(len(block) / 2) :]

    return right_part + xor(left_part, encryption_function(right_part, key))
