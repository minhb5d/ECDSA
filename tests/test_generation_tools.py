import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src" / "python"))

from eddsa_reference import load_curves
from generate_safe_prime import generate, is_probable_prime
from validate_parameters import validate


class GenerationToolTests(unittest.TestCase):
    def test_safe_prime_generation_is_reproducible(self):
        first = generate("custom-eddsa-test", 64)
        second = generate("custom-eddsa-test", 64)
        self.assertEqual(first, second)
        p = int(first["p"])
        factor = int(first["safe_prime_factor"])
        self.assertEqual(p, 2 * factor + 1)
        self.assertTrue(is_probable_prime(p))
        self.assertTrue(is_probable_prime(factor))

    def test_historical_parameter_validation(self):
        report = validate(load_curves()["mycurve"])
        self.assertTrue(all(report["checks"].values()))
        self.assertFalse(report["derived"]["complete_affine_formula_sufficient_condition"])


if __name__ == "__main__":
    unittest.main()
