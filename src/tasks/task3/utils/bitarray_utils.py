from typing import List

from bitarray import bitarray
from bitarray.util import int2ba


def convert_text_to_bitarray(text: str) -> bitarray:
    array = bitarray()
    array.frombytes(text.encode())
    return array


def convert_hex_key_to_bitarray(hex_key: str, *, length: int) -> bitarray:
    if length <= 0:
        raise ValueError('The length must be greater than zero.')

    int_key = int(hex_key, 16)

    try:
        return int2ba(int_key, length=length)
    except OverflowError:
        return int2ba(int_key)[-length:]


def split_by_block_length(bits: bitarray, block_length: int) -> List[bitarray]:
    blocks = [bits[i : (i + block_length)] for i in range(0, len(bits), block_length)]

    last_block = blocks[-1]
    if len(last_block) != block_length:
        need_to_fill = block_length - len(last_block)
        last_block.extend([0] * need_to_fill)
        blocks[-1] = last_block

    return blocks
