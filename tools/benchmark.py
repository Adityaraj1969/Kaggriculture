"""
TITAN-1 Benchmark CLI Harness
Executes multi-seed head-to-head simulations with statistical profiling and gate assertions.
"""

import argparse
import os
import sys
import time

from kaggle_environments import make

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)


def run_benchmark(
    agent_path: str,
    opponent: str,
    seeds: list[int],
    min_win_rate: float = 0.85,
    min_avg_score: float = 22000.0,
    verbose: bool = True,
) -> bool:
    print("=" * 80)
    print("TITAN-1 AGRO-ECONOMIC BENCHMARK RUNNER")
    print(f"Agent:     {agent_path}")
    print(f"Opponent:  {opponent}")
    print(f"Seeds:     {seeds}")
    print("=" * 80)

    scores_p0 = []
    scores_p1 = []
    latencies = []
    wins = 0

    header = f"{'Seed':>6} | {'Agent (P0)':>12} | {'Opponent (P1)':>14} | {'Margin':>10} | {'Status':>8} | {'Time':>7}"
    print(header)
    print("-" * 80)

    for s in seeds:
        t0 = time.perf_counter()
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([agent_path, opponent])
        elapsed = time.perf_counter() - t0

        final = env.steps[-1]
        p0 = final[0].reward
        p1 = final[1].reward
        won = p0 > p1
        margin = p0 - p1

        if won:
            wins += 1
        scores_p0.append(p0)
        scores_p1.append(p1)
        latencies.append(elapsed)

        res_str = "WIN" if won else "LOSS"
        row = f"{s:>6} | ${p0:>10,.0f} | ${p1:>12,.0f} | ${margin:>8,.0f} | {res_str:>8} | {elapsed:>5.1f}s"
        print(row)

    n = len(seeds)
    win_rate = wins / n if n > 0 else 0.0
    avg_p0 = sum(scores_p0) / n if n > 0 else 0.0
    avg_p1 = sum(scores_p1) / n if n > 0 else 0.0
    min_p0 = min(scores_p0) if scores_p0 else 0.0
    max_p0 = max(scores_p0) if scores_p0 else 0.0
    avg_lat = sum(latencies) / n if n > 0 else 0.0

    print("=" * 80)
    print("BENCHMARK EXECUTIVE SUMMARY")
    print(f"Total Matches:      {n}")
    print(f"Win Rate:           {wins}/{n} ({win_rate * 100:.1f}%) [Gate: >={min_win_rate * 100:.1f}%]")
    print(f"Mean Agent Reward:  ${avg_p0:,.0f} [Gate: >=${min_avg_score:,.0f}]")
    print(f"Opponent Mean:      ${avg_p1:,.0f}")
    print(f"Min / Max Reward:   ${min_p0:,.0f} / ${max_p0:,.0f}")
    print(f"Mean Match Latency: {avg_lat:.2f}s (~{avg_lat / 720 * 1000:.2f}ms / turn)")
    print("=" * 80)

    passed_wr = win_rate >= min_win_rate
    passed_score = avg_p0 >= min_avg_score

    if passed_wr and passed_score:
        print("[SUCCESS] All tournament deployment gates PASSED.")
        return True
    else:
        print("[FAILURE] Deployment gates FAILED:")
        if not passed_wr:
            print(f"  - Win rate {win_rate * 100:.1f}% below target {min_win_rate * 100:.1f}%")
        if not passed_score:
            print(f"  - Average reward ${avg_p0:,.0f} below target ${min_avg_score:,.0f}")
        return False


def main():
    parser = argparse.ArgumentParser(description="TITAN-1 Benchmark CLI")
    parser.add_argument("--agent", default=os.path.join(ROOT, "main.py"), help="Path to agent script")
    parser.add_argument("--opponent", default="starter", help="Opponent identifier (starter, random)")
    parser.add_argument("--seeds", default="1,2,3,4,5", help="Comma-separated list of integer seeds")
    parser.add_argument("--min-win-rate", type=float, default=0.85, help="Minimum win rate required to pass")
    parser.add_argument("--min-avg-score", type=float, default=22000.0, help="Minimum average score required")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose logging")

    args = parser.parse_args()
    seed_list = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]

    success = run_benchmark(
        agent_path=args.agent,
        opponent=args.opponent,
        seeds=seed_list,
        min_win_rate=args.min_win_rate,
        min_avg_score=args.min_avg_score,
        verbose=not args.quiet,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
