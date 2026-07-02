# Side-Channel Analysis

## Threat model

An attacker may observe execution time, cache behavior, branch prediction,
memory access patterns, power consumption, or electromagnetic emissions while
a secret scalar is processed. The most obvious vulnerable pattern is:

```text
while k > 0:
    if k & 1:
        R = R + A
```

Its loop length and number of additions depend on secret scalar bits.

## What this repository improves

The Python and C++17 reference functions always execute 256 iterations. Each
iteration calculates `candidate = R + A`, then selects `R` or `candidate` with
a mask. There are no source-level scalar-dependent branches or table indices
in the scalar loop.

```text
R = identity
A = G
for i = 0..255:
    candidate = R + A
    R = mask_select(R, candidate, bit(k, i))
    A = A + A
```

This is best described as **fixed-loop, mask-selection control flow**.

## What is not guaranteed

The repository does not claim complete constant-time arithmetic:

- Python `int` and Boost `cpp_int` use variable-size representations.
- multiplication, reduction, and allocation costs can depend on operands.
- affine point addition performs modular inversions.
- language runtimes and compilers may transform source-level mask operations.
- no cache, power, electromagnetic, or compiler-assembly audit is included.

Consequently, timing benchmarks cannot prove absence of side channels.

## Production roadmap

A hardened implementation should use fixed-width limbs, branch-free carry and
borrow handling, constant-time modular reduction, projective or extended
coordinates to avoid per-addition inversion, constant-time conditional moves,
fixed-window tables with constant-time lookup, scalar blinding where suitable,
zeroization, and assembly inspection on every supported target.

Validation should include dudect-style timing tests, known-answer tests,
invalid-point and low-order-point tests, sanitizers, compiler/version matrices,
and independent cryptographic review.


The historical parameters do not satisfy the common sufficient condition for complete Twisted Edwards addition ( square and d nonsquare). The affine formulas must not be assumed exception-free; see the validation report and parameter-generation documentation.
