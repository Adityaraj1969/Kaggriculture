```
  _______ _____ _______       _   _        __     _____ ____  __  __ ____ ___ _   _ _____ 
 |__   __|_   _|__   __|/\   | \ | |      /_ |   / ____/ __ \|  \/  |  _ \_ _| \ | | ____|
    | |    | |    | |  /  \  |  \| |______ | |  | |   | |  | | \  / | |_) | ||  \| | |__  
    | |    | |    | | / /\ \ | . ` |______|| |  | |   | |  | | |\/| |  _ <| || . ` |  __| 
    | |   _| |_   | |/ ____ \| |\  |       | |  | |___| |__| | |  | | |_) | || |\  | |___ 
    |_|  |_____|  |_/_/    \_\_| \_|       |_|   \_____\____/|_|  |_|____/___|_| \_|_____|
```

```
══════════════════════════════════════════════════════════════════════════════════════════════════════
  TITAN-1 / COMBINE · KAGGRICULTURE (Kaggle × Google LLC)
  Master Agro-Economic Engineering Documentation Suite & Tournament Repository
──────────────────────────────────────────────────────────────────────────────────────────────────────
  DOCUMENT    00 / 12 · MASTER DOCUMENTATION INDEX & REPOSITORY GUIDE (README.md)
  SPONSOR     Google LLC                             PLATFORM    Kaggle Competitions
  PRIZE POOL  $50,000 Total ($5,000 Tier #1 Award)   TARGET      Championship Rank #1
  STATUS      PRODUCTION CANDIDATE                   REV         3.2.0 (Verified Canon)
  WORKSPACE   ./ (Repository Root)
══════════════════════════════════════════════════════════════════════════════════════════════════════
```

# TITAN-1 / COMBINE — Autonomous Agro-Economic Engine

> *"The land is free. Everything else is an economic trade. One season. Two farms. One ledger that does not lie."*

---

## Executive Overview

**Kaggriculture** is an official simulation competition hosted by **Kaggle** and sponsored by **Google LLC**. Two autonomous agents manage competing 10×10 agricultural estates across a 720-turn (30-day) competitive season (turns $0$ through $719$). Agents plant, water, fertilize, and harvest crops; construct coops and pastures; manage livestock; hire labor; and expand land—all while transacting through a **single, shared, highly reactive marketplace** governed by non-linear price dynamics.

At the conclusion of Turn 719, the agent with the highest liquid bank balance wins the match. However, **Kaggle rating updates depend strictly on binary win/loss/tie outcomes—coin margin provides zero additional reward**. 

**TITAN-1 / COMBINE** is a championship-grade autonomous agent built on mathematical microeconomics, low-allocation NumPy computing, and Bayesian opponent modeling. Rather than treating Kaggriculture as a naive farming game, TITAN-1 approaches it as a **high-frequency market microstructure and inventory arbitrage problem wearing a scarecrow costume**.

---

## Complete Documentation Index (11 Modules + Master Index)

The repository contains 11 authoritative engineering specifications plus this master index, formatted in **Editorial Developer Noir / High-Density Terminal Telemetry**:

