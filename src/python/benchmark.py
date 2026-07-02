"""Matched scalar-multiplication benchmark for MyCurve and Ed25519."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import random
import statistics
import time

from eddsa_reference import load_curves, scalar_multiply


def benchmark(curve, scalars: list[int]) -> dict[str, float | int | str]:
    timings = []
    sink = 0
    for scalar in scalars:
        started = time.perf_counter_ns()
        result = scalar_multiply(scalar, curve.g, curve)
        timings.append((time.perf_counter_ns() - started) / 1_000_000_000.0)
        sink ^= result[0] ^ result[1]
    return {
        "runtime": "Python",
        "curve": curve.name,
        "trials": len(timings),
        "average_seconds": statistics.fmean(timings),
        "minimum_seconds": min(timings),
        "maximum_seconds": max(timings),
        "median_seconds": statistics.median(timings),
        "stdev_seconds": statistics.pstdev(timings),
        "sink": sink,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260510)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.trials <= 0:
        parser.error("--trials must be positive")

    curves = load_curves()
    rng = random.Random(args.seed)
    scalars = [rng.randrange(1, min(c.q for c in curves.values())) for _ in range(args.trials)]
    rows = [benchmark(curves[key], scalars) for key in ("mycurve", "ed25519")]

    fields = [
        "runtime", "curve", "trials", "average_seconds", "minimum_seconds",
        "maximum_seconds", "median_seconds", "stdev_seconds", "sink",
    ]
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    for row in rows:
        print(
            f"{row['curve']:<10} trials={row['trials']} "
            f"avg={row['average_seconds']:.7f}s "
            f"min={row['minimum_seconds']:.7f}s "
            f"max={row['maximum_seconds']:.7f}s"
        )


if __name__ == "__main__":
    main()

