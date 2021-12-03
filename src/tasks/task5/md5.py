import struct
from typing import List

from bitarray import bitarray

_MODULUS = 2 ** 32


class MD5:
    _s = (
        7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
        5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
        4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
        6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
    )

    _t = (
        0xD76AA478, 0xE8C7B756, 0x242070DB, 0xC1BDCEEE,
        0xF57C0FAF, 0x4787C62A, 0xA8304613, 0xFD469501,
        0x698098D8, 0x8B44F7AF, 0xFFFF5BB1, 0x895CD7BE,
        0x6B901122, 0xFD987193, 0xA679438E, 0x49B40821,
        0xF61E2562, 0xC040B340, 0x265E5A51, 0xE9B6C7AA,
        0xD62F105D, 0x02441453, 0xD8A1E681, 0xE7D3FBC8,
        0x21E1CDE6, 0xC33707D6, 0xF4D50D87, 0x455A14ED,
        0xA9E3E905, 0xFCEFA3F8, 0x676F02D9, 0x8D2A4C8A,
        0xFFFA3942, 0x8771F681, 0x6D9D6122, 0xFDE5380C,
        0xA4BEEA44, 0x4BDECFA9, 0xF6BB4B60, 0xBEBFBC70,
        0x289B7EC6, 0xEAA127FA, 0xD4EF3085, 0x04881D05,
        0xD9D4D039, 0xE6DB99E5, 0x1FA27CF8, 0xC4AC5665,
        0xF4292244, 0x432AFF97, 0xAB9423A7, 0xFC93A039,
        0x655B59C3, 0x8F0CCC92, 0xFFEFF47D, 0x85845DD1,
        0x6FA87E4F, 0xFE2CE6E0, 0xA3014314, 0x4E0811A1,
        0xF7537E82, 0xBD3AF235, 0x2AD7D2BB, 0xEB86D391,
    )

    @classmethod
    def hash(cls, text: str) -> int:  # noqa: WPS231
        bit_text = cls.__text_to_bits(text)
        cls.__expand_bits(bit_text)

        a0 = 0x67452301
        b0 = 0xEFCDAB89
        c0 = 0x98BADCFE
        d0 = 0x10325476

        for block in cls.__split_by_chunk_length(bit_text, 512):
            a = a0
            b = b0
            c = c0
            d = d0

            words = cls.__split_by_chunk_length(block, 32)
            words = [int.from_bytes(word.tobytes(), byteorder='little') for word in words]

            for i in range(64):
                if i in range(16):
                    f = (b & c) | (~b & d)  # noqa: WPS465
                    k = i
                elif i in range(16, 32):
                    f = (b & d) | (~d & c)  # noqa: WPS465
                    k = (5 * i + 1) % 16
                elif i in range(32, 48):
                    f = b ^ c ^ d
                    k = (3 * i + 5) % 16
                else:
                    f = c ^ (~d | b)  # noqa: WPS465
                    k = (7 * i) % 16

                f = (f + a) % _MODULUS
                f = (f + words[k]) % _MODULUS
                f = (f + cls._t[i]) % _MODULUS
                f = cls.__rotate_left(f, cls._s[i])
                f = (f + b) % _MODULUS

                a = d
                d = c
                c = b
                b = f

            a0 = (a0 + a) % _MODULUS
            b0 = (b0 + b) % _MODULUS
            c0 = (c0 + c) % _MODULUS
            d0 = (d0 + d) % _MODULUS

        return cls.__convert_states(a0, b0, c0, d0)

    @staticmethod
    def __text_to_bits(text: str) -> bitarray:
        array = bitarray()
        array.frombytes(text.encode('utf-8'))
        return array

    @staticmethod
    def __expand_bits(bits: bitarray) -> None:
        bits_length = len(bits)
        length_bits = bitarray()
        length_bits.frombytes(struct.pack('<Q', bits_length))

        bits.append(1)

        if len(bits) % 512 <= 448:
            need_to_fill = 448 - len(bits) % 512
        else:
            need_to_fill = 960 - len(bits) % 512  # 960 = 512 + 448

        bits.extend([0] * need_to_fill)

        bits += length_bits

    @staticmethod
    def __split_by_chunk_length(bits: bitarray, block_length: int) -> List[bitarray]:
        return [bits[i: (i + block_length)] for i in range(0, len(bits), block_length)]

    @staticmethod
    def __rotate_left(x: int, n: int) -> int:
        return (x << n) | (x >> (32 - n))

    @staticmethod
    def __convert_states(a: int, b: int, c: int, d: int) -> int:
        a = int.from_bytes(struct.pack('>I', a), byteorder='little')
        b = int.from_bytes(struct.pack('>I', b), byteorder='little')
        c = int.from_bytes(struct.pack('>I', c), byteorder='little')
        d = int.from_bytes(struct.pack('>I', d), byteorder='little')

        return int(f'{format(a, "08x")}{format(b, "08x")}{format(c, "08x")}{format(d, "08x")}', 16)
