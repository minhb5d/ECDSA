import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "python"))

from eddsa_reference import (  # noqa: E402
    IDENTITY, is_on_curve, keygen, load_curves, scalar_multiply, sign, verify,
)


class CurveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curves = load_curves()

    def test_base_points_are_on_curves(self):
        for curve in self.curves.values():
            with self.subTest(curve=curve.name):
                self.assertTrue(is_on_curve(curve.g, curve))

    def test_declared_subgroup_orders(self):
        for curve in self.curves.values():
            with self.subTest(curve=curve.name):
                self.assertEqual(IDENTITY, scalar_multiply(curve.q, curve.g, curve))

    def test_custom_signature_round_trip(self):
        curve = self.curves["mycurve"]
        secret, public = keygen(curve)
        signature = sign(b"message", secret, public, curve)
        self.assertTrue(verify(b"message", signature, public, curve))
        self.assertFalse(verify(b"modified", signature, public, curve))


if __name__ == "__main__":
    unittest.main()

