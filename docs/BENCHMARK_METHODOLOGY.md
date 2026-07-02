# Benchmark Methodology

## Compared operation

Both implementations measure scalar multiplication `kG` only. Hashing, key
generation, point encoding, signing, and verification are outside the timed
region.

## Fair-comparison controls

- MyCurve and Ed25519 use the same affine Twisted Edwards formulas.
- Both execute the same 256-iteration scalar loop.
- Each runtime reuses one deterministic scalar set for both curves.
- Results report average, minimum, maximum, and where available median and
  standard deviation.
- A result-dependent sink prevents dead-code elimination.

## Observed range

“Observed runtime range” means `[minimum, maximum]` over measured trials. It is
not a confidence interval, theoretical bound, service-level objective, or
portable performance guarantee.

## Known limitations

The original Python trial count was not recorded. Historical measurements were
provided as aggregate values without raw per-trial samples or full machine
metadata. They are retained for traceability, not presented as independently
reproduced results.

For publication-quality results, record CPU model, OS, compiler/interpreter,
optimization flags, thermal/power settings, warm-up policy, trial order, raw
samples, and commit hash. Run multiple independent processes and report robust
statistics and uncertainty intervals.

