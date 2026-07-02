"""Deterministically derive a probable safe prime from a public seed.

This generator is for reproducible parameter research. Miller-Rabin establishes
probable primality; publication-grade parameter generation should additionally
archive a proof certificate from SageMath, PARI/GP, or another audited tool.
"""

import argparse
import hashlib
import json
from pathlib import Path

BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)
DOMAIN = b"custom-eddsa-safe-prime-v1"


def is_probable_prime(value: int) -> bool:
    if value < 2:
        return False
    for prime in BASES:
        if value % prime == 0:
            return value == prime
    odd_part = value - 1
    shifts = 0
    while odd_part % 2 == 0:
        shifts += 1
        odd_part //= 2
    for base in BASES:
        witness = pow(base, odd_part, value)
        if witness in (1, value - 1):
            continue
        for _ in range(shifts - 1):
            witness = pow(witness, 2, value)
            if witness == value - 1:
                break
        else:
            return False
    return True


def candidate_from_seed(seed: bytes, counter: int, bits: int) -> int:
    output = bytearray()
    block = 0
    while len(output) * 8 < bits:
        output.extend(hashlib.sha512(
            DOMAIN + len(seed).to_bytes(4, "big") + seed
            + counter.to_bytes(8, "big") + block.to_bytes(4, "big")
        ).digest())
        block += 1
    value = int.from_bytes(output, "big") & ((1 << (bits - 1)) - 1)
    return value | (1 << (bits - 2)) | 1


def generate(seed: str, bits: int, start_counter: int = 0):
    if bits < 64:
        raise ValueError("bits must be at least 64")
    seed_bytes = seed.encode("utf-8")
    counter = start_counter
    while True:
        q_safe = candidate_from_seed(seed_bytes, counter, bits)
        p = 2 * q_safe + 1
        if p.bit_length() == bits and is_probable_prime(q_safe) and is_probable_prime(p):
            return {
                "algorithm": "custom-eddsa-safe-prime-v1",
                "hash": "SHA-512",
                "seed_utf8": seed,
                "counter": counter,
                "bits": bits,
                "p": str(p),
                "safe_prime_factor": str(q_safe),
                "checks": {"p_probable_prime": True, "factor_probable_prime": True, "p_equals_2q_plus_1": True},
            }
        counter += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", required=True, help="Public UTF-8 nothing-up-my-sleeve seed")
    parser.add_argument("--bits", type=int, default=256)
    parser.add_argument("--start-counter", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = generate(args.seed, args.bits, args.start_counter)
    encoded = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
