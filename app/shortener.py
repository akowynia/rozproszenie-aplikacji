import hashlib
from typing import Optional

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE = len(ALPHABET)


def _to_base62(number: int, length: int) -> str:
    if number == 0:
        return ALPHABET[0] * length
    code = []
    while number:
        code.append(ALPHABET[number % BASE])
        number //= BASE
    return "".join(reversed(code)).zfill(length)[:length]


def generate_short_code_from_number(number: int, length: int = 6) -> str:
    return _to_base62(number, length)


def generate_short_code(long_url: str, length: int = 6, nonce: Optional[int] = None) -> str:
    key = long_url if nonce is None else f"{long_url}#{nonce}"
    digest = hashlib.sha256(key.encode()).digest()
    number = int.from_bytes(digest[:6], byteorder="big")
    return generate_short_code_from_number(number, length)
