# Results and Interpretation

The aggregate measurements in `results/reported-results.csv` were supplied by
the original study and its author. They have not been reconstructed from raw
per-trial samples in this repository.

| Runtime | Curve | Average (s) | Observed range (s) |
|---|---|---:|---:|
| Python | MyCurve | 0.1003544 | 0.0943864-0.1370574 |
| Python | Ed25519 | 0.0982963 | 0.0924462-0.1092304 |
| C++17 | MyCurve | 0.0151267 | 0.0125334-0.0212813 |
| C++17 | Ed25519 | 0.0148832 | 0.0116208-0.0219940 |

MyCurve was approximately 2.09% slower than Ed25519 in Python and 1.64% slower
in the reported C++17 run. These ratios describe this arithmetic model and
environment only. They do not establish production signing throughput.

The lower C++17 times are expected because compiled native code removes much
of the interpreter overhead. Cross-runtime speedup must not be attributed to
the curve parameters themselves.

