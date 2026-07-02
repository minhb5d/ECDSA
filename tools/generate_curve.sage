#!/usr/bin/env sage
"""Search deterministic Twisted Edwards parameters over a generated prime.

Run with SageMath, not plain CPython. The script counts points independently,
requires #E(Fp) = h*q with prime q, derives a subgroup generator, and records
the seed/counters needed to reproduce the result.
"""

import argparse
import hashlib
import json
from pathlib import Path
from sage.all import EllipticCurve, GF, Integer, is_prime

DOMAIN_D = b"custom-eddsa-curve-d-v1"
DOMAIN_G = b"custom-eddsa-base-point-v1"


def hash_integer(seed, domain, counter, p):
    digest = hashlib.sha512(domain + len(seed).to_bytes(4, "big") + seed
                            + counter.to_bytes(8, "big")).digest()
    return Integer(int.from_bytes(digest, "big")) % p


def point_add(left, right, p, a, d):
    x1, y1 = left
    x2, y2 = right
    product = d * x1 * x2 * y1 * y2
    x_den = 1 + product
    y_den = 1 - product
    if x_den == 0 or y_den == 0:
        raise ZeroDivisionError("exceptional affine addition denominator")
    return ((x1 * y2 + y1 * x2) / x_den,
            (y1 * y2 - a * x1 * x2) / y_den)


def scalar_multiply(scalar, point, p, a, d):
    result = (p(0), p(1))
    addend = point
    while scalar:
        if scalar & 1:
            result = point_add(result, addend, p, a, d)
        addend = point_add(addend, addend, p, a, d)
        scalar >>= 1
    return result


def edwards_order(p, a, d):
    # ax^2+y^2=1+dx^2y^2 maps to Bv^2=u^3+Au^2+u.
    A = 2 * (a + d) / (a - d)
    B = 4 / (a - d)
    unit_b_curve = EllipticCurve(p, [0, A, 0, 1, 0])
    unit_order = Integer(unit_b_curve.cardinality())
    return unit_order if B.is_square() else 2 * Integer(p.order()) + 2 - unit_order


def derive_base_point(seed, start_counter, field, a, d, q, h):
    counter = start_counter
    while True:
        x = field(hash_integer(seed, DOMAIN_G, counter, Integer(field.order())))
        denominator = 1 - d * x * x
        if denominator != 0:
            y_squared = (1 - a * x * x) / denominator
            if y_squared.is_square():
                point = (x, y_squared.sqrt())
                try:
                    generator = scalar_multiply(h, point, field, a, d)
                    if generator != (field(0), field(1)) and scalar_multiply(q, generator, field, a, d) == (field(0), field(1)):
                        return generator, counter
                except ZeroDivisionError:
                    pass
        counter += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prime-json", type=Path, required=True)
    parser.add_argument("--seed", required=True)
    parser.add_argument("--a", type=int, default=-1)
    parser.add_argument("--cofactor", type=int, default=8)
    parser.add_argument("--start-d-counter", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    prime_record = json.loads(args.prime_json.read_text(encoding="utf-8"))
    p_integer = Integer(prime_record["p"])
    if not is_prime(p_integer) or not is_prime((p_integer - 1) // 2):
        raise SystemExit("input p is not a proven safe prime in SageMath")
    field = GF(p_integer)
    a = field(args.a)
    seed = args.seed.encode("utf-8")

    d_counter = args.start_d_counter
    while True:
        d = field(hash_integer(seed, DOMAIN_D, d_counter, p_integer))
        if d != 0 and d != a:
            order = edwards_order(field, a, d)
            if order % args.cofactor == 0:
                q = order // args.cofactor
                if is_prime(q):
                    generator, g_counter = derive_base_point(seed, 0, field, a, d, q, args.cofactor)
                    a_symbol = -1 if not a.is_square() else 1
                    d_symbol = -1 if not d.is_square() else 1
                    result = {
                        "algorithm": "custom-eddsa-curve-search-v1",
                        "hash": "SHA-512",
                        "seed_utf8": args.seed,
                        "prime_record": prime_record,
                        "d_counter": d_counter,
                        "base_point_counter": g_counter,
                        "p": str(p_integer), "a": str(Integer(a)), "d": str(Integer(d)),
                        "q": str(q), "h": args.cofactor,
                        "gx": str(Integer(generator[0])), "gy": str(Integer(generator[1])),
                        "group_order": str(order),
                        "checks": {
                            "p_prime": True, "p_safe_prime": True, "q_prime": True,
                            "order_equals_h_times_q": order == args.cofactor * q,
                            "q_times_g_is_identity": True,
                            "a_legendre_symbol": a_symbol,
                            "d_legendre_symbol": d_symbol,
                            "complete_addition_sufficient_condition": a_symbol == 1 and d_symbol == -1,
                        },
                    }
                    args.output.parent.mkdir(parents=True, exist_ok=True)
                    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
                    print(json.dumps(result, indent=2))
                    return
        d_counter += 1


if __name__ == "__main__":
    main()
