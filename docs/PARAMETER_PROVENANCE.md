# Parameter Provenance

The custom parameter set was recovered from the original exploratory notebook.
The repository verifies its algebraic relationships but does not contain the
seed and deterministic search transcript that generated it.

Therefore, the defensible statement is:

> The parameters are custom parameters that pass the documented algebraic
> checks. They are not claimed to be fully verifiably random or to have a
> complete nothing-up-my-sleeve derivation.

## Included checks

- probable primality of `p` and `q`
- base point membership
- `qG = identity`
- cofactor declaration
- signing and verification consistency

## Required for a stronger claim

A future parameter-generation release should publish a fixed public seed,
domain-separated hash construction, exact counter sequence, rejection rules,
point derivation method, point-counting transcript, software versions, and a
script that reproduces every final parameter from the seed.

