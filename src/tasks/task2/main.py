from bitarray import bitarray

from src.tasks.task2.config import (
    INITIAL_PERMUTATION,
    KEY_INITIAL_PERMUTATION,
    REVERSED_INITIAL_PERMUTATION,
)
from src.tasks.task2.utils.bitarray_utils import (
    convert_hex_key_to_bitarray,
    convert_text_to_bitarray,
    permute,
    split_by_block_length,
)
from src.tasks.task2.utils.feistel import feistel_transformations
from src.tasks.task2.utils.key_utils import add_additional_bits, generate_subkeys


def encode(text: str, key: str) -> bitarray:
    bitstring = convert_text_to_bitarray(text)
    blocks = split_by_block_length(bitstring, 64)
    bitkey = convert_hex_key_to_bitarray(key, length=56)
    extended_key = add_additional_bits(bitkey)
    shuffled_key = permute(extended_key, KEY_INITIAL_PERMUTATION)
    subkeys = generate_subkeys(shuffled_key)

    encrypted_text = bitarray()
    for block in blocks:
        shuffled_block = permute(block, INITIAL_PERMUTATION)
        encrypted_block = feistel_transformations(shuffled_block, subkeys)
        encrypted_text += permute(encrypted_block, REVERSED_INITIAL_PERMUTATION)

    return encrypted_text


def decode(bitstring: bitarray, key: str) -> bitarray:
    blocks = split_by_block_length(bitstring, 64)
    bitkey = convert_hex_key_to_bitarray(key, length=56)
    extended_key = add_additional_bits(bitkey)
    shuffled_key = permute(extended_key, KEY_INITIAL_PERMUTATION)
    subkeys = generate_subkeys(shuffled_key)

    encrypted_text = bitarray()
    for block in blocks:
        shuffled_block = permute(block, INITIAL_PERMUTATION)
        encrypted_block = feistel_transformations(shuffled_block, subkeys[::-1])
        encrypted_text += permute(encrypted_block, REVERSED_INITIAL_PERMUTATION)

    return encrypted_text
