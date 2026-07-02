# Contributing

Changes to arithmetic or parameters should include tests and an explanation of
their security impact. New benchmark results must include raw samples, runtime
and compiler versions, optimization flags, CPU/OS details, trial count, warm-up
policy, and the commit hash tested.

Do not describe code as constant-time solely because it has a fixed loop.
Claims must distinguish regularized control flow from constant-time field
arithmetic and should be supported by assembly review and timing analysis.

