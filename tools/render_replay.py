"""
TITAN-1 Match Visualizer & Replay Generator
Simulates a full match and exports an interactive Kaggle HTML visualizer replay.
"""

import argparse
import os
import sys
import webbrowser

from kaggle_environments import make

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)


def generate_replay(
    agent_path: str,
    opponent: str,
    seed: int,
    steps: int,
    output_path: str,
    auto_open: bool = True,
):
    print("=" * 80)
    print("TITAN-1 MATCH SIMULATION & REPLAY GENERATOR")
    print(f"Agent:    {agent_path}")
    print(f"Opponent: {opponent}")
    print(f"Seed:     {seed}")
    print(f"Turns:    {steps}")
    print("=" * 80)

    print("[1/3] Running episode simulation on official engine...")
    env = make("kaggriculture", configuration={"episodeSteps": steps, "seed": seed}, debug=True)
    env.run([agent_path, opponent])

    final_step = env.steps[-1]
    p0_reward = final_step[0].reward
    p1_reward = final_step[1].reward
    margin = p0_reward - p1_reward
    status = "WIN" if p0_reward > p1_reward else "LOSS"

    print("\n[2/3] Match Completed!")
    print(f"  • TITAN-1 Score:  ${p0_reward:,.2f}")
    print(f"  • Opponent Score: ${p1_reward:,.2f}")
    print(f"  • Margin:         ${margin:,.2f} ({status})")

    print("\n[3/3] Rendering interactive HTML replay...")
    html_content = env.render(mode="html")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  • Replay saved to: {output_path} ({file_size_mb:.2f} MB)")
    print("=" * 80)
    print("You can open this HTML file in Chrome, Edge, or Firefox to watch:")
    print("  - Farmer & hired hand movements across the 10x10 grid")
    print("  - Crop planting, watering, fertilizing, and maturation")
    print("  - Coops, pastures, geese, and egg harvesting")
    print("  - Real-time market supply/demand curves and price fluctuations")
    print("=" * 80)

    if auto_open:
        print(f"Opening {output_path} in your default browser...")
        webbrowser.open("file://" + os.path.abspath(output_path))


def main():
    parser = argparse.ArgumentParser(description="TITAN-1 Replay Visualizer")
    parser.add_argument("--agent", default=os.path.join(ROOT, "main.py"), help="Agent path")
    parser.add_argument("--opponent", default="starter", help="Opponent (starter, random)")
    parser.add_argument("--seed", type=int, default=42, help="Episode RNG seed")
    parser.add_argument("--steps", type=int, default=720, help="Episode turns (default 720)")
    parser.add_argument(
        "--output",
        default=os.path.join(ROOT, "replays", "match_replay.html"),
        help="Target HTML output path",
    )
    parser.add_argument("--no-open", action="store_true", help="Do not automatically launch browser")

    args = parser.parse_args()
    generate_replay(
        agent_path=args.agent,
        opponent=args.opponent,
        seed=args.seed,
        steps=args.steps,
        output_path=args.output,
        auto_open=not args.no_open,
    )


if __name__ == "__main__":
    main()
