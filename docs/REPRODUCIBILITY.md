# Reproduction Guide

## Python

```bash
python --version
python -m unittest discover -s tests -v
python src/python/benchmark.py --trials 100 --seed 20260510 \
  --output results/python-latest.csv
```

## C++17

Install a C++17 compiler, CMake, and Boost headers, then run:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
./build/eddsa_benchmark 100
```

On Windows with a multi-configuration generator, the executable is commonly
located at `build/Release/eddsa_benchmark.exe`.

## Figure

```bash
python -m pip install -r requirements.txt
python scripts/plot_results.py
```

Record the commit hash and environment alongside every new result:

```bash
git rev-parse HEAD
python --version
c++ --version
cmake --version
```


## Parameter validation and generation

```bash
python tools/validate_parameters.py --output parameters/validation-report.json
python tools/generate_safe_prime.py --seed "Custom EdDSA Twisted Edwards Research 2026-07-02 v1" --bits 256 --output parameters/generated-safe-prime-v1.json
```

Generating a complete curve additionally requires SageMath:

```bash
sage tools/generate_curve.sage --prime-json parameters/generated-safe-prime-v1.json --seed "Custom EdDSA Twisted Edwards Research 2026-07-02 v1" --a -1 --cofactor 8 --output parameters/generated-curve-v1.json
```