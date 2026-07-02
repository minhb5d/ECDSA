from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "reported-results.csv"
OUTPUT = ROOT / "results" / "benchmark-comparison.png"


def main() -> None:
    with INPUT.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    runtimes = ["Python", "C++17"]
    values = {}
    for curve in ("MyCurve", "Ed25519"):
        values[curve] = [
            float(next(row["average_seconds"] for row in rows
                       if row["runtime"] == runtime and row["curve"] == curve))
            for runtime in runtimes
        ]

    x = np.arange(len(runtimes))
    width = 0.36
    figure, axis = plt.subplots(figsize=(8, 4.8), dpi=160)
    bars = [
        axis.bar(x - width / 2, values["MyCurve"], width, label="MyCurve", color="#1f77b4"),
        axis.bar(x + width / 2, values["Ed25519"], width, label="Ed25519", color="#ff7f0e"),
    ]
    axis.set_title("Scalar multiplication benchmark comparison")
    axis.set_ylabel("Average runtime (seconds)")
    axis.set_xticks(x, runtimes)
    axis.set_ylim(0, 0.108)
    axis.legend(loc="upper right")
    for group in bars:
        for bar in group:
            axis.annotate(f"{bar.get_height():.4f}",
                          (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                          xytext=(0, 3), textcoords="offset points",
                          ha="center", va="bottom", fontsize=9)
    figure.tight_layout()
    figure.savefig(OUTPUT, bbox_inches="tight")
    print(OUTPUT)


if __name__ == "__main__":
    main()