```
┌────┬─────────────────────────────┬─────────────────────────────────┬─────────────────────────────────────────────────┐
│ #  │ Specification Document      │ Engineering Class & Focus       │ Primary Purpose & Key Theoretical Contents      │
├────┼─────────────────────────────┼─────────────────────────────────┼─────────────────────────────────────────────────┤
│ 00 │ README.md (This File)       │ Master Repository Index         │ Project navigation, system codenames, runbooks. │
│ 01 │ PRD.md                      │ Product Requirements & Scope    │ Problem definition, 10 failure modes, SLAs.     │
│ 02 │ Rules.md                    │ Mathematical Ground Truth       │ Canon price formulas, numerical tables, bounds. │
│ 03 │ Architecture.md             │ 5-Tier System Model             │ Sub-45ms pipeline, 2D NumPy tensors, memory.    │
│ 04 │ Design.md                   │ Decision & Scheduling Logic     │ Task dataclass, value density, global mesh.     │
│ 05 │ AI_Strategy.md              │ Strategic & Economic Playbook   │ Relative objective theorem, 5 risk postures.    │
│ 06 │ Phases.md                   │ Execution Lifecycle Roadmap     │ 4 match phases, capital velocity, calendar.     │
│ 07 │ Evaluation.md               │ Adversarial League Framework    │ Bradley-Terry convergence, benchmark matrix.    │
│ 08 │ code_quality.md             │ Production Engineering Standard │ Static analysis, Hypothesis testing, watchdogs. │
│ 09 │ UI_UX_designed.md           │ CRT Terminal Interface          │ The Docket & Observatory, CSS telemetry widget. │
│ 10 │ Validation.md               │ Correctness & Invariant Gates   │ Sandbox envelopes, open question test scripts.  │
│ 11 │ Demo.md                     │ Judge Presentation Runbook      │ 3-min/8-min scripts, multi-seed benchmark tape. │
└────┴─────────────────────────────┴─────────────────────────────────┴─────────────────────────────────────────────────┘
```

---

## Decoded System Terminology & Architecture Codenames

```
╔══════════════════════════════╦═══════════════════════════════════════════════════════════════════════════════╗
║ SYSTEM CODENAME              ║ ARCHITECTURAL FUNCTION & REPOSITORY MAPPING                                   ║
╠══════════════════════════════╬═══════════════════════════════════════════════════════════════════════════════╣
║ TITAN-1 / COMBINE            ║ The complete autonomous decision engine submitted to the live Kaggle ladder. ║
╠══════════════════════════════╬═══════════════════════════════════════════════════════════════════════════════╣
║ THE DOCKET                   ║ High-contrast terminal telemetry stream logging every tactical justification. ║
╠══════════════════════════════╬═══════════════════════════════════════════════════════════════════════════════╣
║ OBSERVATORY                  ║ Developer Noir CRT visualizer and match replay inspection console.            ║
╠══════════════════════════════╬═══════════════════════════════════════════════════════════════════════════════╣
║ LEDGER                       ║ Continuous non-linear price and market-impact simulation layer.               ║
╠══════════════════════════════╬═══════════════════════════════════════════════════════════════════════════════╣
║ LEAKY BUCKET                 ║ Intraday continuous seller regulating shed inventory to prevent discards.    ║
╠══════════════════════════════╬═══════════════════════════════════════════════════════════════════════════════╣
║ SILO                         ║ Offline adversarial benchmarking and local regression testbed.                ║
╚══════════════════════════════╩═══════════════════════════════════════════════════════════════════════════════╝
```

---

## The Three Invariant Economic Laws

### Law 1: The Relative Objective Theorem (`AI_Strategy.md §1`)
Kaggle rating updates depend strictly on binary win/loss/tie outcomes. Winning by $\$1$ awards identical leaderboard Elo to winning by $\$10,000$. Therefore:
$$\text{Maximize } P(\text{Bank}_{\text{us}} > \text{Bank}_{\text{opp}}) \quad \not\equiv \quad \text{Maximize } \mathbb{E}[\text{Bank}_{\text{us}}]$$
- When **Leading** ($\text{Bank}_{\text{us}} - \text{Bank}_{\text{opp}} > +\$3,000$): Variance is a liability. Shift into `PROTECT_LEAD` (low-variance crops, crash-immune assets).
- When **Trailing** ($\text{Bank}_{\text{us}} - \text{Bank}_{\text{opp}} < -\$3,000$): Variance is an asset. Shift into `SURGE_TRAIL` (high-upside Melon/Strawberry volatility).

