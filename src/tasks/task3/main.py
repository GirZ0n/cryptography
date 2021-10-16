from bitarray import bitarray
from bitarray.util import ba2hex

from src.tasks.task3.utils.aes import (
    add_round_key,
    bits_to_block,
    block_to_bits,
    generate_keys,
    mix_columns,
    shift_rows,
    sub_bytes,
)
from src.tasks.task3.utils.bitarray_utils import (
    convert_hex_key_to_bitarray,
    convert_text_to_bitarray,
    split_by_block_length,
)


def encode(text: str, key: str):
    bitstring = convert_text_to_bitarray(text)
    blocks = split_by_block_length(bitstring, 128)
    states = list(map(bits_to_block, blocks))

    bitkey = convert_hex_key_to_bitarray(key, length=128)
    bitkey = bits_to_block(bitkey)
    keys = generate_keys(bitkey)

    res = bitarray()
    for i, state in enumerate(states):
        add_round_key(state, keys[0])

        for j in range(1, 10):
            sub_bytes(state)
            state = shift_rows(state)
            mix_columns(state)
            add_round_key(state, keys[j])

        sub_bytes(state)
        state = shift_rows(state)
        add_round_key(state, keys[-1])

        res += block_to_bits(state)

    return res


def decode(bitstring: bitarray, key: str) -> bitarray:
    blocks = split_by_block_length(bitstring, 128)
    states = list(map(bits_to_block, blocks))

    bitkey = convert_hex_key_to_bitarray(key, length=128)
    bitkey = bits_to_block(bitkey)

    keys = generate_keys(bitkey)[::-1]

    res = bitarray()
    for i, state in enumerate(states):
        add_round_key(state, keys[0])

        for j in range(1, 10):
            state = shift_rows(state, is_inverse=True)
            sub_bytes(state, is_inverse=True)
            add_round_key(state, keys[j])
            mix_columns(state, is_inverse=True)

        state = shift_rows(state, is_inverse=True)
        sub_bytes(state, is_inverse=True)
        add_round_key(state, keys[-1])

        res += block_to_bits(state)

    return res


if __name__ == '__main__':
    ba = encode('Hello, World!', 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA')
    print(ba2hex(ba))
    res = decode(ba, 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA')
    print(ba2hex(res))
