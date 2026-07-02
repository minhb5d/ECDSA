# Reproducible Parameter Generation

This repository separates validation of the historical curve from a new,
deterministic generation policy. Generation v1 does not retroactively prove
how the historical parameters were selected.

## Safe field prime

`tools/generate_safe_prime.py` derives candidates from a domain-separated
SHA-512 hash of a public UTF-8 seed and counter. It accepts the first candidate
for which both `r` and `p = 2r + 1` pass Miller-Rabin, then records the seed and
counter in JSON.

```bash
python tools/generate_safe_prime.py \
  --seed "Custom EdDSA Twisted Edwards Research 2026-07-02 v1" \
  --bits 256 --output parameters/generated-safe-prime-v1.json
```

Miller-Rabin gives probable primes. A final standardized parameter set should
also archive primality certificates from SageMath or PARI/GP.

## Curve and subgroup

`tools/generate_curve.sage` requires SageMath. For each deterministic `d`
candidate it rejects singular choices, maps the Twisted Edwards curve to its
Montgomery model, counts points, requires `#E(Fp) = h*q` with prime `q`, derives
a point from the seed, clears the cofactor, verifies `qG = O`, and records all
parameters and counters.

```bash
sage tools/generate_curve.sage \
  --prime-json parameters/generated-safe-prime-v1.json \
  --seed "Custom EdDSA Twisted Edwards Research 2026-07-02 v1" \
  --a -1 --cofactor 8 --output parameters/generated-curve-v1.json
```

Point counting can take substantial time because many candidates may be
rejected before the requested group structure appears.

## Completeness warning

A common sufficient condition for complete Twisted Edwards addition is that
`a` is a square and `d` is a nonsquare. The historical curve has Legendre
symbols `chi(a) = -1` and `chi(d) = -1`, so that sufficient condition is not
satisfied. Production formulas must therefore characterize exceptional cases
and avoid secret-dependent handling.

## Historical validation

```bash
python tools/validate_parameters.py \
  --output parameters/validation-report.json
```

This confirms the safe-prime and published subgroup relationships while
retaining the need for independent point counting to prove the full order.