### Law 2: Mass-Balance Trade Reconstruction (`AI_Strategy.md §5`)
The opponent's shed is private, but the total market inventory $I_{\text{curr}}$ is public, and town shop demand $D_{\text{town}}$ is fully deterministic. TITAN-1 reconstructs hidden adversary sales every hour:
$$\Delta S_{\text{opp}}(c) = I_{\text{curr}}(c) - I_{\text{prev}}(c) + D_{\text{town}}(c) - \Delta S_{\text{us}}(c)$$
When opponent mature tiles are cleared without corresponding market sales, the Bayesian tracker detects hoarded stockpiles and front-runs impending dumps before prices collapse.

### Law 3: Terminal Liquidation Discipline (`AI_Strategy.md §6`)
Unsold crops and animal products remaining in the shed at Turn 719 possess a salvage value of **exactly $\$0.00$**.
- Turn 600: Hard gestation gate permanently bans new Melon plantings.
- Turn 696 (Day 30): Complete cessation of all seeding.
- Turns 711–719: Continuous sales liquidate all shed reserves into cash across available order lines.

---

## Quickstart Runbook & CLI Commands

### 1. Environment Verification
```bash
# Verify Python 3.10+ and dependencies
python --version
pip install kaggle-environments numpy mypy ruff pytest
```

### 2. Instant Local 720-Turn Simulation
```bash
# Run local match against Kaggle starter agent
python -c "
from kaggle_environments import make
env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': 42}, debug=True)
env.run(['main.py', 'starter'])
final = env.steps[-1]
print(f'Player 0: ${final[0].reward:,.2f} | Player 1: ${final[1].reward:,.2f}')
"
```

### 3. Run Self-Play Pre-Submission Invariant Gates
```bash
# Execute 5-seed self-play verification suite
python validate_submission.py
```

### 4. Execute Adversarial League Benchmark
```bash
# Evaluate agent against registered opponents
python evaluate_league.py
```

### 5. Push Standalone Champion Agent to Kaggle Ladder
```bash
# Deploy certified single-file master build via Kaggle CLI
kaggle competitions submit kaggriculture -f main.py -m "TITAN-1 v3.2 Champion Candidate"
```

---

## Suggested Reading Pathways

```
┌─────────────────────────┬──────────────────────────────────────────────────────────────────────────┐
│ Reader Profile          │ Recommended Navigational Sequence                                        │
├─────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ Competition Judges      │ Demo.md (3-Min Pitch) ──> PRD.md ──> AI_Strategy.md                      │
│ Core Systems Architects │ Architecture.md ──> Design.md ──> code_quality.md ──> Validation.md      │
│ Economic Strategists    │ Rules.md ──> AI_Strategy.md ──> Phases.md ──> Demo.md                    │
│ QA & Release Engineers  │ Validation.md ──> Evaluation.md ──> code_quality.md                      │
│ Frontend & UI Designers │ UI_UX_designed.md ──> Demo.md                                            │
└─────────────────────────┴──────────────────────────────────────────────────────────────────────────┘
```

---

## Competition Calendar & Milestone Gates

```
[AUGUST 2026] ─────────────────── [SEP 23: MERGER GATE] ──────── [SEP 28: FREEZE] ────── [SEP 30: FINALS]
Phase 0: Mathematical Canon       Phase 2: Town Arbitrage        Phase 4: Soak Test       Championship
Phase 1: Low-Allocation Engine    Phase 3: Dump Defense          48-Hour Hard Freeze      Leaderboard Lock
```

- **September 23, 2026:** Entry and Team Merger Deadline. Final team roster locked.
- **September 28, 2026:** 48-Hour Code Freeze. No experimental logic permitted; both slots occupied by soak-tested releases.
- **September 30, 2026:** Final Submission Deadline. The latest two submissions compete in the final Bradley-Terry tournament.

---

```
══════════════════════════════════════════════════════════════════════════════════════════════════════
  TITAN-1 / COMBINE // KAGGRICULTURE                                                          § README
  AUTHENTIC SPECIFICATION RATIFIED · 11 SPECIFICATION MODULES + MASTER INDEX VERIFIED
══════════════════════════════════════════════════════════════════════════════════════════════════════
```
