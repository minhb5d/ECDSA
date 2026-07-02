"""Educational EdDSA-style arithmetic for the custom Twisted Edwards curve.

The scalar loop has regularized control flow, but Python big integers are not
constant-time. This module is for validation and reproducible research only.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import secrets
from typing import Tuple

Point = Tuple[int, int]
IDENTITY: Point = (0, 1)
SCALAR_BITS = 256


@dataclass(frozen=True)
class Curve:
    name: str
    p: int
    a: int
    d: int
    q: int
    h: int
    g: Point


def load_curves() -> dict[str, Curve]:
    root = Path(__file__).resolve().parents[2]
    raw = json.loads((root / "parameters" / "curves.json").read_text(encoding="utf-8-sig"))
    curves = {}
    for key, item in raw.items():
        p = int(item["p"])
        curves[key] = Curve(
            name=item["name"],
            p=p,
            a=int(item["a"]) % p,
            d=int(item["d"]) % p,
            q=int(item["q"]),
            h=int(item["h"]),
            g=(int(item["gx"]), int(item["gy"])),
        )
    return curves


def inverse(value: int, curve: Curve) -> int:
    return pow(value % curve.p, curve.p - 2, curve.p)


def point_add(left: Point, right: Point, curve: Curve) -> Point:
    x1, y1 = left
    x2, y2 = right
    p = curve.p
    product = curve.d * x1 * x2 * y1 * y2 % p
    x3 = (x1 * y2 + y1 * x2) * inverse(1 + product, curve) % p
    y3 = (y1 * y2 - curve.a * x1 * x2) * inverse(1 - product, curve) % p
    return x3, y3


def select_int(left: int, right: int, bit: int) -> int:
    mask = -(bit & 1)
    return (left & ~mask) | (right & mask)


def select_point(left: Point, right: Point, bit: int) -> Point:
    return select_int(left[0], right[0], bit), select_int(left[1], right[1], bit)


def scalar_multiply(scalar: int, point: Point, curve: Curve) -> Point:
    """Fixed 256-iteration, mask-selection scalar multiplication.

    The Python runtime and bigint operations remain variable-time. The function
    regularizes algorithm-level control flow only.
    """
    result = IDENTITY
    addend = point
    for bit_index in range(SCALAR_BITS):
        candidate = point_add(result, addend, curve)
        result = select_point(result, candidate, (scalar >> bit_index) & 1)
        addend = point_add(addend, addend, curve)
    return result


def is_on_curve(point: Point, curve: Curve) -> bool:
    x, y = point
    p = curve.p
    left = (curve.a * x * x + y * y) % p
    right = (1 + curve.d * x * x * y * y) % p
    return left == right


def hash_to_scalar(data: bytes, curve: Curve) -> int:
    return int.from_bytes(hashlib.sha512(data).digest(), "big") % curve.q


def encode_point(point: Point) -> bytes:
    return point[0].to_bytes(32, "big") + point[1].to_bytes(32, "big")


def keygen(curve: Curve) -> tuple[int, Point]:
    secret = secrets.randbelow(curve.q - 1) + 1
    return secret, scalar_multiply(secret, curve.g, curve)


def sign(message: bytes, secret: int, public: Point, curve: Curve) -> tuple[Point, int]:
    secret_bytes = secret.to_bytes(32, "big")
    nonce = hash_to_scalar(secret_bytes + message, curve)
    nonce_point = scalar_multiply(nonce, curve.g, curve)
    challenge = hash_to_scalar(encode_point(nonce_point) + encode_point(public) + message, curve)
    response = (nonce + challenge * secret) % curve.q
    return nonce_point, response


def verify(message: bytes, signature: tuple[Point, int], public: Point, curve: Curve) -> bool:
    nonce_point, response = signature
    if not (0 <= response < curve.q):
        return False
    if not is_on_curve(nonce_point, curve) or not is_on_curve(public, curve):
        return False
    challenge = hash_to_scalar(encode_point(nonce_point) + encode_point(public) + message, curve)
    left = scalar_multiply(response, curve.g, curve)
    right = point_add(nonce_point, scalar_multiply(challenge, public, curve), curve)
    return left == right


if __name__ == "__main__":
    custom = load_curves()["mycurve"]
    sk, pk = keygen(custom)
    message = b"Custom EdDSA research validation"
    signature = sign(message, sk, pk, custom)
    print(f"curve={custom.name}")
    print(f"G_on_curve={is_on_curve(custom.g, custom)}")
    print(f"qG_identity={scalar_multiply(custom.q, custom.g, custom) == IDENTITY}")
    print(f"signature_valid={verify(message, signature, pk, custom)}")




