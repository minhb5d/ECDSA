"""Validate the published custom curve and emit an auditable JSON report."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "python"))
sys.path.insert(0, str(ROOT / "tools"))

from eddsa_reference import IDENTITY, is_on_curve, load_curves, scalar_multiply
from generate_safe_prime import is_probable_prime


def legendre(value: int, p: int) -> int:
    symbol = pow(value % p, (p - 1) // 2, p)
    return -1 if symbol == p - 1 else symbol


def validate(curve):
    safe_factor = (curve.p - 1) // 2
    a_symbol = legendre(curve.a, curve.p)
    d_symbol = legendre(curve.d, curve.p)
    group_order = curve.h * curve.q
    trace = curve.p + 1 - group_order
    hasse_bound = 2 * __import__("math").isqrt(curve.p)
    return {
        "curve": curve.name,
        "equation": "a*x^2 + y^2 = 1 + d*x^2*y^2 (mod p)",
        "checks": {
            "p_probable_prime": is_probable_prime(curve.p),
            "p_is_safe_prime": is_probable_prime(safe_factor) and curve.p == 2 * safe_factor + 1,
            "q_probable_prime": is_probable_prime(curve.q),
            "base_point_on_curve": is_on_curve(curve.g, curve),
            "q_times_base_is_identity": scalar_multiply(curve.q, curve.g, curve) == IDENTITY,
            "declared_order_within_hasse_interval": abs(trace) <= hasse_bound,
        },
        "derived": {
            "safe_prime_factor": str(safe_factor),
            "declared_group_order_h_times_q": str(group_order),
            "trace_if_declared_order_is_exact": str(trace),
            "a_legendre_symbol": a_symbol,
            "d_legendre_symbol": d_symbol,
            "complete_affine_formula_sufficient_condition": a_symbol == 1 and d_symbol == -1,
        },
        "warning": (
            "qG=O proves that G has order dividing q, but an independent point count is required "
            "to prove #E(Fp)=h*q. The standard sufficient condition for complete twisted-Edwards "
            "addition (a square, d nonsquare) is not satisfied by the current custom parameters."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate(load_curves()["mycurve"])
    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    if not all(report["checks"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
