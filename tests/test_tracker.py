import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from titan.tracker import BayesianOpponentTracker


class TestBayesianTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = BayesianOpponentTracker()

    def test_initial_hazard(self):
        """With zero stockpiled estimate, dump hazard should be 0.0."""
        for c in self.tracker.commodities:
            self.assertEqual(self.tracker.get_dump_hazard(c), 0.0)

    def test_harvest_detection(self):
        """Detecting mature plant disappearing should increment shed estimate."""
        prev_tiles = [[None for _ in range(10)] for _ in range(10)]
        curr_tiles = [[None for _ in range(10)] for _ in range(10)]

        # Opponent had mature melon
        prev_tiles[2][2] = {
            "kind": "PLANT",
            "crop": "MELON",
            "yield_units": 6,
            "planted_day": 0,
        }
        # Step forward: plant harvested
        curr_tiles[2][2] = None

        self.tracker.prev_opp_tiles = prev_tiles
        self.tracker.update(curr_tiles, {}, step=10, shops=[])
        self.assertEqual(self.tracker.hoarded_shed_est["MELON"], 6)

        # Hazard probability should now be positive
        hazard = self.tracker.get_dump_hazard("MELON")
        self.assertGreater(hazard, 0.35)

    def test_town_drain_integration(self):
        """Shop drain calculation returns accurate product counts."""
        drain = self.tracker._calc_town_drain(step=4, shops=["BAKERY", "PET_CAFE"])
        # Bakery: EGG + WHEAT (mult 1)
        # Pet Cafe: CARROT (mult 2 for single product)
        self.assertEqual(drain["EGG"], 1)
        self.assertEqual(drain["WHEAT"], 1)
        self.assertEqual(drain["CARROT"], 2)


if __name__ == "__main__":
    unittest.main()

