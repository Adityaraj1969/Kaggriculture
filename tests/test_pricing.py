import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from titan.constants import MARKET_I0, MARKET_PARAMS, PRICE_FLOOR
from titan.pricing import compute_sell_revenue, market_price


class TestMarketPricing(unittest.TestCase):
    """27-Point Boundary Value Verification across all 9 commodities (Validation.md §1.3)."""

    CANONICAL_POINTS = {
        # item: (P(I0 - T), P(I0 + T), P(I0 + 2T))
        "WHEAT": (45, 20, 19),
        "CARROT": (70, 10, 1),
        "TOMATO": (84, 24, 9),
        "STRAWBERRY": (204, 1, 1),
        "MELON": (300, 1, 1),
        "EGG": (70, 40, 39),
        "MILK": (256, 1, 1),
        "WOOL": (240, 1, 1),
        "FERTILIZER": (140, 60, 20),
    }

    def test_canonical_boundary_points(self):
        for item, (exp_below, exp_above_1, exp_above_2) in self.CANONICAL_POINTS.items():
            t = MARKET_PARAMS[item]["T"]

            # Point 1: I0 - T (Scarcity)
            p_below = market_price(item, MARKET_I0 - t)
            self.assertEqual(
                p_below,
                exp_below,
                f"{item} at I0 - T: expected {exp_below}, got {p_below}",
            )

            # Point 2: I0 + T (Glut +1T)
            p_above_1 = market_price(item, MARKET_I0 + t)
            self.assertEqual(
                p_above_1,
                exp_above_1,
                f"{item} at I0 + T: expected {exp_above_1}, got {p_above_1}",
            )

            # Point 3: I0 + 2T (Glut +2T)
            p_above_2 = market_price(item, MARKET_I0 + 2 * t)
            self.assertEqual(
                p_above_2,
                exp_above_2,
                f"{item} at I0 + 2T: expected {exp_above_2}, got {p_above_2}",
            )

    def test_price_floor_invariant(self):
        """Price must never drop below PRICE_FLOOR (1.00)."""
        for item in MARKET_PARAMS:
            huge_glut_price = market_price(item, MARKET_I0 + 100000)
            self.assertGreaterEqual(huge_glut_price, PRICE_FLOOR)

    def test_cumulative_sell_revenue(self):
        """Simulate multi-unit sequential sell revenue."""
        rev = compute_sell_revenue("WHEAT", 5, MARKET_I0)
        self.assertGreater(rev, 0)
        # Average price should be around base price ()
        self.assertTrue(90 <= rev <= 130)


if __name__ == "__main__":
    unittest.main()


