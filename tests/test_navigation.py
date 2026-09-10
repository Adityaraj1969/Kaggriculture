import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from titan.navigation import get_quadrant, is_unlocked, manhattan, step_towards, nearest


class TestNavigation(unittest.TestCase):
    def test_quadrant_geometry(self):
        self.assertEqual(get_quadrant(0, 0), 0)  # NW
        self.assertEqual(get_quadrant(4, 4), 0)  # NW
        self.assertEqual(get_quadrant(5, 0), 1)  # NE
        self.assertEqual(get_quadrant(9, 4), 1)  # NE
        self.assertEqual(get_quadrant(0, 5), 2)  # SW
        self.assertEqual(get_quadrant(4, 9), 2)  # SW
        self.assertEqual(get_quadrant(5, 5), 3)  # SE
        self.assertEqual(get_quadrant(9, 9), 3)  # SE

    def test_unlock_lookup(self):
        uq = {0, 1}
        self.assertTrue(is_unlocked(2, 2, uq))
        self.assertTrue(is_unlocked(7, 3, uq))
        self.assertFalse(is_unlocked(2, 7, uq))
        self.assertFalse(is_unlocked(8, 8, uq))

    def test_manhattan_distance(self):
        self.assertEqual(manhattan(0, 0, 3, 4), 7)
        self.assertEqual(manhattan(5, 5, 5, 5), 0)

    def test_step_towards(self):
        # Stepping from (0,0) towards (2,0) should go EAST
        self.assertEqual(step_towards(0, 0, 2, 0), ["EAST"])
        # Stepping from (2,2) towards (2,0) should go NORTH
        self.assertEqual(step_towards(2, 2, 2, 0), ["NORTH"])
        # At target, returns PASS
        self.assertEqual(step_towards(2, 2, 2, 2), ["PASS"])

    def test_nearest(self):
        candidates = [(0, 0), (5, 5), (9, 9)]
        self.assertEqual(nearest(4, 4, candidates), (5, 5))
        self.assertEqual(nearest(1, 0, candidates), (0, 0))


if __name__ == "__main__":
    unittest.main()

