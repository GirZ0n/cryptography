from copy import copy
from typing import List, Tuple

import numpy as np
import pandas as pd
from bitarray import bitarray
from bitarray.util import ba2hex, ba2int, hex2ba, int2ba
from multimethod import multimethod

from src.tasks.task3.config import INV_MIX_COLUMNS_MATRIX, INV_SBOX, MIX_COLUMNS_MATRIX, RCON, SBOX
from src.tasks.task3.utils.bitarray_utils import (
    convert_hex_key_to_bitarray,
    convert_text_to_bitarray,
    split_by_block_length,
)

Word = List[int]
Block = List[Word]
Key = List[List[int]]


def bits_to_block(bits: bitarray) -> Block:
    blocks = split_by_block_length(bits, 8)

    state = []
    for i in range(0, len(blocks), 4):
        state.append(list(map(ba2int, blocks[i : i + 4])))

    return state


def block_to_bits(block: Block) -> Block:
    result = bitarray()
    for row in block:
        for elem in row:
            result += int2ba(elem, length=8)
    return result


def sub_byte(byte: int, sbox: Tuple[Tuple[int]]) -> int:
    row_number = byte // 16
    column_number = byte % 16
    return sbox[row_number][column_number]


@multimethod
def sub_bytes(state: Block, is_inverse: bool = False) -> None:
    s_box = INV_SBOX if is_inverse else SBOX

    new_state = state
    for column_index, word in enumerate(state):
        for row_index, byte in enumerate(word):
            new_state[column_index][row_index] = sub_byte(byte, s_box)


@multimethod
def sub_bytes(word: Word, is_inverse: bool = False) -> None:
    s_box = INV_SBOX if is_inverse else SBOX

    for index, byte in enumerate(word):
        word[index] = sub_byte(byte, s_box)


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
        result = 0
        for j, table in enumerate(row):
            result ^= table[old_word[j]]
        word[i] = result


def mix_columns(state: Block, is_inverse: bool = False):
    mix_columns_matrix = INV_MIX_COLUMNS_MATRIX if is_inverse else MIX_COLUMNS_MATRIX
    for word in state:
        mix_column(word, mix_columns_matrix)


def add_round_key(state: Block, key: Key) -> None:
    for column_index, word in enumerate(state):
        for row_index, _ in enumerate(word):
            state[column_index][row_index] ^= key[column_index][row_index]


# def x_time(byte: bitarray) -> bitarray:
#     if byte & bitarray('10000000'):
#         return ((byte << 1) ^ bitarray('00011011')) & bitarray('11111111')
#
#     return byte << 1
#
#
# def mix_columns(state: Block, is_inverse: bool = False) -> None:
#     if is_inverse:
#         for i in range(4):
#             u = x_time(x_time(state[0][i] ^ state[2][i]))
#             v = x_time(x_time(state[1][i] ^ state[3][i]))
#             state[0][i] ^= u
#             state[1][i] ^= v
#             state[2][i] ^= u
#             state[3][i] ^= v
#
#     for i in range(len(state[0])):
#         t = state[0][i] ^ state[1][i] ^ state[2][i] ^ state[3][i]
#         u = state[0][i]
#         state[0][i] ^= t ^ x_time(state[0][i] ^ state[1][i])
#         state[1][i] ^= t ^ x_time(state[1][i] ^ state[2][i])
#         state[2][i] ^= t ^ x_time(state[2][i] ^ state[3][i])
#         state[3][i] ^= t ^ x_time(state[3][i] ^ u)


def rot_word(word: Word) -> Word:
    return word[1:] + word[:1]


def xor_words(first: Word, second: Word) -> Word:
    return [f ^ s for f, s in zip(first, second)]


def _expand_key(key: Block, index: int) -> Key:
    new_key = copy(key)

    temp = rot_word(new_key[3])
    sub_bytes(temp)
    temp = xor_words(temp, RCON[index])
    new_key[0] = xor_words(new_key[0], temp)

    for i in range(1, 4):
        new_key[i] = xor_words(new_key[i], new_key[i - 1])

    return new_key


def generate_keys(key: Key) -> List[Key]:
    keys = [key]
    for i in range(10):
        keys.append(_expand_key(keys[i], i))
    return keys


def _print_list(a, header):
    print(header)
    print(
        pd.DataFrame(np.array([[hex(elem)[2:] for elem in column] for column in a]).T).to_string(
            index=False, header=False
        )
    )
    print()


