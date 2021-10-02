from math import floor
from typing import List

from bitarray import bitarray

from src.tasks.task2.config import FILL_SYMBOL


def convert_text_to_bitarray(text: str) -> bitarray:
    array = bitarray()
    array.frombytes(text.encode())
    return array


def convert_key_to_bitarray(key: str, *, number_of_bits: int, base: int) -> bitarray:
    return bitarray(format(int(key, base), f'0{number_of_bits}b'))[:number_of_bits]


def split_by_block_length(bits: bitarray, block_length: int, fill: str = FILL_SYMBOL) -> List[bitarray]:
    blocks = [bits[i: (i + block_length)] for i in range(0, len(bits), block_length)]

    bit_fill = convert_text_to_bitarray(fill)
    if len(bit_fill) != 8:
        raise ValueError('The bit length of "fill" must be 8.')

    last_block = blocks[-1]
    if len(last_block) != block_length:
        need_to_fill = block_length - len(last_block)
        last_block += bit_fill * floor(need_to_fill / len(bit_fill))
        blocks[-1] = last_block

    return blocks


def permute(block: bitarray, permutation_table: tuple, bias: int = 1) -> bitarray:

    if min(permutation_table) - bias < 0 or max(permutation_table) - bias >= len(block):
        raise ValueError(
            f'The values in the table of permutations must be in the range from 0 to {len(block) - 1}. '
            f'The current value range with bias: [{min(permutation_table) - bias}, {max(permutation_table) - bias}].',
        )

    return bitarray([block[position - bias] for position in permutation_table])
