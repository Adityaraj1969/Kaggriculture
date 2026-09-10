<!-- ==============================================================================================
  KAGGRICULTURE MASTER SUITE :: AUTONOMOUS AGRO-ECONOMIC SIMULATION RUNTIME
  SPONSOR: GOOGLE LLC | PLATFORM: KAGGLE COMPETITIONS ($50,000 TOURNAMENT POOL)
  DOCUMENT: 01 / 12 · PRODUCT REQUIREMENTS DOCUMENT (PRD.md)
  STYLE: EDITORIAL DEVELOPER NOIR // HIGH-DENSITY CINEMATIC TERMINAL TELEMETRY
  SECURITY LEVEL: CHAMPIONSHIP SUBMISSION CANDIDATE // WORLD RANK #1 SPECIFICATION
============================================================================================== -->

# Project Combine // TITAN-1 : Autonomous Agro-Economic Runtime

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PROJECT COMBINE // TITAN-1 : AUTONOMOUS AGRO-ECONOMIC RUNTIME                          │
│ SYSTEM ARCHITECTURE PRD • HIGH-DENSITY TOURNAMENT SPECIFICATION                        │
│ SPONSORED BY GOOGLE LLC • KAGGLE SIMULATIONS BENCHMARK                                  │
└────────────────────────────────────────────────────────────────────────────────────────┘
[SYSTEM: INITIALIZED]        [ENGINE: TITAN-1.0.5-NOIR]    [ENV: LINUX-PY310-SANDBOX]
[SUBMISSION REGIME: LATEST-2] [CONVERGENCE: BRADLEY-TERRY]  [TARGET: RANK #1 WORLD ($5k GRAND)]
[TIMELINE: JUL 29 - OCT 15]   [SEASON HORIZON: 720 TURNS]   [CYCLE BUDGET: < 45MS COOPERATIVE DEADLINE]
[DOCUMENT ID: COMBINE-PRD-01] [SPECIFICATION: SLAS & FRS]   [STATUS: RATIFIED SPECIFICATION]
```

---

## 1. Executive Summary & Macroeconomic Problem Space

The **Kaggle Kaggriculture Simulation** (sponsored by **Google LLC**) models a closed, non-linear, stochastic duopoly across a 30-day season ($720$ discrete turns / $24$ turns per day, indexed $0$ through $719$). Two adversarial agents cultivate independent $10 \times 10$ spatial farming matrices while trading against a unified, dynamic macroeconomic order book governed by asymmetric pricing elasticity, inventory-driven price collapse, town consumption drains, and non-linear labor cost escalation.

Ten places pay **$5,000 each — $50,000 total** — determined by a continuous Bradley-Terry matchmaking ladder followed by a two-week post-deadline convergence tournament.

### The Core Thesis:
> *Most agents in this competition will play the farming game in isolation. **TITAN-1** plays the market game underneath it — because the market is where 80% of competitive edge is won or lost.*

Underneath its casual farming aesthetic, Kaggriculture is a formal sandbox for **real-world enterprise supply chain optimization, dynamic market microstructure equilibrium, multi-agent game-theoretic confrontation, and capital velocity allocation under uncertainty**.

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 GLOBAL LEADERBOARD OBJECTIVE           │
                  ├──────────────────────┬─────────────────────────────────┤
                  │ Terminal Metric      │ Target Production SLA           │
                  ├──────────────────────┼─────────────────────────────────┤
                  │ Tournament Elo       │ > 1,850.0 Bradley-Terry Points  │
                  │ Final Bank Cash      │ > $22,000.00 Gold (vs Starter)  │
                  │ Matchmaking Win Rate │ > 85.00% vs General Pool        │
                  │ Action Invalidation  │ 0.000% (Strict Zero Tolerance)  │
                  │ Shed Dropped Items   │ 0 Units (Loss Prevention)       │
                  │ Neglected Crop Weeds │ 0 Tiles (Zero Attrition)        │
                  │ Escaped Livestock    │ 0 Animals (Unbroken Feed Loop)  │
                  └──────────────────────┴─────────────────────────────────┘
```

---

## 2. Competitive Context & The Submission Economy

Success on the Kaggle leaderboard requires strict operational discipline around three environmental constraints:

1. **Relative Win Objective:** Skill ratings update on win/loss/tie only. The margin of victory does not affect the rating delta (`Rules.md §11`). A $1 win is worth identical Elo to a $5,000 blowout. Consistency and downside risk management strictly dominate high-variance speculation.
2. **The Latest-2 Submission Tracking Rule:** While teams can upload up to 5 agents per day, **only the latest 2 submissions** are actively paired on the ladder and evaluated in the final Bradley-Terry tournament. High-frequency iteration must be backed by absolute local evaluation gates (`Evaluation.md §6`) to avoid stranding an inferior bot as one of the two active slots at the deadline.
3. **Information Asymmetry:** Player bank accounts, spatial tile layouts, worker coordinates, land expansions, and daily hires are **100% public** every turn. Conversely, shed stockpiles, seed counts, and worker held inventories are strictly private. **TITAN-1** exploits public telemetry to mathematically reconstruct the opponent's private shed inventory via mass-balance reconciliation (`Design.md §2`).

---

## 3. Structural Game Vulnerabilities & Algorithmic Countermeasures

Standard heuristic baselines and greedy rule-based bots catastrophically fail in Kaggriculture due to 10 systemic traps embedded in the physics and economics of the simulation engine. **TITAN-1** is architected around formal mathematical countermeasures for each vulnerability:

```
╔════╦══════════════════════════════════════╦════════════════════════════════════════════════════════════════════╗
║ #  ║ STRUCTURAL ENGINE VULNERABILITY      ║ TITAN-1 ALGORITHMIC COUNTERMEASURE                                 ║
╠════╬══════════════════════════════════════╬════════════════════════════════════════════════════════════════════╣
║ 01 ║ Asymmetric Quadratic Price Collapse  ║ Marginal Elasticity Derivative (dQ/dt) Selling Gates               ║
║ 02 ║ Shed 100-Capacity Drop Discards      ║ Turn-by-Turn Leaky-Bucket Liquidation (< 60% Capacity Cap)        ║
║ 03 ║ Day 0 Unwatered Crop Mortality Trap  ║ Atomic Day 0 Same-Turn Planting & Watering Reservation Invariant   ║
║ 04 ║ Fibonacci Labor Cost Escalation      ║ Workload-to-Capacity Dynamic Sizing Function with Hard Cap         ║
║ 05 ║ Central 2x2 Shed Spatial Contention  ║ 4-Way Geometric Quadrant Shed Port Routing Protocol                ║
║ 06 ║ Stochastic Town Shop Draw Drift      ║ Dynamic Poisson Demand Projection & 90% Confidence Interval Bounds ║
║ 07 ║ Opponent Inventory Hoarding & Dumps  ║ Bayesian Shed Mass-Balance Estimator & Pre-Emptive Liquidation     ║
║ 08 ║ Engine Timeout Violations (>1000ms)  ║ Sub-2.5ms Fractional Simplex Knapsack Solver + Cooperative Timeout ║
║ 09 ║ Adversarial Price Griefing / Ruins   ║ Closed-Loop Autarkic Goose/Egg/Fertilizer Economic Failover Mode   ║
║ 10 ║ Sunk Capital Velocity Stagnation     ║ Net Present Value (NPV) Dynamic Land Expansion Trigger ($1k/$2k/$4k)║
╚════╩══════════════════════════════════════╩════════════════════════════════════════════════════════════════════╝
```

---

## 4. Quantitative Performance Targets & Engineering SLAs

Every module within **TITAN-1** operates under strict deterministic service-level agreements (SLAs), verified against local benchmark suites (`starter`, `random`, and local scripted test harnesses):

| Metric Identifier | Parameter Name | Baseline Starter | Local Heuristic Benchmark | TITAN-1 Production SLA | Verification Gate |
|---|---|---|---|---|---|
| **KPI-01** | End-of-Season Bank Capital | $\approx \$16,000$ | $\approx \$18,500$ | **$\ge \$22,000.00$** | Objective Maximand |
| **KPI-02** | Win Rate vs Baseline Starter | $50.0\%$ (mirror) | $72.0\%$ | **$\ge 85.00\%$** | Elo Optimizer |
| **KPI-03** | Mean Turn Execution Latency | $2.1\text{ ms}$ | $11.5\text{ ms}$ | **$< 8.00\text{ ms}$** | Profiler Watchdog |
| **KPI-04** | P99 Turn Execution Latency | $4.8\text{ ms}$ | $28.0\text{ ms}$ | **$< 35.00\text{ ms}$** | 45.0 ms Cooperative Break |
| **KPI-05** | Shed Item Overflow Discard | Occasional spikes | Periodic drops | **$0.000\text{ units}$ (0%)** | Mathematical Invariant |
| **KPI-06** | Neglected Plant Weed Conversions | Baseline weed loss | Rare weed loss | **$0.000\text{ tiles}$ (0%)** | Tier-0 Survival Gate |
| **KPI-07** | Escaped Livestock Incidents | Starvation hazards | Rare escapes | **$0.000\text{ animals}$ (0%)** | Unbroken Feed Schedule |
| **KPI-08** | Invalid Engine Action Returns | $0.00\%$ | $0.05\%$ | **$0.000\%$ (0 Invalids)** | Pre-Flight Schema Sanitizer |
| **KPI-09** | Peak RAM Consumption | $\approx 42\text{ MB}$ | $\approx 65\text{ MB}$ | **$< 85\text{ MB}$** | Pre-allocated NumPy Buffers |

---

## 5. System Personas & Observability Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                SYSTEM PERSONAS & TELEMETRY FEEDS                               │
├──────────────────────┬─────────────────────────────┬───────────────────────────────────────────┤
│ Persona Code         │ Subsystem Focus             │ Responsibility & Decision Output          │
├──────────────────────┼─────────────────────────────┼───────────────────────────────────────────┤
│ **ARCHON-MACRO**     │ Portfolio & Capital Alloc   │ Computes daily NPV expansion, knapsack    │
│                      │                             │ simplex solutions, and posture switches.  │
│ **VECTOR-MICRO**     │ Spatial Dispatch & Routing  │ Solves worker pathing, 4-port shed locks, │
│                      │                             │ and global mesh navigation.               │
│ **NEXUS-MARKET**     │ High-Frequency Order Tape   │ Reconciles market queues, computes order  │
│                      │                             │ price elasticity, and drains shed stock.  │
│ **AEGIS-WATCHDOG**   │ Zero-Failure Safety Circuit │ Validates output schema, enforces turn    │
│                      │                             │ deadlines (<45ms), and catches exceptions.│
│ **OBSERVATORY**      │ Visual Telemetry Terminal   │ High-density developer noir console for   │
│                      │                             │ live match playback and replay analysis.  │
└──────────────────────┴─────────────────────────────┴───────────────────────────────────────────┘
```

---

## 6. Functional Requirements (FR)

### 6.1. Perception & Environment Ingestion (Tier 1)
- **FR-01 (Multi-Channel 2D State Tensors):** The engine must ingest the $10 \times 10$ terrain grid into layered 2D NumPy arrays `(10, 10, C)` (encoding terrain type, crop ID, age, moisture, structure, and animal state) within $< 1.2\text{ ms}$.
- **FR-02 (Multi-Force Market Reconciliation):** The engine must compute the exact balance of market forces per commodity each turn:
  $$\Delta S_{\text{opp}}(c, t) = \max\left(0, \; \Delta I_{\text{market}}(c, t) + \Delta D_{\text{town}}(c, t) - \Delta S_{\text{us}}(c, t) + \Delta B_{\text{us}}(c, t)\right)$$
- **FR-03 (Bayesian Opponent Shed Tracking):** The agent must maintain a belief vector $\hat{S}_{\text{opp}}(c)$ of the opponent's private shed stockpile by integrating observed field harvests and reconciled market sales.
- **FR-04 (Town Shop Drain Projection):** The system must continuously update dynamic demand vectors across all active shops (drawn with replacement up to 8 instances), projecting cumulative absorption capacity over $24$-turn, $48$-turn, and season-end horizons.

### 6.2. Macroeconomic & Posture Optimization (Tier 2)
- **FR-05 (Dynamic Event-Driven Expansion):** The engine must evaluate quadrant unlocking ($\text{NE}=\$1\text{k}, \text{SW}=\$2\text{k}, \text{SE}=\$4\text{k}$) based on capital velocity and Net Present Value ($\text{NPV} > 1.25 \times \text{Cost}$) rather than fixed turn counts.
- **FR-06 (Fractional Simplex Knapsack Solver):** At the beginning of each in-game day (hour $0$), the macro solver must allocate available tiles across crops and livestock within $< 2.5\text{ ms}$ using a vectorized marginal profit density formulation.
- **FR-07 (Workload-Driven Labor Sizing):** The agent must hire farm hands strictly according to daily task counts, capping hires to prevent Fibonacci wage inefficiency:
  $$K^*(t) = \min\left( K_{\text{cap}}(\text{Quads}), \; \max\left(0, \left\lceil \frac{N_{\text{tasks}}}{18} \right\rceil - 1 \right) \right)$$
- **FR-08 (Gestation Boundary Cutoff):** The system must disallow the purchasing and planting of crops whose maturity window exceeds remaining season turns ($T_{\text{rem}} = 719 - \text{turn}$).

### 6.3. Spatial Logistics & Multi-Agent Micro (Tier 3)
- **FR-09 (Global Mesh Navigation & Shed Port Partitioning):** To eliminate deadlocks and boundary oscillation, workers navigate a unified graph comprising all unlocked tiles plus the central shed tiles `{(4,4), (5,4), (4,5), (5,5)}`. Hands spawning at `(5,4)` route cleanly into unlocked zones.
- **FR-10 (Boustrophedon Serpentine Field Sweep):** Worker travel paths must follow scanline serpentine orders to minimize Manhattan movement distance per task.
- **FR-11 (Atomic Day 0 Watering Guarantee):** Any seed planted must have an accompanying `WATER` action executed on the same turn or assigned to a co-located worker within the same day.
- **FR-12 (Animal Husbandry Loop):** Livestock (Geese, Cows, Sheep) must receive daily `FEED` (Wheat) before any other action, followed by `CARE` banking and daily `COLLECT_FERTILIZER`.
- **FR-13 (Fertilizer Compounding Allocation):** Collected fertilizer must be prioritized for premium one-time crops (Melons) during their active yield bonus window to double incremental yield ($+1 \to +2$ units/day).

### 6.4. Market Liquidation & Order Execution (Tier 4)
- **FR-14 (Continuous Leaky-Bucket Selling):** The market module must emit sales orders every single turn (up to the 10-order line engine ceiling) with appropriately sized batch quantities, guaranteeing shed inventory remains below $60$ units ($< 60\%$ capacity).
- **FR-15 (Asymmetric Elasticity Safety Gate):** For goods subject to quadratic or steep linear price collapse (Melon, Strawberry, Milk, Wool), normal intraday sale volumes must be dynamically throttled to prevent dropping market price below $65\%$ of target base value.
- **FR-16 (Pre-Emptive Opponent Dump Trigger):** When opponent hoarded inventory surpasses hazard threshold ($P_{\text{dump}} > 0.35$), the agent must front-run market liquidity by liquidating owned inventory of that commodity immediately.
- **FR-17 (Terminal Season Liquidation):** Between turns $696$ and $719$ (Hour 23 of Day 30), all field maintenance must cease, and $100\%$ of remaining inventory must be liquidated across available order lines into gold.

### 6.5. Safety Watchdog & Invariant Engine (Tier 5)
- **FR-18 (Pre-Flight Action Validation):** All generated moves and market orders must pass an offline schema and boundary checker before dispatch to the Kaggle environment.
- **FR-19 (Cooperative Deadline Watchdog):** Inner loops must poll execution time. If total turn processing approaches $40.0\text{ ms}$, the engine must abort deeper branch exploration, serialize candidate actions, and return a legal move.
- **FR-20 (Autarkic Anti-Griefing Fallback):** If the Market Health Index, parameterized by aggregate $\text{MHI}_{\text{agg}} = \frac{1}{|C|} \sum \frac{P_c}{B_c}$ and commodity fragility $\text{MHI}_{\text{fragile}} = \min_{c \in C_{\text{fragile}}} \frac{P_c}{B_c}$, breaches threshold ($\text{MHI}_{\text{fragile}} < 0.50$ or $\text{MHI}_{\text{agg}} < 0.70$), indicating severe commodity price destruction, the engine must pivot to a closed-loop Goose/Egg/Fertilizer production mode generating $\$895.00/\text{day}$ with zero dependency on ruined open markets.

---

## 7. Non-Functional Requirements (NFR)

- **NFR-01 (Deterministic Replayability):** Given a static environment seed, execution across $720$ turns must be $100\%$ bitwise deterministic.
- **NFR-02 (Memory Overhead & Low-Allocation NumPy Architecture):** Peak memory usage must not exceed $85\text{ MB}$. Core inner loops reuse pre-allocated NumPy array buffers to minimize Python garbage collection pauses.
- **NFR-03 (Single-File & Multi-File Portability):** The codebase must support packaging into a monolithic standalone `main.py` and modular bundle `submission.tar.gz`.
- **NFR-04 (Zero External Binary Dependencies):** Execution must rely solely on standard Python libraries and pre-installed Kaggle runtime packages (`numpy`, `scipy`).
- **NFR-05 (Fault Isolation):** Unhandled exceptions in perception or macro optimization must never crash the submission; a top-level guard must catch any error and emit a guaranteed legal fallback action.

---

## 8. Risk Analysis & Mitigation Matrix

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   ENGINE RISK CONTROL MATRIX                                   │
├────────────────────────────┬────────┬────────┬─────────────────────────────────────────────────┤
│ Risk Event                 │ Prob.  │ Impact │ Built-in Engineering Mitigation                 │
├────────────────────────────┼────────┼────────┼─────────────────────────────────────────────────┤
│ Opponent Flash-Dump Crash  │ HIGH   │ CRIT   │ Bayesian shed tracker triggers sales 1 turn     │
│                            │        │        │ before opponent maturity window opens.          │
│ Shed 100-Item Overflow     │ MED    │ HIGH   │ Leaky-bucket turn-by-turn liquidation maintains │
│                            │        │        │ shed capacity buffer >= 40 free slots.          │
│ Kaggle 1000ms Step Timeout │ LOW    │ FATAL  │ Sub-2.5ms Simplex LP + cooperative watchdog.    │
│ Adverse Town Shop Draws    │ MED    │ MED    │ Dynamic linear hedging across staple crops.     │
│ Deadlock at Center Shed    │ HIGH   │ HIGH   │ Geometric 4-quadrant port isolation protocol.   │
│ Bad Late-Cycle Submission  │ LOW    │ FATAL  │ Automated 5-Gate pre-flight deployment checklist│
│                            │        │        │ protecting the two active tracked slots.        │
└────────────────────────────┴────────┴────────┴─────────────────────────────────────────────────┘
```

```
[PRD RATIFIED: SYNTHESIS COMPLETE]
[STATUS: READY FOR COMPLETE ARCHITECTURAL TRACE]
```
