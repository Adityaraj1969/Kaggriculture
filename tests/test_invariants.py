import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from titan.agent import agent


class TestSafetyInvariants(unittest.TestCase):
    def test_fault_tolerant_fallback(self):
        """Malformed or corrupted observations must never raise exceptions."""
        malformed_obs = {}
        out = agent(malformed_obs)
        self.assertIn("farmer", out)
        self.assertIn("hands", out)
        self.assertIn("market", out)
        self.assertEqual(out["farmer"], ["PASS"])

    def test_market_order_batch_ceiling(self):
        """Engine enforces strict ceiling of <= 10 market order lines per turn."""
        dummy_obs = {
            "player": 0,
            "day": 10,
            "hour": 0,
            "step": 240,
            "farms": [
                {
                    "money": 10000.0,
                    "tiles": [[None for _ in range(10)] for _ in range(10)],
                    "unlocked_quadrants": ["NW", "NE"],
                    "farmer": [4, 4],
                    "hands": [],
                },
                {"money": 5000.0, "tiles": [], "hands": []},
            ],
            "private": {
                "shed": {item: 100 for item in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]},
                "seeds": {},
                "inventories": [{}],
            },
            "market": {"inventory": {}},
            "town": {"unlocked_shops": []},
        }
        out = agent(dummy_obs)
        self.assertLessEqual(len(out["market"]), 10)

    def test_action_schema_structure(self):
        """Unit actions and market orders follow valid Kaggle syntax."""
        dummy_obs = {
            "player": 0,
            "day": 0,
            "hour": 0,
            "step": 0,
            "farms": [
                {
                    "money": 3000.0,
                    "tiles": [[None for _ in range(10)] for _ in range(10)],
                    "unlocked_quadrants": ["NW"],
                    "farmer": [0, 0],
                    "hands": [],
                },
                {"money": 3000.0, "tiles": [], "hands": []},
            ],
            "private": {"shed": {}, "seeds": {}, "inventories": [{}]},
            "market": {"inventory": {}},
            "town": {"unlocked_shops": []},
        }
        out = agent(dummy_obs)
        self.assertIsInstance(out["farmer"], list)
        self.assertIsInstance(out["hands"], list)
        self.assertIsInstance(out["market"], list)
        for order in out["market"]:
            self.assertIn(order[0], ["BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "SELL", "HIRE", "BUY_LAND"])


if __name__ == "__main__":
    unittest.main()

