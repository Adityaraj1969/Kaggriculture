"""
==============================================================================================
KAGGRICULTURE TITAN-1 :: CHAMPIONSHIP AUTONOMOUS AGENT (PRODUCTION CANDIDATE)
SPONSOR: GOOGLE LLC | PLATFORM: KAGGLE COMPETITIONS ($50,000 TOURNAMENT POOL)
==============================================================================================
"""

import math
import time
from typing import Any

# ==============================================================================================
# CANONICAL ENGINE CONSTANTS (Rules.md, kaggriculture.py)
# ==============================================================================================

CROPS: dict[str, dict[str, Any]] = {
    "WHEAT":      {"seed": 10, "first_yield_day": 2, "max_yield_day": 4, "interval": 0, "max_yield": 6, "ongoing": False},
    "CARROT":     {"seed": 20, "first_yield_day": 2, "max_yield_day": 3, "interval": 0, "max_yield": 4, "ongoing": False},
    "TOMATO":     {"seed": 50, "first_yield_day": 8, "max_yield_day": 8, "interval": 1, "max_yield": 4, "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True},
    "MELON":      {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False},
}

ANIMALS: dict[str, dict[str, Any]] = {
    "GOOSE": {"cost": 300, "structure": "COOP",    "first_yield_day": 4, "interval": 1, "max_held": 4, "product": "EGG"},
    "COW":   {"cost": 400, "structure": "PASTURE", "first_yield_day": 8, "interval": 2, "max_held": 6, "product": "MILK"},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "first_yield_day": 6, "interval": 3, "max_held": 6, "product": "WOOL"},
}

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]

# Engine-exact market parameters (kaggriculture.py)
MARKET_I0 = 10000
PRICE_FLOOR = 1
HINGE_GAIN = 8.0

