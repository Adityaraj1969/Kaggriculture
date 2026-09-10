import os
import sys
import unittest

from kaggle_environments import make

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from titan.agent import agent


class TestSimulationIntegration(unittest.TestCase):
    """End-to-end 720-turn simulation verification against baseline starter."""

    def test_single_episode_victory_seed1(self):
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 1}, debug=True)
        env.run([agent, "starter"])
        final_step = env.steps[-1]
        p0_reward = final_step[0].reward
        p1_reward = final_step[1].reward

        self.assertEqual(final_step[0].status, "DONE")
        self.assertGreater(p0_reward, p1_reward, "P0 () must beat starter P1 ()")
        self.assertGreaterEqual(p0_reward, 22000.0, "P0 reward () must meet the  SLA")


if __name__ == "__main__":
    unittest.main()


