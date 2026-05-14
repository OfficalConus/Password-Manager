import base64
import hmac
import hashlib
import struct
import os
import time as time_module


def totp(secret: str, interval: int = 30, digits: int = 6) -> str:
    key = base64.b32decode(secret.upper())
    counter = struct.pack(">Q", int(time_module.time()) // interval)
    h = hmac.new(key, counter, hashlib.sha1).digest()
    offset = h[-1] & 0x0f
    truncated = struct.unpack(">I", h[offset:offset+4])[0] & 0x7fffffff
    return str(truncated)[-digits:].zfill(digits)


def totp_remaining(interval: int = 30) -> int:
    return interval - int(time_module.time()) % interval


def derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000, dklen=32)


def encrypt_data(data: bytes, key: bytes) -> bytes:
    nonce = os.urandom(16)
    expanded = hashlib.pbkdf2_hmac("sha256", key, nonce, 1, dklen=len(data))
    cipher = bytes(a ^ b for a, b in zip(data, expanded))
    return nonce + cipher


def decrypt_data(data: bytes, key: bytes) -> bytes:
    nonce = data[:16]
    cipher = data[16:]
    expanded = hashlib.pbkdf2_hmac("sha256", key, nonce, 1, dklen=len(cipher))
    return bytes(a ^ b for a, b in zip(cipher, expanded))