def encode(text: str, key: str):
    bitstring = convert_text_to_bitarray(text)
    print(ba2hex(bitstring))
    # bitstring = hex2ba('54776F204F6E65204E696E652054776F')
    blocks = split_by_block_length(bitstring, 128)
    states = list(map(bits_to_block, blocks))

    bitkey = convert_hex_key_to_bitarray(key, length=128)
    # bitkey = hex2ba('5468617473206D79204B756E67204675')
    bitkey = bits_to_block(bitkey)
    keys = generate_keys(bitkey)

    # for key in keys:
    #     print(' '.join([hex(elem)[2:] for column in key for elem in column]))

    res = bitarray()
    for i, state in enumerate(states):
        # _print_list(state, f'State 0')

        # _print_list(keys[0], f'Key 0')

        add_round_key(state, keys[0])
        # _print_list(state, f'State 0 (round key)')

        for j in range(1, 10):
            sub_bytes(state)
            # _print_list(state, f'State {j} (sub bytes)')

            state = shift_rows(state)
            # _print_list(state, f'State {j} (shift rows)')

            mix_columns(state)
            # _print_list(state, f'State {j} (mix columns)')

            # _print_list(keys[j], f'Key {j}')

            add_round_key(state, keys[j])
            # _print_list(state, f'State {j} (round bytes)')

        sub_bytes(state)
        # _print_list(state, f'State 10 (sub bytes)')

        state = shift_rows(state)
        # _print_list(state, f'State 10 (shift rows)')

        # _print_list(keys[-1], f'Key 10')

        add_round_key(state, keys[-1])
        # _print_list(state, f'State 10 (round key)')

        res += block_to_bits(state)

    print()

    # for r in res:
    #     print(' '.join([hex(elem)[2:] for column in r for elem in column]))

    return res


def decode(bitstring: bitarray, key: str) -> bitarray:
    # bitstring = hex2ba('29c3505f571420f6402299b31a02d73a')
    blocks = split_by_block_length(bitstring, 128)
    states = list(map(bits_to_block, blocks))

    bitkey = convert_hex_key_to_bitarray(key, length=128)
    # bitkey = hex2ba('5468617473206D79204B756E67204675')
    bitkey = bits_to_block(bitkey)

    keys = generate_keys(bitkey)[::-1]

    res = bitarray()
    for i, state in enumerate(states):
        # _print_list(state, f'State 0')

        # _print_list(keys[0], f'Key 0')

        add_round_key(state, keys[0])
        # _print_list(state, f'State 0 (round key)')

        for j in range(1, 10):
            state = shift_rows(state, is_inverse=True)
            # _print_list(state, f'State {j} (shift rows)')

            sub_bytes(state, is_inverse=True)
            # _print_list(state, f'State {j} (sub bytes)')

            # _print_list(keys[j], f'Key {j}')
            add_round_key(state, keys[j])
            # _print_list(state, f'State {j} (round bytes)')

            mix_columns(state, is_inverse=True)
            # _print_list(state, f'State {j} (mix columns)')

        state = shift_rows(state, is_inverse=True)
        # _print_list(state, f'State 10 (shift rows)')

        sub_bytes(state, is_inverse=True)
        # _print_list(state, f'State 10 (sub bytes)')

        # _print_list(keys[-1], f'Key 10')

        add_round_key(state, keys[-1])
        # _print_list(state, f'State 10 (round key)')

        res += block_to_bits(state)

    return res
    # for r in res:
    #     print(' '.join([hex(elem)[2:] for column in r for elem in column]))


if __name__ == '__main__':
    ba = encode('Hello, World!', 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA')
    print(ba2hex(ba))
    res = decode(ba, 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA')
    print(ba2hex(res))
    # inp = '00000001001000110100010101100111100010011010101111001101111011110000000100100011010001010110011110001001101010111100110111101111'
    #
    # res = bits_to_block(bitarray(inp))
    # for row in res:
    #     print(' '.join(map(str, row)))
    # F
    # print()
    #
    # kek = _transpose(res)
    # for row in kek:
    #     print(' '.join(map(str, row)))
    #
    # print()
    #
    # res = shift_rows(res)
    # # for row in res:
    # #     print(' '.join(map(str, row)))
    # #
    # # print()
    #
    # res = _transpose(res)
    # for row in res:
    #     print(' '.join(map(str, row)))
    #
    # print()
