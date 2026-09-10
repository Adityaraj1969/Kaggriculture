"""
TITAN-1 Multi-Tier Adversarial League Evaluator
Evaluates the candidate against built-in archetypes ('starter', 'random') and outputs skill ratings.
"""

import argparse
import os
import sys

from kaggle_environments import make

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)


def evaluate_tier(agent_path: str, opponent_name: str, seeds: list[int]) -> dict:
    wins = 0
    draws = 0
    losses = 0
    scores = []
    opp_scores = []

    for s in seeds:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([agent_path, opponent_name])
        final = env.steps[-1]
        p0 = final[0].reward
        p1 = final[1].reward
        scores.append(p0)
        opp_scores.append(p1)

        if p0 > p1:
            wins += 1
        elif p0 == p1:
            draws += 1
        else:
            losses += 1

    total = len(seeds)
    win_rate = (wins + 0.5 * draws) / total if total > 0 else 0.0
    avg_score = sum(scores) / total if total > 0 else 0.0
    avg_opp = sum(opp_scores) / total if total > 0 else 0.0

    return {
        "opponent": opponent_name,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "total": total,
        "win_rate": win_rate,
        "avg_score": avg_score,
        "avg_opp": avg_opp,
    }


def main():
    parser = argparse.ArgumentParser(description="TITAN-1 Adversarial League Evaluation")
    parser.add_argument("--agent", default=os.path.join(ROOT, "main.py"), help="Path to agent script")
    parser.add_argument("--seeds", default="1,2,3,4,5", help="Seeds per tier")
    args = parser.parse_args()

    seed_list = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]

    print("=" * 80)
    print("TITAN-1 ADVERSARIAL LEAGUE TOURNAMENT EVALUATOR")
    print(f"Agent: {args.agent}")
    print(f"Seeds: {seed_list}")
    print("=" * 80)

    opponents = ["starter", "random"]
    results = []

    for opp in opponents:
        print(f"[*] Evaluating against tier archetype '{opp}'...")
        res = evaluate_tier(args.agent, opp, seed_list)
        results.append(res)
        print(
            f"    -> Win Rate: {res['wins']}/{res['total']} ({res['win_rate']*100:.1f}%) | "
            f"Avg: ${res['avg_score']:,.0f} vs ${res['avg_opp']:,.0f}"
        )

    print("\n" + "=" * 80)
    print(f"{'Tier Opponent':<18} | {'Record (W-D-L)':<16} | {'Win Rate':<10} | {'Mean P0':<12} | {'Mean P1':<12}")
    print("-" * 80)
    for r in results:
        record_str = f"{r['wins']}-{r['draws']}-{r['losses']}"
        print(
            f"{r['opponent']:<18} | {record_str:<16} | {r['win_rate']*100:>7.1f}%   | "
            f"${r['avg_score']:>10,.0f} | ${r['avg_opp']:>10,.0f}"
        )
    print("=" * 80)


if __name__ == "__main__":
    main()
