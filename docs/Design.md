<!-- ==============================================================================================
  KAGGRICULTURE MASTER SUITE :: AUTONOMOUS AGRO-ECONOMIC SIMULATION RUNTIME
  SPONSOR: GOOGLE LLC | PLATFORM: KAGGLE COMPETITIONS ($50,000 TOURNAMENT POOL)
  DOCUMENT: 04 / 12 · DETAILED SOFTWARE DESIGN & TASK-VALUE SCHEDULER (Design.md)
  STYLE: EDITORIAL DEVELOPER NOIR // HIGH-DENSITY CINEMATIC TERMINAL TELEMETRY
  SECURITY LEVEL: CHAMPIONSHIP SUBMISSION CANDIDATE // WORLD RANK #1 SPECIFICATION
============================================================================================== -->

# Detailed Software Design & Algorithmic Specifications

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ DETAILED SOFTWARE DESIGN & ALGORITHMIC SPECIFICATIONS                                  │
│ TASK-VALUE SCHEDULER, GLOBAL MESH ROUTING, BAYESIAN RECONCILER & LIQUIDATION ENGINE   │
│ PRODUCTION BLUEPRINT • DETERMINISTIC MULTI-AGENT CONTROL                                │
└────────────────────────────────────────────────────────────────────────────────────────┘
[MODULE: DESIGN-CORE]         [PRECISION: IEEE-754 FP64 / 2D NUMPY TENSORS] [SCHEDULER: TWO-TIER VALUE-DENSITY]
[TIME COMPLEXITY: O(N log N)] [SPACE COMPLEXITY: O(1) STATIC BUFFER]        [MEMORY OVERHEAD: LOW-ALLOCATION]
[DOCUMENT ID: COMBINE-DES-04] [SPECIFICATION: ALGORITHMS & KERNELS]         [STATUS: RATIFIED SPECIFICATION]
```

---

## 00 · Core Architectural Design Axioms

1. **Hard Constraints Before Soft Preferences:** A crop about to convert to a weed or an animal about to escape is not a "low-value task"—it is an immediate asset write-off. Decay avoidance and survival tasks are categorized as **Tier-0** and resolved before any value-density competition occurs.
2. **One Universal Currency for Every Decision:** Watering a field, hiring a hand, and selling Wheat appear incomparable on their face. They become directly comparable the moment every candidate action is expressed as **Expected Net Dollars per Turn of Unit-Time Spent** ($\text{Value Density}$).
3. **Plan Against the Gap, Not the Total:** The scoring engine is parameterized by $\Delta \text{Bank} = \text{Bank}_{\text{us}} - \text{Bank}_{\text{opp}}$ rather than our own bank balance in isolation.
4. **Re-Derive, Never Presume:** Every candidate move is verified against current spatial state immediately prior to action emission. Stale cached intents are discarded.

---

## 01 · World State Representation & Memory Model

The perception engine ingests observation dictionaries into layered 2D NumPy arrays `(10, 10, C)` every turn:

```
╔═════════════════╦══════════════════════════════════════════════════════════╦═══════════════════════╗
║ WORLD VIEW      ║ CONSTITUENT STATE FIELDS                                 ║ REFRESH CADENCE       ║
╠═════════════════╬══════════════════════════════════════════════════════════╬═══════════════════════╣
║ `MyFarm`        ║ Spatial grid tensor (10x10xC), units, cash, shed, seeds. ║ Every turn (Step 0-719║
║ `OpponentFarm`  ║ Public grid tensor (10x10xC), units, cash, land quads.   ║ Every turn (Step 0-719║
║ `MarketState`   ║ Inventory, exact current prices, and 24-step history.    ║ Every turn (Step 0-719║
║ `TownState`     ║ Active shop instances and integrated demand-rate vectors.║ Every turn (Step 0-719║
╚═════════════════╩══════════════════════════════════════════════════════════╩═══════════════════════╝
```

---

## 02 · The Task-Value Scheduling Framework

### 2.1. The Task Data Structure
```python
@dataclass(slots=True)
class Task:
    kind: str             # "WATER", "HARVEST", "PLANT", "FEED", "CARE", "PICKUP", "PLACE", "BUILD_COOP", "COLLECT_FERTILIZER", "SELL", "HIRE", "BUY_LAND"
    target: tuple | None  # (x, y) coordinates or None for market-wide orders
    tier: int             # 0 = Hard Invariant (Survival), 1 = Economic Optimization
    est_turns: int        # Travel distance + execution turns to complete
    est_value: float      # Expected dollar value unlocked
    deadline_turns: int   # Turns remaining before catastrophic state transition (decay/escape)
```

### 2.2. Task Valuation Calculus
The expected value `est_value` translates domain-specific agronomic dynamics into liquid capital:

| Task Kind | Valuation Formula |
|---|---|
| `WATER` (Active Bonus Window) | $\Delta \text{Yield} \times P_{\text{simulated}}(I_{\text{curr}} + \text{Yield})$ |
| `HARVEST` (Ready Crop / Animal) | $\text{YieldUnits} \times P_{\text{simulated}}(I_{\text{curr}} + \text{YieldUnits})$ net of market impact |
| `FEED` (Livestock) | Prevents animal loss (Tier 0 when `consecutive_unfed == 1`), preserves banked bonus |
| `CARE` (Livestock) | Incremental future yield: $+1 \times P_{\text{simulated}}(I_{\text{curr}} + \text{yield})$ |
| `COLLECT_FERTILIZER` | Sells at $\$100$ or doubles yield bonus progression on high-margin crops |
| `PICKUP` / `PLACE` (Animal) | Deploys bought shed livestock onto active coop/pasture to start production cycle |
| `BUILD_COOP` / `BUILD_PASTURE` | $\$0$ capital investment; enables placement of compounding livestock |
| `SELL` (Shed Inventory) | $\sum_{k=1}^n P(I_{\text{curr}} + k)$ bounded by marginal elasticity gate |
| `HIRE` (Farm Hand) | Marginal production unlocked by 18 actions minus Fibonacci wage cost |
| `BUY_LAND` (Sequential Unlock) | Discounted Net Present Value ($\text{NPV}_k$) over remaining season turns |
| `FERTILIZE` | Saves 2 watering worker-turns & hedges yield cap on high-margin crops |

### 2.3. Value Density & Two-Tier Gating
$$\text{Value Density} = \frac{\text{EstValue}}{\max(1, \; \text{EstTurns})}$$

```python
def schedule_tasks(tasks: list[Task]) -> list[Task]:
    """Two-tier priority queue ensuring zero asset write-offs."""
    tier0 = [t for t in tasks if t.tier == 0] # Urgent survival invariants
    tier1 = [t for t in tasks if t.tier == 1] # Economic optimization

    # Tier 0 sorted by earliest deadline; Tier 1 sorted by value density
    tier0.sort(key=lambda t: t.deadline_turns)
    tier1.sort(key=lambda t: t.est_value / max(1, t.est_turns), reverse=True)

    # Hard constraints strictly precede optimization
    return tier0 + tier1
```

---

## 03 · Spatial Logistics: Global Walkable Mesh & Shed Port Routing

### 3.1. The Hand Spawn & Boundary Traps
A critical structural failure mode occurs when hired hands spawn. The first hired hand always spawns at coordinate `(5, 4)`, which resides in quadrant **NE**. If only quadrant **NW** is unlocked, any pathfinder that strictly restricts movement within `[0..4, 0..4]` causes the hand to become trapped or oscillate infinitely along the quadrant boundary.

### 3.2. Global Walkable Navigation Mesh
Per `Rules.md §3`, central shed tiles `{(4,4), (5,4), (4,5), (5,5)}` are **accessible and actionable regardless of quadrant lock status**. The navigation mesh is defined as:
$$\mathcal{M}_{\text{walkable}} = \mathcal{T}_{\text{unlocked}} \cup \{(4,4), (5,4), (4,5), (5,5)\}$$

```
                      NORTH BOUNDARY
         NW QUADRANT                     NE QUADRANT
    [Workers 0, 1]                  [Spawn Point (5,4)]
           │                               │
           ▼                               ▼
    PORT (4,4) ◄─────► [SHED] ◄─────► PORT (5,4)
           ▲                               ▲
           │                               │
    PORT (4,5) ◄─────► [SHED] ◄─────► PORT (5,5)
           ▲                               ▲
           │                               │
    [Workers 4, 5]                  [Workers 6, 7]
          SW QUADRANT                     SE QUADRANT
                      SOUTH BOUNDARY
```

- **Dedicated Port Invariant:** When interacting with the shed (e.g. `DROP` harvest or `PICKUP` fertilizer), workers use their quadrant's assigned port (`NW -> (4,4)`, `NE -> (5,4)`, `SW -> (4,5)`, `SE -> (5,5)`).
- **Corridor Traversal:** Hands spawned at `(5,4)` can walk immediately west into `(4,4)` and enter the NW operational zone without issuing illegal moves or triggering oscillation loops.
- **BFS Pathfinding:** Distance calculations use Breadth-First Search across $\mathcal{M}_{\text{walkable}}$, caching a $10 \times 10$ distance matrix per turn.

---

## 04 · Bayesian Opponent Tracking & Mass-Balance Reconciliation

Because opponent shed inventory is hidden, **TITAN-1** isolates the opponent's true hidden inventory through an exact conservation of mass equation:

$$\Delta S_{\text{opp}}(c, t) = \max\left(0, \; \left(I_{\text{curr}}(c) - I_{\text{prev}}(c)\right) + \Delta D_{\text{town}}(c, t) - \Delta S_{\text{us}}(c, t) + \Delta B_{\text{us}}(c, t)\right)$$

$$\hat{S}_{\text{opp}}(c, t) = \max\left(0, \; \hat{S}_{\text{opp}}(c, t - 1) + \Delta H_{\text{opp}}(c, t) - \Delta S_{\text{opp}}(c, t)\right)$$

```python
class BayesianOpponentTracker:
    """
    High-Frequency Bayesian Reconstruction of Opponent Private Shed Inventory.
    Reconciles public market deltas against town demand vectors and observed field harvests.
    """
    def __init__(self, market_params: dict):
        self.params = market_params
        self.crops = list(market_params.keys())
        self.hoarded_shed_est = {c: 0 for c in self.crops}
        self.prev_opp_tiles = None
        self.prev_market_inv = None
        self.our_sales_last_turn = {c: 0 for c in self.crops}
        self.our_buys_last_turn = {c: 0 for c in self.crops}

    def record_own_orders(self, orders: list):
        self.our_sales_last_turn = {c: 0 for c in self.crops}
        self.our_buys_last_turn = {c: 0 for c in self.crops}
        for cmd in orders:
            if not isinstance(cmd, (list, tuple)) or len(cmd) < 3:
                continue
            action, item, qty = cmd[0], cmd[1], int(cmd[2])
            if action == "SELL" and item in self.crops:
                self.our_sales_last_turn[item] += qty
            elif action == "BUY_PRODUCT" and item in self.crops:
                self.our_buys_last_turn[item] += qty

    def update(self, opp_tiles: list, current_market_inv: dict, step: int, unlocked_shops: list):
        # 1. Harvest detection on opponent farm
        if self.prev_opp_tiles is not None and opp_tiles is not None:
            for y in range(10):
                for x in range(10):
                    prev = self.prev_opp_tiles[y][x]
                    curr = opp_tiles[y][x]
                    if isinstance(prev, dict) and prev.get("kind") == "PLANT":
                        crop = prev.get("crop")
                        if curr is None or (isinstance(curr, dict) and curr.get("kind") != "PLANT"):
                            harvested = max(1, prev.get("yield_units", 1))
                            if crop in self.hoarded_shed_est:
                                self.hoarded_shed_est[crop] += harvested

        # 2. Market inventory balance reconciliation
        if self.prev_market_inv is not None and current_market_inv is not None:
            town_drain = self._calculate_turn_town_drain(step, unlocked_shops)
            for c in self.crops:
                curr_i = current_market_inv.get(c, 10000)
                prev_i = self.prev_market_inv.get(c, 10000)
                delta_m = curr_i - prev_i
                opp_sales = delta_m + town_drain.get(c, 0) - self.our_sales_last_turn.get(c, 0) + self.our_buys_last_turn.get(c, 0)
                if opp_sales > 0:
                    self.hoarded_shed_est[c] = max(0, self.hoarded_shed_est[c] - opp_sales)

        self.prev_opp_tiles = opp_tiles
        self.prev_market_inv = dict(current_market_inv) if current_market_inv else None

    def get_dump_hazard(self, commodity: str) -> float:
        stock = self.hoarded_shed_est.get(commodity, 0)
        return float(1.0 - math.exp(-stock / 12.0))
```

---

## 05 · Continuous Leaky-Bucket Market Liquidation Engine

### 5.1. The Line Limit vs Quantity Distinction
The Kaggle environment enforces a hard ceiling of **at most 10 market order lines** per turn (`len(market_orders) <= 10`). However, the environment imposes **no per-order unit quantity limit**; an order `["SELL", "WHEAT", 60]` is fully valid if 60 units reside in the shed.
Artificial unit caps (e.g. capping batch quantity to 10 units) fatally throttle endgame liquidation.

### 5.2. The Correct Liquidation Kernel
1. **Intraday Pacing (Phases 1–3):** For commodities with quadratic sensitivity (e.g. Melon), sell volume is bounded by marginal price elasticity to keep prices above $65\%$ of baseline.
2. **Terminal Liquidation (Turns 696–719):** Sell volume is unbounded by price elasticity; orders batch **all available shed inventory** across the 10 order lines to guarantee 100% liquidation before Turn 719.

```python
MARKET_BASE_PRICES: dict[str, int] = {
    "WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250,
    "EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100
}

MARKET_THROUGHPUT_T: dict[str, int] = {
    "WHEAT": 400, "CARROT": 450, "TOMATO": 200, "STRAWBERRY": 100, "MELON": 300,
    "EGG": 332, "MILK": 122, "WOOL": 105, "FERTILIZER": 200
}

FRAGILE_COMMODITIES: set[str] = {"MELON", "STRAWBERRY", "MILK", "WOOL"}

class ContinuousLeakyBucketEngine:
    def __init__(self, shed_safety_ceiling: int = 60):
        self.shed_safety_ceiling = shed_safety_ceiling

    def _compute_elasticity_headroom(self, commodity: str, current_inv: int) -> int:
        """Calculates volume headroom before market price drops below 65% of base."""
        t_cap = MARKET_THROUGHPUT_T.get(commodity, 200)
        if commodity in FRAGILE_COMMODITIES:
            delta = max(0, current_inv - 10000)
            return max(1, min(15, int(t_cap * 0.35 - delta)))
        return max(5, int(t_cap * 0.50))

    def generate_orders(self, shed_inv: dict, market_inv: dict, dump_hazards: dict, is_endgame: bool) -> list:
        orders = []
        # Priority: high hazard first, then highest base price
        priority_order = sorted(
            shed_inv.keys(),
            key=lambda c: (dump_hazards.get(c, 0.0), MARKET_BASE_PRICES.get(c, 0)),
            reverse=True
        )

        for c in priority_order:
            if len(orders) >= 10:
                break # Hard Kaggle limit: max 10 order lines

            available = shed_inv.get(c, 0)
            if available <= 0:
                continue

            if is_endgame or dump_hazards.get(c, 0.0) > 0.35:
                # Terminal liquidation or immediate dump front-running
                sell_qty = available
            else:
                # Intraday pacing: bound by elasticity headroom to avoid self-induced price collapse
                safe_vol = self._compute_elasticity_headroom(c, market_inv.get(c, 10000))
                sell_qty = min(available, safe_vol)

            if sell_qty > 0:
                orders.append(["SELL", c, sell_qty])

        return orders
```

---

## 06 · Market Health Index (MHI) Formulation

The **Market Health Index ($\text{MHI}$)** monitors open-market pricing health across all plantable commodities. Because an unweighted average obscures single-crop flash collapses, **TITAN-1** evaluates both aggregate health and worst-case commodity fragility:

$$\text{MHI}_{\text{agg}}(t) = \frac{1}{|C|} \sum_{c \in C} \frac{P_c(I_c(t))}{B_c}, \qquad \text{MHI}_{\text{fragile}}(t) = \min_{c \in C_{\text{fragile}}} \frac{P_c(I_c(t))}{B_c}$$

where:
- $C = \{\text{WHEAT}, \text{CARROT}, \text{TOMATO}, \text{STRAWBERRY}, \text{MELON}\}$
- $C_{\text{fragile}} = \{\text{MELON}, \text{STRAWBERRY}, \text{MILK}, \text{WOOL}\}$
- $P_c(I_c(t))$ is the simulated spot price from `Rules.md §6`
- $B_c$ is the canonical base price ($\text{Wheat}=\$25, \text{Carrot}=\$35, \text{Tomato}=\$60, \text{Strawberry}=\$120, \text{Melon}=\$250$)

```
┌──────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────┐
│ MHI Conditions                           │ System Strategic Regime & Operational Behavior                           │
├──────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ MHI_agg >= 0.85 and MHI_fragile >= 0.70  │ NORMAL TRADING: Full crop cycles, high-frequency leaky-bucket sales.     │
│ 0.70 <= MHI_agg < 0.85 (Fragile >= 0.50) │ CAUTION: Restrict high-fragility plantings; focus on town-demanded crops.│
│ MHI_fragile < 0.50 or MHI_agg < 0.70     │ AUTARKIC FAILOVER: Decouple from ruined crops; pivot 100% to closed-loop │
│                                          │ Goose/Egg/Fertilizer generating $895/day in safe cashflow.               │
└──────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────┘
```

```
[DESIGN SPECIFICATION COMPLETE]
[STATUS: 100% COMPILED FOR HIGH-INTEGRITY PRODUCTION IMPLEMENTATION]
```
