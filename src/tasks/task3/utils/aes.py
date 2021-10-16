from copy import copy
from typing import List, Tuple

from bitarray import bitarray
from bitarray.util import ba2int, int2ba
from multimethod import multimethod

from src.tasks.task3.config import INV_MIX_COLUMNS_MATRIX, INV_SBOX, MIX_COLUMNS_MATRIX, RCON, SBOX
from src.tasks.task3.utils.bitarray_utils import split_by_block_length

Word = List[int]
Block = List[Word]


def bits_to_block(bits: bitarray) -> Block:
    blocks = split_by_block_length(bits, 8)

    state = []
    for i in range(0, len(blocks), 4):
        state.append(list(map(ba2int, blocks[i : i + 4])))

    return state


def block_to_bits(block: Block) -> bitarray:
    return sum([int2ba(number, length=8) for row in block for number in row], start=bitarray())


def sub_byte(byte: int, sbox: Tuple[Tuple[int]]) -> int:
    row_number = byte // 16
    column_number = byte % 16
    return sbox[row_number][column_number]


@multimethod
def sub_bytes(word: Word, is_inverse: bool = False) -> None:
    s_box = INV_SBOX if is_inverse else SBOX
    for index, byte in enumerate(word):
        word[index] = sub_byte(byte, s_box)


@multimethod
def sub_bytes(state: Block, is_inverse: bool = False) -> None:  # noqa: WPS440, F811
    for word in state:
        sub_bytes(word, is_inverse)


def _transpose(state: Block) -> Block:
    transposed_state = [[] for _ in range(len(state[0]))]
    for row in state:
        for index, byte in enumerate(row):
            transposed_state[index].append(byte)

    return transposed_state


def shift_rows(state: Block, is_inverse: bool = False) -> Block:
    rows = _transpose(state)
    for index, row in enumerate(rows):
        if is_inverse:
            rows[index] = row[-index:] + row[:-index]
        else:
            rows[index] = row[index:] + row[:index]

    return _transpose(rows)


def mix_column(word: Word, mix_columns_matrix: Tuple[Tuple[Tuple[int]]]) -> None:
    old_word = copy(word)
    for i, row in enumerate(mix_columns_matrix):
        word[i] = 0
        for j, table in enumerate(row):
            word[i] ^= table[old_word[j]]


def mix_columns(state: Block, is_inverse: bool = False):
    mix_columns_matrix = INV_MIX_COLUMNS_MATRIX if is_inverse else MIX_COLUMNS_MATRIX
    for word in state:
        mix_column(word, mix_columns_matrix)


def add_round_key(state: Block, key: Block) -> None:
    for column_index, word in enumerate(state):
        for row_index, _ in enumerate(word):
            state[column_index][row_index] ^= key[column_index][row_index]


def rot_word(word: Word) -> Word:
    return word[1:] + word[:1]


def xor_words(first: Word, second: Word) -> Word:
    return [f ^ s for f, s in zip(first, second)]


def _expand_key(key: Block, index: int) -> Block:
    new_key = copy(key)

    temp = rot_word(new_key[3])
    sub_bytes(temp)
    temp = xor_words(temp, RCON[index])
    new_key[0] = xor_words(new_key[0], temp)

    for i in range(1, 4):
        new_key[i] = xor_words(new_key[i], new_key[i - 1])

    return new_key


def generate_keys(key: Block) -> List[Block]:
    keys = [key]
    for i in range(10):
        keys.append(_expand_key(keys[i], i))
    return keys
