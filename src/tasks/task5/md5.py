import struct
from typing import List

from bitarray import bitarray


class MD5:
    _s = (
        7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
        5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
        4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
        6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
    )

    _key = (
        0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
        0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
        0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
        0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
        0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
        0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
        0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
        0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
        0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
        0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
        0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
        0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
        0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
        0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
        0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
        0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
    )

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

    @classmethod
    def hash(cls, text: str) -> int:
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
                    f = (b & c) | (~b & d)
                    k = i
                elif i in range(16, 32):
                    f = (b & d) | (~d & c)
                    k = (5 * i + 1) % 16
                elif i in range(32, 48):
                    f = b ^ c ^ d
                    k = (3 * i + 5) % 16
                else:
                    f = c ^ (~d | b)
                    k = (7 * i) % 16

                f = (f + a) % (2 ** 32)
                f = (f + words[k]) % (2 ** 32)
                f = (f + cls._key[i]) % (2 ** 32)
                f = cls.__rotate_left(f, cls._s[i])
                f = (f + b) % (2 ** 32)

                a = d
                d = c
                c = b
                b = f

            a0 = (a0 + a) % 2 ** 32
            b0 = (b0 + b) % 2 ** 32
            c0 = (c0 + c) % 2 ** 32
            d0 = (d0 + d) % 2 ** 32

        a0 = int.from_bytes(struct.pack('>I', a0), byteorder='little')
        b0 = int.from_bytes(struct.pack('>I', b0), byteorder='little')
        c0 = int.from_bytes(struct.pack('>I', c0), byteorder='little')
        d0 = int.from_bytes(struct.pack('>I', d0), byteorder='little')

        return int(f'{format(a0, "08x")}{format(b0, "08x")}{format(c0, "08x")}{format(d0, "08x")}', 16)