MARKET_PARAMS: dict[str, dict[str, Any]] = {
    "WHEAT":      {"base":  25, "I0": MARKET_I0, "T": 400, "below_func": "sqrt",   "below_target": 0.80, "above_func": "log",    "above_target": 0.20},
    "CARROT":     {"base":  35, "I0": MARKET_I0, "T": 450, "below_func": "hinge",  "below_target": 1.00, "above_func": "sqrt",   "above_target": 0.70},
    "TOMATO":     {"base":  60, "I0": MARKET_I0, "T": 200, "below_func": "hinge",  "below_target": 0.40, "above_func": "sqrt",   "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": MARKET_I0, "T": 100, "below_func": "sqrt",   "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON":      {"base": 250, "I0": MARKET_I0, "T": 300, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.60},
    "EGG":        {"base":  50, "I0": MARKET_I0, "T": 332, "below_func": "hinge",  "below_target": 0.40, "above_func": "log",    "above_target": 0.20},
    "MILK":       {"base": 160, "I0": MARKET_I0, "T": 122, "below_func": "sqrt",   "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL":       {"base": 200, "I0": MARKET_I0, "T": 105, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": MARKET_I0, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}

FRAGILE_COMMODITIES = {"MELON", "STRAWBERRY", "MILK", "WOOL"}

# Gestation cutoffs: last day to plant for ANY yield
LAST_PLANT_DAY = {"WHEAT": 27, "CARROT": 27, "MELON": 19, "TOMATO": 21, "STRAWBERRY": 19}

# Land quadrant costs (sequential unlock: NE -> SW -> SE)
QUADRANT_COSTS = {1: 1000, 2: 2000, 3: 4000}

# Central shed portals
SHED_ACCESS_TILES = {(4, 4), (5, 4), (4, 5), (5, 5)}

# Engine-exact town shops (kaggriculture.py SHOPS)
SHOPS = {
    "BAKERY":         ["EGG", "WHEAT"],
    "PIZZA_SHOP":     ["MILK", "TOMATO", "WHEAT"],
    "BRUNCH_SPOT":    ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE":     ["WOOL"],
    "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"],
    "PET_CAFE":       ["CARROT"],
    "SMOOTHIE_SHOP":  ["STRAWBERRY", "MILK"],
    "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}


def _fib(n: int) -> int:
    """Fibonacci(n) for hiring costs. fib(0)=1, fib(1)=1, fib(2)=2, ..."""
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# ==============================================================================================
# ENGINE-EXACT PRICE SIMULATION (FR-02, Rules.md section 6)
# ==============================================================================================

def _shape(func: str, x: float, T: float = 0.0) -> float:
    """Exact replica of kaggriculture.py _shape function."""
    x = max(0.0, x)
    if func == "linear":
        return x
    if func == "sq":
        return x * x
    if func == "sqrt":
        return math.sqrt(x)
    if func == "log":
        return math.log(1.0 + x)
    if func == "log10":
        return math.log10(1.0 + x)
    if func == "hinge":
        if T <= 0:
            return x
        u = x / T
        return u + HINGE_GAIN * max(0.0, u - 1.0) ** 2
    return x


def market_price(item: str, inventory: int) -> int:
    """Compute exact market price matching the engine. Floor at PRICE_FLOOR."""
    p = MARKET_PARAMS[item]
    base = float(p["base"])
    I0 = float(p["I0"])
    T = float(p["T"])
    if inventory < I0:
        f = str(p["below_func"])
        below_target = float(p["below_target"])
        amp = below_target * base / _shape(f, T, T)
        price = base + amp * _shape(f, I0 - inventory, T)
    else:
        f = str(p["above_func"])
        above_target = float(p["above_target"])
        amp = above_target * base / _shape(f, T, T)
        price = base - amp * _shape(f, inventory - I0, T)
    return max(PRICE_FLOOR, int(round(price)))


# ==============================================================================================
# BAYESIAN OPPONENT TRACKER (FR-02, FR-03, FR-04)
# ==============================================================================================

class BayesianOpponentTracker:
    """Reconstructs opponent hidden shed inventory via mass-balance reconciliation."""

    def __init__(self) -> None:
        self.commodities = [p for p in PRODUCTS if p != "FERTILIZER"]
        self.hoarded_shed_est: dict[str, int] = {c: 0 for c in self.commodities}
        self.prev_opp_tiles: list[list[Any]] | None = None
        self.prev_market_inv: dict[str, int] | None = None
        self.our_sales: dict[str, int] = {c: 0 for c in self.commodities}
        self.our_buys: dict[str, int] = {c: 0 for c in self.commodities}

    def record_own_orders(self, orders: list[list[Any]]) -> None:
        self.our_sales = {c: 0 for c in self.commodities}
        self.our_buys = {c: 0 for c in self.commodities}
        for cmd in orders:
            if not isinstance(cmd, (list, tuple)) or len(cmd) < 3:
                continue
            act, item, qty = cmd[0], cmd[1], int(cmd[2])
            if act == "SELL" and item in self.our_sales:
                self.our_sales[item] += qty
            elif act in ("BUY_PRODUCT",) and item in self.our_buys:
                self.our_buys[item] += qty

    def update(self, opp_tiles: list[list[Any]] | None, market_inv: dict[str, int],
               step: int, shops: list[str]) -> None:
        # Detect opponent harvests
        if self.prev_opp_tiles is not None and opp_tiles is not None:
            for y in range(min(10, len(opp_tiles))):
                for x in range(min(10, len(opp_tiles[y]))):
                    prev = self.prev_opp_tiles[y][x]
                    curr = opp_tiles[y][x]
                    if isinstance(prev, dict) and prev.get("kind") == "PLANT":
                        crop = prev.get("crop")
                        if curr is None or (isinstance(curr, dict) and curr.get("kind") != "PLANT"):
                            harvested = max(1, prev.get("yield_units", 1))
                            if crop in self.hoarded_shed_est:
                                self.hoarded_shed_est[crop] += harvested

        # Reconcile market delta vs town drain
        if self.prev_market_inv is not None and market_inv:
            drain = self._calc_town_drain(step, shops)
            for c in self.commodities:
                curr_i = market_inv.get(c, MARKET_I0)
                prev_i = self.prev_market_inv.get(c, MARKET_I0)
                delta = curr_i - prev_i
                opp_sales = (delta + drain.get(c, 0) - self.our_sales.get(c, 0)
                             + self.our_buys.get(c, 0))
                if opp_sales > 0:
                    self.hoarded_shed_est[c] = max(0, self.hoarded_shed_est[c] - opp_sales)

        self.prev_opp_tiles = [row[:] for row in opp_tiles] if opp_tiles else None
        self.prev_market_inv = dict(market_inv) if market_inv else None

    def _calc_town_drain(self, step: int, shops: list[str]) -> dict[str, int]:
        drain: dict[str, int] = {c: 0 for c in self.commodities}
        if step % 24 == 0:
            for c in self.commodities:
                drain[c] += 1
        if step % 4 == 0:
            for shop_name in shops:
                products = SHOPS.get(shop_name, [])
                mult = 2 if len(products) == 1 else 1
                for item in products:
                    if item in drain:
                        drain[item] += mult
        return drain

    def get_dump_hazard(self, commodity: str) -> float:
        stock = self.hoarded_shed_est.get(commodity, 0)
        return float(1.0 - math.exp(-stock / 12.0))


# ==============================================================================================
# NAVIGATION HELPERS
# ==============================================================================================

def _get_quadrant(x: int, y: int) -> int:
    if x < 5 and y < 5: return 0
    if x >= 5 and y < 5: return 1
    if x < 5 and y >= 5: return 2
    return 3


def _is_unlocked(x: int, y: int, uq: set[int]) -> bool:
    return _get_quadrant(x, y) in uq


def _manhattan(x1: int, y1: int, x2: int, y2: int) -> int:
    return abs(x1 - x2) + abs(y1 - y2)


def _step_towards(cx: int, cy: int, tx: int, ty: int) -> list[str]:
    """Single greedy step towards target. All tiles are walkable (engine allows
    movement onto locked tiles; only field actions are blocked)."""
    if cx == tx and cy == ty:
        return ["PASS"]
    best_dir = "PASS"
    best_dist = _manhattan(cx, cy, tx, ty)
    for dx, dy, name in [(0, -1, "NORTH"), (0, 1, "SOUTH"), (-1, 0, "WEST"), (1, 0, "EAST")]:
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < 10 and 0 <= ny < 10:
            d = _manhattan(nx, ny, tx, ty)
            if d < best_dist:
                best_dist = d
                best_dir = name
    return [best_dir]


def _nearest(wx: int, wy: int, tiles_list: list[tuple[int, int]]) -> tuple[int, int]:
    """Find nearest tile from a list."""
    if not tiles_list:
        return (0, 0)
    return min(tiles_list, key=lambda t: _manhattan(wx, wy, t[0], t[1]))


def _find_target(wx: int, wy: int,
                 urgent_water: list[tuple[int, int]],
                 ready_harvest: list[tuple[int, int]],
                 plantable: list[tuple[int, int]],
                 unfed: list[tuple[int, int]],
                 claimed: set[tuple[int, int]]) -> tuple[int, int]:
    """Find the nearest high-priority unclaimed task tile."""
    for tile_list in [unfed, urgent_water, ready_harvest, plantable]:
        unclaimed = [t for t in tile_list if t not in claimed]
        if unclaimed:
            return _nearest(wx, wy, unclaimed)
    return (0, 0)


# ==============================================================================================
# PLANTING PRIORITY
# ==============================================================================================

def _get_plant_order(posture: str, day: int, days_left: int,
                     shed: dict[str, int]) -> list[str]:
    """Returns ordered list of crops to plant based on posture and timing."""
    if posture == "AUTARKY":
        return ["WHEAT"]
    if posture == "LEADING":
        return ["WHEAT", "CARROT"]
    if posture == "ENDGAME":
        return ["WHEAT", "CARROT"] if days_left >= 3 else []
    if posture == "TRAILING":
        result: list[str] = []
        if days_left >= 12: result.append("MELON")
        if days_left >= 16: result.append("STRAWBERRY")
        if days_left >= 11: result.append("TOMATO")
        if shed.get("WHEAT", 0) < 2: result.append("WHEAT")
        result.append("CARROT")
        if "WHEAT" not in result: result.append("WHEAT")
        return result
    # BALANCED
    result = []
    if days_left >= 12: result.append("MELON")
    if shed.get("WHEAT", 0) < 2: result.append("WHEAT")
    result.append("CARROT")
    if "WHEAT" not in result: result.append("WHEAT")
    return result


# ==============================================================================================
# MARKET HEALTH INDEX (FR-20)
# ==============================================================================================

def _compute_mhi(market_inv: dict[str, int]) -> tuple[float, float]:
    """Returns (MHI_aggregate, MHI_fragile)."""
    ratios: list[float] = []
    fragile: list[float] = []
    for item in PRODUCTS:
        if item == "FERTILIZER":
            continue
        inv = market_inv.get(item, MARKET_I0)
        price = market_price(item, inv)
        base = float(MARKET_PARAMS[item]["base"])
        r = price / base
        ratios.append(r)
        if item in FRAGILE_COMMODITIES:
            fragile.append(r)
    mhi_agg = sum(ratios) / len(ratios) if ratios else 1.0
    mhi_frag = min(fragile) if fragile else 1.0
    return mhi_agg, mhi_frag


# ==============================================================================================
# TITAN-1 STATE
# ==============================================================================================

class _TitanState:
    def __init__(self) -> None:
        self.tracker = BayesianOpponentTracker()
        self.posture = "BALANCED"
        self.prev_step = -1

    def reset(self) -> None:
        self.tracker = BayesianOpponentTracker()
        self.posture = "BALANCED"
        self.prev_step = -1


_ST = _TitanState()


# ==============================================================================================
# MAIN AGENT ENTRY POINT
# ==============================================================================================

def agent(obs: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    """TITAN-1 Championship Agent. Sub-40ms execution, zero-crash guarantee."""
    t0 = time.perf_counter()
    FALLBACK: dict[str, Any] = {"farmer": ["PASS"], "hands": [], "market": []}

    try:
        # ==== PERCEPTION ====
        pid = obs.get("player", 0)
        farms = obs.get("farms", [{}, {}])
        my_farm = farms[pid] if pid < len(farms) else {}
        opp_farm = farms[1 - pid] if (1 - pid) < len(farms) else {}
        private = obs.get("private", {})
        shed = private.get("shed", {})
        seeds = private.get("seeds", {})
        inventories = private.get("inventories", [{}])
        market_obs = obs.get("market", {})
        market_inv = market_obs.get("inventory", {}) if isinstance(market_obs, dict) else {}
        town_obs = obs.get("town", {})
        shops = town_obs.get("unlocked_shops", []) if isinstance(town_obs, dict) else []

        day = int(obs.get("day", 0))
        hour = int(obs.get("hour", 0))
        step = int(obs.get("step", day * 24 + hour))
        days_left = 30 - day
        is_endgame = day >= 29 or step >= 696

        tiles = my_farm.get("tiles", [])
        my_money = float(my_farm.get("money", 0.0))
        opp_money = float(opp_farm.get("money", 0.0))
        money_gap = my_money - opp_money

        # Reset on new episode
        if step == 0 or step < _ST.prev_step:
            _ST.reset()
        _ST.prev_step = step

        # Unlocked quadrants
        uq: set[int] = {0}
        for q in my_farm.get("unlocked_quadrants", ["NW"]):
            if isinstance(q, int) and 0 <= q <= 3: uq.add(q)
            elif q == "NW": uq.add(0)
            elif q == "NE": uq.add(1)
            elif q == "SW": uq.add(2)
            elif q == "SE": uq.add(3)

        # ==== BAYESIAN UPDATE & POSTURE ====
        _ST.tracker.update(opp_farm.get("tiles"), market_inv, step, shops)
        mhi_agg, mhi_frag = _compute_mhi(market_inv)

        if mhi_frag < 0.50 or mhi_agg < 0.70:
            _ST.posture = "AUTARKY"
        elif is_endgame:
            _ST.posture = "ENDGAME"
        elif money_gap > 3000:
            _ST.posture = "LEADING"
        elif money_gap < -3000:
            _ST.posture = "TRAILING"
        else:
            _ST.posture = "BALANCED"
        posture = _ST.posture

        # ==== TILE SURVEY ====
        urgent_water: list[tuple[int, int]] = []
        ready_harvest: list[tuple[int, int]] = []
        plantable: list[tuple[int, int]] = []
        weed_tiles: list[tuple[int, int]] = []
        animal_tiles: list[tuple[int, int]] = []
        unfed_animals: list[tuple[int, int]] = []
        empty_structs: list[tuple[int, int]] = []
        unfert_melon: list[tuple[int, int]] = []
        harvestable_animal: list[tuple[int, int]] = []
        fert_avail: list[tuple[int, int]] = []
        all_structs: list[tuple[int, int]] = []

        for y in range(10):
            if y >= len(tiles): break
            for x in range(10):
                if x >= len(tiles[y]): break
                if not _is_unlocked(x, y, uq): continue
                t = tiles[y][x]
                if t is None:
                    plantable.append((x, y))
                elif isinstance(t, dict):
                    k = t.get("kind")
                    if k == "PLANT":
                        crop = t.get("crop", "WHEAT")
                        cd = CROPS.get(crop, CROPS["WHEAT"])
                        age = day - t.get("planted_day", 0)
                        if not t.get("watered_today", False):
                            urgent_water.append((x, y))
                        yu = t.get("yield_units", 0)
                        if age >= cd["first_yield_day"] and (
                            yu >= cd["max_yield"] or age >= cd["max_yield_day"] or days_left <= 2):
                            ready_harvest.append((x, y))
                        if crop == "MELON" and t.get("fertilized_until_day", -1) < day and age < cd["max_yield_day"]:
                            unfert_melon.append((x, y))
                    elif k in ("COOP", "PASTURE"):
                        all_structs.append((x, y))
                        if t.get("animal"):
                            animal_tiles.append((x, y))
                            if not t.get("fed_today", False):
                                unfed_animals.append((x, y))
                            if t.get("yield_units", 0) > 0:
                                harvestable_animal.append((x, y))
                            if t.get("fertilizer_available", False):
                                fert_avail.append((x, y))
                        else:
                            empty_structs.append((x, y))
                    elif k == "WEED":
                        weed_tiles.append((x, y))

        has_animals = len(animal_tiles) > 0
        has_goose_shed = shed.get("GOOSE", 0) > 0
        has_goose_inv = any(inv.get("GOOSE", 0) > 0 for inv in inventories)
        has_goose_placed = any(
            isinstance(tiles[y][x], dict) and tiles[y][x].get("animal") == "GOOSE"
            for y in range(min(10, len(tiles)))
            for x in range(min(10, len(tiles[y]) if y < len(tiles) else 0))
            if isinstance(tiles[y][x], dict)
        )
        has_any_struct = len(all_structs) > 0

        # ==== MARKET ORDERS ====
        market_orders: list[list[Any]] = []

        # (A) LEAKY-BUCKET SELLING (FR-14, FR-15, FR-16, FR-17)
        sell_list: list[tuple[float, str, int]] = []
        for item in PRODUCTS:
            stock = shed.get(item, 0)
            if stock <= 0: continue
            reserve = 0
            if not is_endgame:
                if item == "WHEAT" and (has_animals or has_goose_shed or shed.get("COW", 0) > 0):
                    reserve = max(2, len(animal_tiles))
                elif item == "FERTILIZER" and unfert_melon:
                    reserve = min(len(unfert_melon), stock)
            avail = max(0, stock - reserve)
            if avail <= 0: continue
            dh = _ST.tracker.get_dump_hazard(item)
            bp = float(MARKET_PARAMS.get(item, {}).get("base", 50))
            sell_list.append((dh * 100.0 + bp, item, avail))

        sell_list.sort(key=lambda x: x[0], reverse=True)
        for _, item, avail in sell_list:
            if len(market_orders) >= 10: break
            if is_endgame or _ST.tracker.get_dump_hazard(item) > 0.35:
                qty = avail
            else:
                ci = market_inv.get(item, MARKET_I0)
                T = float(MARKET_PARAMS[item]["T"])
                if item in FRAGILE_COMMODITIES:
                    headroom = max(1, min(15, int(T * 0.35 - max(0, ci - MARKET_I0))))
                else:
                    headroom = max(5, int(T * 0.50))
                qty = min(avail, headroom)
            if qty > 0:
                market_orders.append(["SELL", item, qty])

        _ST.tracker.record_own_orders(market_orders)

        # (B) LAND EXPANSION (FR-05)
        next_q = None
        for q in [1, 2, 3]:
            if q not in uq:
                next_q = q
                break
        n_hands = len(my_farm.get("hands", []))
        if next_q is not None and len(market_orders) < 10:
            cost = QUADRANT_COSTS[next_q]
            npv = 25 * 15.0 * max(0, days_left - 2)
            buf = {1: 1800, 2: 2000, 3: 2500}.get(next_q, 2000)
            min_d = {1: 4, 2: 10, 3: 16}.get(next_q, 4)
            min_h = {1: 1, 2: 2, 3: 3}.get(next_q, 1)
            ok = (day >= min_d and days_left >= 8 and my_money >= cost + buf
                  and n_hands >= min_h and npv > 1.25 * cost)
            if next_q == 3 and posture not in ("AUTARKY", "TRAILING"):
                ok = False
            if ok:
                market_orders.append(["BUY_LAND"])
                my_money -= cost

        # (C) HIRING (FR-07)
        hires = int(my_farm.get("hires_today", 0))
        max_cap = min(8, len(uq) * 2)
        ptasks = (len(urgent_water) + len(ready_harvest) + len(unfed_animals) +
                  len(harvestable_animal) + len(fert_avail) +
                  min(len(plantable), sum(seeds.get(c, 0) for c in CROPS)))
        want = min(max_cap, max(0, (ptasks + 17) // 18))
        while hires < want and n_hands < max_cap and len(market_orders) < 10 and days_left >= 3:
            w = _fib(hires)
            if my_money >= w + 800:
                market_orders.append(["HIRE"])
                my_money -= w
                hires += 1
                n_hands += 1
            else:
                break

        # (D) ANIMAL PURCHASES (FR-12)
        if (not has_goose_placed and not has_goose_shed and not has_goose_inv
            and len(market_orders) < 10 and my_money >= 2200
            and days_left >= 12 and 1 in uq):
            market_orders.append(["BUY_ANIMAL", "GOOSE", 1])
            my_money -= 300

        # Cow under AUTARKY/TRAILING
        has_cow = any(
            isinstance(tiles[y][x], dict) and tiles[y][x].get("animal") == "COW"
            for y in range(min(10, len(tiles)))
            for x in range(min(10, len(tiles[y]) if y < len(tiles) else 0))
            if isinstance(tiles[y][x], dict)
        )
        if (posture in ("AUTARKY", "TRAILING") and not has_cow
            and shed.get("COW", 0) == 0 and day >= 8 and days_left >= 14
            and my_money >= 3500 and len(uq) >= 2 and len(market_orders) < 10):
            market_orders.append(["BUY_ANIMAL", "COW", 1])
            my_money -= 400

        # (D2) WHEAT FEED
        lc = len(animal_tiles) + shed.get("GOOSE", 0) + shed.get("COW", 0) + shed.get("SHEEP", 0)
        if lc > 0 and shed.get("WHEAT", 0) < max(2, lc) and my_money >= 100 and len(market_orders) < 10 and not is_endgame:
            need = min(max(2, lc) - shed.get("WHEAT", 0), 3)
            if need > 0:
                market_orders.append(["BUY_PRODUCT", "WHEAT", need])
                my_money -= need * market_price("WHEAT", market_inv.get("WHEAT", MARKET_I0))

        # (E) FERTILIZER
        if (unfert_melon and shed.get("FERTILIZER", 0) == 0
            and not fert_avail and my_money >= 2500
            and len(market_orders) < 10 and not is_endgame):
            market_orders.append(["BUY_PRODUCT", "FERTILIZER", 1])
            my_money -= market_price("FERTILIZER", market_inv.get("FERTILIZER", MARKET_I0))

        # (F) SEED PURCHASES (FR-08)
        if not is_endgame and days_left >= 3:
            if posture == "LEADING":
                buy_crops = ["WHEAT", "CARROT"]
            elif posture == "TRAILING":
                buy_crops = ["MELON", "WHEAT", "CARROT", "TOMATO", "STRAWBERRY"]
            elif posture == "AUTARKY":
                buy_crops = ["WHEAT"]
            else:
                buy_crops = ["WHEAT", "CARROT", "MELON"]

            for crop in buy_crops:
                if day > LAST_PLANT_DAY.get(crop, 30): continue
                if len(market_orders) >= 10: break
                cur = seeds.get(crop, 0)
                target_stock = 6 if crop in ("WHEAT", "CARROT") else 2
                deficit = target_stock - cur
                if deficit > 0 and my_money >= deficit * CROPS[crop]["seed"] + 500:
                    market_orders.append(["BUY_SEED", crop, deficit])
                    my_money -= deficit * CROPS[crop]["seed"]

        # ==== WORKER DISPATCH ====
        all_workers = [my_farm.get("farmer", [0, 0])] + my_farm.get("hands", [])
        wactions: list[list[Any]] = []
        claimed: set[tuple[int, int]] = set()
        seeds_used: dict[str, int] = {}

        for widx, pos in enumerate(all_workers):
            if (time.perf_counter() - t0) * 1000 > 35:
                wactions.append(["PASS"])
                continue

            wx, wy = (pos[0], pos[1]) if isinstance(pos, (list, tuple)) else (0, 0)
            ct = tiles[wy][wx] if 0 <= wy < len(tiles) and 0 <= wx < len(tiles[wy]) else None
            # Handle LOCKED string tiles — treat as impassable for actions
            if ct == "LOCKED":
                ct = None  # normalize for branching; movement is legal, actions are no-ops
            winv = inventories[widx] if widx < len(inventories) else {}
            act: list[Any] = ["PASS"]

            is_shed_adj = (wx, wy) in SHED_ACCESS_TILES
            on_unlocked = _is_unlocked(wx, wy, uq)

            # (1) On animal tile — Feed > Care > Collect > Harvest
            if isinstance(ct, dict) and ct.get("kind") in ("COOP", "PASTURE") and ct.get("animal"):
                if not ct.get("fed_today", False) and winv.get("WHEAT", 0) > 0:
                    act = ["FEED"]
                elif not ct.get("cared_today", False):
                    act = ["CARE"]
                elif ct.get("fertilizer_available", False):
                    act = ["COLLECT_FERTILIZER"]
                elif ct.get("yield_units", 0) > 0:
                    act = ["HARVEST"]
                elif not ct.get("fed_today", False) and shed.get("WHEAT", 0) > 0:
                    act = _step_towards(wx, wy, 4, 4)
                else:
                    tgt = _find_target(wx, wy, urgent_water, ready_harvest, plantable, unfed_animals, claimed)
                    act = _step_towards(wx, wy, tgt[0], tgt[1])

            # (2) On empty structure — place animal if carrying one
            elif isinstance(ct, dict) and ct.get("kind") in ("COOP", "PASTURE") and not ct.get("animal"):
                if winv.get("GOOSE", 0) > 0 and ct.get("kind") == "COOP":
                    act = ["PLACE", "GOOSE"]
                elif winv.get("COW", 0) > 0 and ct.get("kind") == "PASTURE":
                    act = ["PLACE", "COW"]
                elif winv.get("SHEEP", 0) > 0 and ct.get("kind") == "PASTURE":
                    act = ["PLACE", "SHEEP"]
                else:
                    tgt = _find_target(wx, wy, urgent_water, ready_harvest, plantable, unfed_animals, claimed)
                    act = _step_towards(wx, wy, tgt[0], tgt[1])

            # (3) On plant tile — Water > Harvest > Fertilize
            elif isinstance(ct, dict) and ct.get("kind") == "PLANT":
                crop = ct.get("crop", "WHEAT")
                cd = CROPS.get(crop, CROPS["WHEAT"])
                age = day - ct.get("planted_day", 0)
                if not ct.get("watered_today", False):
                    act = ["WATER"]
                    claimed.add((wx, wy))
                elif age >= cd["first_yield_day"] and (
                    ct.get("yield_units", 0) >= cd["max_yield"] or age >= cd["max_yield_day"] or days_left <= 2):
                    act = ["HARVEST"]
                    claimed.add((wx, wy))
                elif crop == "MELON" and winv.get("FERTILIZER", 0) > 0 and ct.get("fertilized_until_day", -1) < day:
                    act = ["FERTILIZE"]
                else:
                    tgt = _find_target(wx, wy, urgent_water, ready_harvest, plantable, unfed_animals, claimed)
                    act = _step_towards(wx, wy, tgt[0], tgt[1])

            # (4) On weed — dig it
            elif isinstance(ct, dict) and ct.get("kind") == "WEED":
                act = ["DIG"]

            # (5) On empty tile (or shed-adjacent tile that is empty/locked)
            elif ct is None:
                # First check: if shed-adjacent, try PICKUP if there's something useful
                pickup_done = False
                if is_shed_adj:
                    if shed.get("GOOSE", 0) > 0 and winv.get("GOOSE", 0) == 0:
                        has_ec = any(isinstance(tiles[ey][ex], dict) and tiles[ey][ex].get("kind") == "COOP"
                                     for ex, ey in empty_structs)
                        if has_ec:
                            act = ["PICKUP", "GOOSE", 1]
                            pickup_done = True
                    if not pickup_done and shed.get("COW", 0) > 0 and winv.get("COW", 0) == 0:
                        has_ep = any(isinstance(tiles[ey][ex], dict) and tiles[ey][ex].get("kind") == "PASTURE"
                                     for ex, ey in empty_structs)
                        if has_ep:
                            act = ["PICKUP", "COW", 1]
                            pickup_done = True
                    if not pickup_done and shed.get("WHEAT", 0) > 0 and winv.get("WHEAT", 0) == 0 and unfed_animals:
                        act = ["PICKUP", "WHEAT", 1]
                        pickup_done = True
                    if not pickup_done and shed.get("FERTILIZER", 0) > 0 and winv.get("FERTILIZER", 0) == 0 and unfert_melon:
                        act = ["PICKUP", "FERTILIZER", 1]
                        pickup_done = True

                # If nothing to pick up, try building or planting (only on unlocked tiles)
                if not pickup_done and on_unlocked:
                    if (has_goose_shed or has_goose_inv) and not has_any_struct and (wx, wy) == (4, 3):
                        act = ["BUILD_COOP"]
                    elif shed.get("COW", 0) > 0 and not any(
                        isinstance(tiles[ey][ex], dict) and tiles[ey][ex].get("kind") == "PASTURE"
                        for ex, ey in all_structs):
                        if (wx, wy) == (3, 3):
                            act = ["BUILD_PASTURE"]
                        else:
                            act = _step_towards(wx, wy, 3, 3)
                    elif days_left >= 3 and not is_endgame:
                        planted = False
                        for crop in _get_plant_order(posture, day, days_left, shed):
                            real = seeds.get(crop, 0) - seeds_used.get(crop, 0)
                            if real > 0 and day <= LAST_PLANT_DAY.get(crop, 30):
                                act = ["PLANT", crop]
                                seeds_used[crop] = seeds_used.get(crop, 0) + 1
                                planted = True
                                break
                        if not planted:
                            tgt = _find_target(wx, wy, urgent_water, ready_harvest, plantable, unfed_animals, claimed)
                            act = _step_towards(wx, wy, tgt[0], tgt[1])
                    else:
                        tgt = _find_target(wx, wy, urgent_water, ready_harvest, plantable, unfed_animals, claimed)
                        act = _step_towards(wx, wy, tgt[0], tgt[1])

                # If on locked tile with nothing to pick up, navigate to useful area
                elif not pickup_done:
                    tgt = _find_target(wx, wy, urgent_water, ready_harvest, plantable, unfed_animals, claimed)
                    act = _step_towards(wx, wy, tgt[0], tgt[1])

            # (6) Fallback navigation (carrying items or on unexpected tile)
            else:
                if winv.get("WHEAT", 0) > 0 and unfed_animals:
                    tgt = _nearest(wx, wy, unfed_animals)
                elif winv.get("FERTILIZER", 0) > 0 and unfert_melon:
                    tgt = _nearest(wx, wy, unfert_melon)
                elif winv.get("GOOSE", 0) > 0:
                    ec = [p for p in empty_structs
                          if isinstance(tiles[p[1]][p[0]], dict) and tiles[p[1]][p[0]].get("kind") == "COOP"]
                    tgt = _nearest(wx, wy, ec) if ec else (4, 3)
                elif winv.get("COW", 0) > 0:
                    ep = [p for p in empty_structs
                          if isinstance(tiles[p[1]][p[0]], dict) and tiles[p[1]][p[0]].get("kind") == "PASTURE"]
                    tgt = _nearest(wx, wy, ep) if ep else (3, 3)
                elif (has_goose_shed or has_goose_inv) and not has_any_struct:
                    tgt = (4, 3)
                elif has_goose_shed and empty_structs:
                    tgt = (4, 4)
                elif unfed_animals and shed.get("WHEAT", 0) > 0:
                    tgt = (4, 4)
                elif unfert_melon and shed.get("FERTILIZER", 0) > 0:
                    tgt = (4, 4)
                else:
                    tgt = _find_target(wx, wy, urgent_water, ready_harvest, plantable, unfed_animals, claimed)
                act = _step_towards(wx, wy, tgt[0], tgt[1])

            wactions.append(act)

        # ==== ASSEMBLE OUTPUT ====
        farmer = wactions[0] if wactions else ["PASS"]
        hands = wactions[1:] if len(wactions) > 1 else []

        if (time.perf_counter() - t0) * 1000 > 40:
            return FALLBACK

        return {
            "farmer": list(farmer),
            "hands": [list(h) for h in hands],
            "market": market_orders[:10],
        }

    except Exception:
        return FALLBACK
