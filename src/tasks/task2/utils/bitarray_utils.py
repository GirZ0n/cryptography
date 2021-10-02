from typing import List

from bitarray import bitarray
from bitarray.util import hex2ba, zeros


def convert_text_to_bitarray(text: str) -> bitarray:
    array = bitarray()
    array.frombytes(text.encode())
    return array


def convert_hex_key_to_bitarray(hex_key: str, *, length: int) -> bitarray:
    if length <= 0:
        raise ValueError('The length must be greater than zero.')

    ba = hex2ba(hex_key)

    if len(ba) <= length:
        pad = zeros(length - len(ba))
        return pad + ba

    return ba[-length:]


def split_by_block_length(bits: bitarray, block_length: int) -> List[bitarray]:
    blocks = [bits[i : (i + block_length)] for i in range(0, len(bits), block_length)]

    last_block = blocks[-1]
    if len(last_block) != block_length:
        need_to_fill = block_length - len(last_block)
        last_block.extend([0] * need_to_fill)
        blocks[-1] = last_block

    return blocks


def permute(block: bitarray, permutation_table: tuple, bias: int = 1) -> bitarray:
    if min(permutation_table) - bias < 0 or max(permutation_table) - bias >= len(block):
        raise ValueError(
            f'The values in the table of permutations must be in the range from 0 to {len(block) - 1}. '
            f'The current value range with bias: [{min(permutation_table) - bias}, {max(permutation_table) - bias}].',
        )

    return bitarray([block[position - bias] for position in permutation_table])
