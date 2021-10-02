from bitarray import bitarray
from bitarray.util import ba2hex

from src.tasks.task2.config import (
    FILL_SYMBOL,
    INITIAL_PERMUTATION,
    KEY_INITIAL_PERMUTATION,
    REVERSED_INITIAL_PERMUTATION,
)
from src.tasks.task2.utils.bitarray_utils import (
    convert_key_to_bitarray,
    convert_text_to_bitarray,
    permute,
    split_by_block_length,
)
from src.tasks.task2.utils.feistel import feistel_transformation
from src.tasks.task2.utils.key_utils import add_additional_bits, generate_subkeys


def encode(text: str, key: str) -> str:
    bitstring = convert_text_to_bitarray(text)
    blocks = split_by_block_length(bitstring, 64, FILL_SYMBOL)
    bitkey = convert_key_to_bitarray(key, number_of_bits=56, base=16)
    extended_key = add_additional_bits(bitkey)
    shuffled_key = permute(extended_key, KEY_INITIAL_PERMUTATION)
    subkeys = generate_subkeys(shuffled_key)

    encrypted_text = bitarray()
    for block in blocks:
        shuffled_block = permute(block, INITIAL_PERMUTATION)

        encrypted_block = shuffled_block
        for i in range(16):
            encrypted_block = feistel_transformation(encrypted_block, subkeys[i])

        encrypted_text += permute(encrypted_block, REVERSED_INITIAL_PERMUTATION)

    return ba2hex(encrypted_text)


if __name__ == '__main__':
    print(encode('qwerty', 'F'))
