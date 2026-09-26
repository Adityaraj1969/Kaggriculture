"""
TITAN-1 v3 :: Championship Agent
Kaggle Kaggriculture ($50,000 Tournament)
Strategy: Aggressive crops + livestock economy + max workforce.
"""

import math
from typing import Any

# ============================================================================
# CONSTANTS
# ============================================================================

CROPS: dict[str, dict[str, Any]] = {
    "WHEAT":      {"seed": 10, "first_yield_day": 2, "max_yield_day": 4, "interval": 0, "max_yield": 6, "ongoing": False},
    "CARROT":     {"seed": 20, "first_yield_day": 2, "max_yield_day": 3, "interval": 0, "max_yield": 4, "ongoing": False},
    "TOMATO":     {"seed": 50, "first_yield_day": 8, "max_yield_day": 8, "interval": 1, "max_yield": 4, "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True},
    "MELON":      {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False},
}

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]

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

LAST_PLANT_DAY = {"WHEAT": 27, "CARROT": 27, "MELON": 19, "TOMATO": 21, "STRAWBERRY": 19}
QUADRANT_COSTS = {1: 1000, 2: 2000, 3: 4000}

# Build spots per quadrant — each quadrant has multiple structure slots
# NW quadrant (always unlocked)
NW_PASTURE = [(3, 3), (1, 4), (3, 1), (0, 2), (1, 2), (0, 0)]
NW_COOP = [(4, 3), (2, 4), (4, 1), (0, 3)]
# NE quadrant (first expansion)
NE_PASTURE = [(6, 3), (8, 4), (6, 1), (9, 2)]
NE_COOP = [(5, 3), (7, 4), (5, 1), (9, 3)]
# SW quadrant (second expansion)
SW_PASTURE = [(3, 6), (1, 8), (3, 9), (0, 7)]
SW_COOP = [(4, 6), (2, 8), (4, 9), (0, 8)]

SHED_ACCESS_TILES = {(4, 4), (5, 4), (4, 5), (5, 5)}


def _fib(n: int) -> int:
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _shape(func: str, x: float, T: float = 0.0) -> float:
    x = max(0.0, x)
    if func == "linear": return x
    if func == "sq": return x * x
    if func == "sqrt": return math.sqrt(x)
    if func == "log": return math.log(1.0 + x)
    if func == "log10": return math.log10(1.0 + x)
    if func == "hinge":
        if T <= 0: return x
        u = x / T
        return u + HINGE_GAIN * max(0.0, u - 1.0) ** 2
    return x


def market_price(item: str, inventory: int) -> int:
    p = MARKET_PARAMS[item]
    base, I0, T = float(p["base"]), float(p["I0"]), float(p["T"])
    if inventory < I0:
        f, bt = str(p["below_func"]), float(p["below_target"])
        amp = bt * base / _shape(f, T, T)
        price = base + amp * _shape(f, I0 - inventory, T)
    else:
        f, at = str(p["above_func"]), float(p["above_target"])
        amp = at * base / _shape(f, T, T)
        price = base - amp * _shape(f, inventory - I0, T)
    return max(PRICE_FLOOR, int(round(price)))


# ============================================================================
# NAVIGATION
# ============================================================================

def _quadrant(x: int, y: int) -> int:
    if x < 5 and y < 5: return 0
    if x >= 5 and y < 5: return 1
    if x < 5 and y >= 5: return 2
    return 3


def _unlocked(x: int, y: int, uq: set[int]) -> bool:
    return _quadrant(x, y) in uq


def _dist(x1: int, y1: int, x2: int, y2: int) -> int:
    return abs(x1 - x2) + abs(y1 - y2)


def _move(cx: int, cy: int, tx: int, ty: int) -> list[str]:
    if cx == tx and cy == ty: return ["PASS"]
    best, bd = "PASS", _dist(cx, cy, tx, ty)
    for dx, dy, d in [(0, -1, "NORTH"), (0, 1, "SOUTH"), (-1, 0, "WEST"), (1, 0, "EAST")]:
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < 10 and 0 <= ny < 10:
            dd = _dist(nx, ny, tx, ty)
            if dd < bd: bd, best = dd, d
    return [best]


def _nearest(wx: int, wy: int, pts: list[tuple[int, int]]) -> tuple[int, int]:
    if not pts: return (4, 4)
    return min(pts, key=lambda p: _dist(wx, wy, p[0], p[1]))


def _pasture_spots(uq: set[int]) -> list[tuple[int, int]]:
    spots = list(NW_PASTURE)
    if 1 in uq: spots += NE_PASTURE
    if 2 in uq: spots += SW_PASTURE
    return spots


def _coop_spots(uq: set[int]) -> list[tuple[int, int]]:
    spots = list(NW_COOP)
    if 1 in uq: spots += NE_COOP
    if 2 in uq: spots += SW_COOP
    return spots


# ============================================================================
# STATE
# ============================================================================

class _S:
    prev = -1
_ST = _S()


# ============================================================================
# HELPER FUNCTIONS (must be before agent — engine uses get_last_callable)
# ============================================================================

def _plant(seeds: dict, su: dict, day: int, dleft: int) -> list[Any]:
    order = []
    if day >= 8:
        # Mid/late game: plant high-value crops first if available
        if dleft >= 12: order.append("STRAWBERRY")
        if dleft >= 12: order.append("MELON")
        if dleft >= 10: order.append("TOMATO")
    if dleft >= 3: order.append("WHEAT")
    if dleft >= 3: order.append("CARROT")
    if day < 8:
        # Early game: high-value as fallback if we have seeds
        if dleft >= 12: order.append("STRAWBERRY")
        if dleft >= 12: order.append("MELON")
        if dleft >= 10: order.append("TOMATO")
    for c in order:
        if day > LAST_PLANT_DAY.get(c, 30): continue
        if seeds.get(c, 0) - su.get(c, 0) > 0:
            return ["PLANT", c]
    return ["PASS"]


def _work(wx: int, wy: int, water: list, harvest: list, empty: list,
          unfed: list, afert: list, aharvest: list,
          claimed: set) -> tuple[int, int]:
    for lst in [unfed, afert, water, aharvest, harvest, empty]:
        unc = [t for t in lst if t not in claimed]
        if unc:
            b = _nearest(wx, wy, unc)
            claimed.add(b)
            return b
    return (4, 4)


# ============================================================================
# MAIN AGENT (must be LAST callable — Kaggle engine uses get_last_callable)
# ============================================================================

def agent(obs: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    """TITAN-1 v3 Championship Agent."""
    FB: dict[str, Any] = {"farmer": ["PASS"], "hands": [], "market": []}
    try:
        pid = obs.get("player", 0)
        farms = obs.get("farms", [{}, {}])
        mf = farms[pid] if pid < len(farms) else {}
        priv = obs.get("private", {})
        shed = priv.get("shed", {})
        seeds = priv.get("seeds", {})
        invs = priv.get("inventories", [{}])
        mkt = obs.get("market", {})
        mkt_inv = mkt.get("inventory", {}) if isinstance(mkt, dict) else {}

        day = int(obs.get("day", 0))
        hour = int(obs.get("hour", 0))
        step = int(obs.get("step", day * 24 + hour))
        dleft = 30 - day
        endgame = day >= 28

        tiles = mf.get("tiles", [])
        money = float(mf.get("money", 0.0))

        if step == 0 or step < _ST.prev:
            _ST.prev = -1
        _ST.prev = step

        # Unlocked quadrants
        uq: set[int] = {0}
        for q in mf.get("unlocked_quadrants", ["NW"]):
            if isinstance(q, int) and 0 <= q <= 3: uq.add(q)
            elif q == "NW": uq.add(0)
            elif q == "NE": uq.add(1)
            elif q == "SW": uq.add(2)
            elif q == "SE": uq.add(3)

        # ---- TILE SURVEY ----
        water: list[tuple[int, int]] = []       # need watering
        harvest: list[tuple[int, int]] = []      # ready to harvest crop
        empty: list[tuple[int, int]] = []        # plantable empty tiles
        unfed: list[tuple[int, int]] = []        # animals needing feed
        uncared: list[tuple[int, int]] = []      # animals needing care
        aharvest: list[tuple[int, int]] = []     # animals with product
        afert: list[tuple[int, int]] = []        # animals with fertilizer
        estructs: list[tuple[int, int]] = []     # empty structures
        structs: list[tuple[int, int]] = []      # all structures
        weeds: list[tuple[int, int]] = []

        for y in range(min(10, len(tiles))):
            for x in range(min(10, len(tiles[y]))):
                if not _unlocked(x, y, uq): continue
                t = tiles[y][x]
                if t is None:
                    if (x, y) not in SHED_ACCESS_TILES:
                        empty.append((x, y))
                elif isinstance(t, dict):
                    k = t.get("kind")
                    if k == "PLANT":
                        cr = t.get("crop", "WHEAT")
                        cd = CROPS.get(cr, CROPS["WHEAT"])
                        age = day - t.get("planted_day", 0)
                        if not t.get("watered_today", False):
                            water.append((x, y))
                        yu = t.get("yield_units", 0)
                        if age >= cd["first_yield_day"] and (
                            yu >= cd["max_yield"] or age >= cd["max_yield_day"] or dleft <= 2):
                            harvest.append((x, y))
                    elif k in ("COOP", "PASTURE"):
                        structs.append((x, y))
                        if t.get("animal"):
                            if not t.get("fed_today", False):
                                unfed.append((x, y))
                            if not t.get("cared_today", False):
                                uncared.append((x, y))
                            if t.get("yield_units", 0) > 0:
                                aharvest.append((x, y))
                            if t.get("fertilizer_available", False):
                                afert.append((x, y))
                        else:
                            estructs.append((x, y))
                    elif k == "WEED":
                        weeds.append((x, y))

        # Animal census
        def _cnt(kind: str) -> tuple[int, int]:
            pl = sum(1 for y2 in range(min(10, len(tiles)))
                     for x2 in range(min(10, len(tiles[y2]) if y2 < len(tiles) else 0))
                     if isinstance(tiles[y2][x2], dict) and tiles[y2][x2].get("animal") == kind)
            pend = shed.get(kind, 0) + sum(iv.get(kind, 0) for iv in invs)
            return pl, pend

        cow_p, cow_q = _cnt("COW")
        sheep_p, sheep_q = _cnt("SHEEP")
        goose_p, goose_q = _cnt("GOOSE")

        n_past = sum(1 for ex, ey in structs
                     if isinstance(tiles[ey][ex], dict) and tiles[ey][ex].get("kind") == "PASTURE")
        n_coop = sum(1 for ex, ey in structs
                     if isinstance(tiles[ey][ex], dict) and tiles[ey][ex].get("kind") == "COOP")
        total_a = cow_p + sheep_p + goose_p

        # How many structures do we NEED vs HAVE?
        need_pasture = max(0, (cow_p + cow_q + sheep_p + sheep_q) - n_past)
        need_coop = max(0, (goose_p + goose_q) - n_coop)

        # ---- MARKET ORDERS ----
        orders: list[list[Any]] = []
        nh = len(mf.get("hands", []))

        # (A) SELL everything from shed
        wt_reserve = max(2, total_a + cow_q + sheep_q + goose_q) if not endgame else 0
        for item in PRODUCTS:
            stk = shed.get(item, 0)
            if stk <= 0 or len(orders) >= 10: continue
            avail = stk if (item != "WHEAT" or endgame) else max(0, stk - wt_reserve)
            if avail > 0:
                orders.append(["SELL", item, avail])

        # (B) HIRE — aggressive daily (hands reset each morning)
        hires_today = int(mf.get("hires_today", 0))
        max_hands = min(12, len(uq) * 4)
        while hires_today < max_hands and nh < max_hands and len(orders) < 10:
            hc = _fib(hires_today)
            # Keep enough for animal/seed purchases
            buf = 200 if day >= 3 else 400
            if money >= hc + buf:
                orders.append(["HIRE"])
                money -= hc
                hires_today += 1
                nh += 1
            else:
                break

        # (C) ANIMALS — gradual scaling, 1 per turn max
        # Top ranker: 13 cows, 3 sheep, 2 geese over 30 days
        # Scale: buy 1 cow per day for first 10 days, then sheep/goose
        if len(orders) < 10 and not endgame and dleft >= 8:
            if day <= 1 and (cow_p + cow_q) == 0 and money >= 500:
                # First cow on day 0-1
                orders.append(["BUY_ANIMAL", "COW", 1])
                money -= 400
            elif day >= 2 and (cow_p + cow_q) < min(8, day + 1) and cow_q <= 1 and money >= 700 and dleft >= 10:
                orders.append(["BUY_ANIMAL", "COW", 1])
                money -= 400
            elif (sheep_p + sheep_q) < 3 and sheep_q == 0 and money >= 800 and dleft >= 10 and cow_p >= 2:
                orders.append(["BUY_ANIMAL", "SHEEP", 1])
                money -= 500
            elif (goose_p + goose_q) < 2 and goose_q == 0 and money >= 600 and dleft >= 8 and cow_p >= 2:
                orders.append(["BUY_ANIMAL", "GOOSE", 1])
                money -= 300

        # (D) BUY WHEAT for animal feed
        feed_need = total_a + cow_q + sheep_q + goose_q
        wt_have = shed.get("WHEAT", 0) + sum(iv.get("WHEAT", 0) for iv in invs)
        if feed_need > 0 and wt_have < feed_need and len(orders) < 10 and not endgame:
            need = min(feed_need - wt_have + 1, 5)
            wp = market_price("WHEAT", mkt_inv.get("WHEAT", MARKET_I0))
            if money >= need * wp + 100:
                orders.append(["BUY_PRODUCT", "WHEAT", need])
                money -= need * wp

        # (E) LAND EXPANSION
        nq = None
        for q in [1, 2, 3]:
            if q not in uq:
                nq = q
                break
        if nq is not None and len(orders) < 10:
            cost = QUADRANT_COSTS[nq]
            md = {1: 5, 2: 10, 3: 16}.get(nq, 5)
            if day >= md and dleft >= 6 and money >= cost + 800:
                orders.append(["BUY_LAND"])
                money -= cost

        # (F) SEEDS — buy every turn to keep pipeline full
        if not endgame and dleft >= 3:
            plans: list[tuple[str, int]] = []
            if day <= LAST_PLANT_DAY.get("WHEAT", 30):
                c = seeds.get("WHEAT", 0)
                if c < 4: plans.append(("WHEAT", min(4, 4 - c)))
            if day <= LAST_PLANT_DAY.get("CARROT", 30):
                c = seeds.get("CARROT", 0)
                if c < 3: plans.append(("CARROT", min(3, 3 - c)))
            if dleft >= 12 and day <= LAST_PLANT_DAY.get("STRAWBERRY", 30) and money >= 500:
                c = seeds.get("STRAWBERRY", 0)
                if c < 3: plans.append(("STRAWBERRY", max(1, 3 - c)))
            if dleft >= 12 and day <= LAST_PLANT_DAY.get("MELON", 30) and money >= 500:
                c = seeds.get("MELON", 0)
                if c < 3: plans.append(("MELON", max(1, 3 - c)))
            if dleft >= 10 and day <= LAST_PLANT_DAY.get("TOMATO", 30) and money >= 400:
                c = seeds.get("TOMATO", 0)
                if c < 2: plans.append(("TOMATO", max(1, 2 - c)))

            for crop, qty in plans:
                if len(orders) >= 10: break
                cost = qty * CROPS[crop]["seed"]
                if money >= cost + 100:
                    orders.append(["BUY_SEED", crop, qty])
                    money -= cost

        # ---- WORKER DISPATCH ----
        workers = [mf.get("farmer", [0, 0])] + mf.get("hands", [])
        acts: list[list[Any]] = []
        claimed: set[tuple[int, int]] = set()
        su: dict[str, int] = {}  # seeds used this turn

        # Precompute available pasture/coop build spots
        p_spots = [s for s in _pasture_spots(uq) if 0 <= s[1] < len(tiles) and 0 <= s[0] < len(tiles[s[1]]) and tiles[s[1]][s[0]] is None]
        c_spots = [s for s in _coop_spots(uq) if 0 <= s[1] < len(tiles) and 0 <= s[0] < len(tiles[s[1]]) and tiles[s[1]][s[0]] is None]

        for wi, pos in enumerate(workers):
            wx, wy = (pos[0], pos[1]) if isinstance(pos, (list, tuple)) else (0, 0)
            ct = tiles[wy][wx] if 0 <= wy < len(tiles) and 0 <= wx < len(tiles[wy]) else None
            if ct == "LOCKED": ct = None
            inv = invs[wi] if wi < len(invs) else {}
            a: list[Any] = ["PASS"]
            sa = (wx, wy) in SHED_ACCESS_TILES

            # --- carrying animal? deliver it ---
            car = None
            if inv.get("COW", 0) > 0: car = "COW"
            elif inv.get("SHEEP", 0) > 0: car = "SHEEP"
            elif inv.get("GOOSE", 0) > 0: car = "GOOSE"

            if car is not None:
                sk = "PASTURE" if car != "GOOSE" else "COOP"
                # On an empty matching structure? Place it
                if isinstance(ct, dict) and ct.get("kind") == sk and not ct.get("animal"):
                    a = ["PLACE", car]
                else:
                    # Find empty matching structure
                    emp = [p for p in estructs
                           if isinstance(tiles[p[1]][p[0]], dict) and tiles[p[1]][p[0]].get("kind") == sk]
                    if emp:
                        tgt = _nearest(wx, wy, emp)
                        a = _move(wx, wy, tgt[0], tgt[1])
                    else:
                        # Need to build — go to build spot
                        spots = p_spots if sk == "PASTURE" else c_spots
                        if spots:
                            bs = _nearest(wx, wy, spots)
                            if (wx, wy) == bs:
                                a = ["BUILD_PASTURE"] if sk == "PASTURE" else ["BUILD_COOP"]
                            else:
                                a = _move(wx, wy, bs[0], bs[1])
                        else:
                            # No spots available, drop animal at shed
                            if sa:
                                a = ["DROP", car, 1]
                            else:
                                tgt = _nearest(wx, wy, list(SHED_ACCESS_TILES))
                                a = _move(wx, wy, tgt[0], tgt[1])
                acts.append(a)
                continue

            # --- carrying wheat for feed? deliver ---
            if 0 < inv.get("WHEAT", 0) <= 3 and unfed:
                tgt = _nearest(wx, wy, unfed)
                if isinstance(ct, dict) and ct.get("kind") in ("COOP", "PASTURE") and ct.get("animal") and not ct.get("fed_today", False):
                    a = ["FEED"]
                else:
                    a = _move(wx, wy, tgt[0], tgt[1])
                acts.append(a)
                continue

            # --- carrying fertilizer? drop at shed ---
            if inv.get("FERTILIZER", 0) > 0:
                if sa:
                    a = ["DROP", "FERTILIZER", inv["FERTILIZER"]]
                else:
                    tgt = _nearest(wx, wy, list(SHED_ACCESS_TILES))
                    a = _move(wx, wy, tgt[0], tgt[1])
                acts.append(a)
                continue

            # --- on animal structure with animal ---
            if isinstance(ct, dict) and ct.get("kind") in ("COOP", "PASTURE") and ct.get("animal"):
                if not ct.get("fed_today", False) and inv.get("WHEAT", 0) > 0:
                    a = ["FEED"]
                elif not ct.get("cared_today", False):
                    a = ["CARE"]
                elif ct.get("fertilizer_available", False):
                    a = ["COLLECT_FERTILIZER"]
                elif ct.get("yield_units", 0) > 0:
                    a = ["HARVEST"]
                else:
                    a = _move(wx, wy, *_work(wx, wy, water, harvest, empty, unfed, afert, aharvest, claimed))
                acts.append(a)
                continue

            # --- on empty structure without animal ---
            if isinstance(ct, dict) and ct.get("kind") in ("COOP", "PASTURE") and not ct.get("animal"):
                a = _move(wx, wy, *_work(wx, wy, water, harvest, empty, unfed, afert, aharvest, claimed))
                acts.append(a)
                continue

            # --- on plant ---
            if isinstance(ct, dict) and ct.get("kind") == "PLANT":
                cr = ct.get("crop", "WHEAT")
                cd = CROPS.get(cr, CROPS["WHEAT"])
                age = day - ct.get("planted_day", 0)
                if not ct.get("watered_today", False):
                    a = ["WATER"]
                    claimed.add((wx, wy))
                elif age >= cd["first_yield_day"] and (
                    ct.get("yield_units", 0) >= cd["max_yield"] or age >= cd["max_yield_day"] or dleft <= 2):
                    a = ["HARVEST"]
                    claimed.add((wx, wy))
                else:
                    a = _move(wx, wy, *_work(wx, wy, water, harvest, empty, unfed, afert, aharvest, claimed))
                acts.append(a)
                continue

            # --- on weed ---
            if isinstance(ct, dict) and ct.get("kind") == "WEED":
                a = ["DIG"]
                acts.append(a)
                continue

            # --- on empty tile ---
            if ct is None:
                # Shed-adjacent: pick up animals or wheat
                if sa:
                    picked = False
                    for atype, sk in [("COW", "PASTURE"), ("SHEEP", "PASTURE"), ("GOOSE", "COOP")]:
                        if shed.get(atype, 0) > 0:
                            # Check we have somewhere to put it
                            emp = [p for p in estructs
                                   if isinstance(tiles[p[1]][p[0]], dict) and tiles[p[1]][p[0]].get("kind") == sk]
                            bspots = p_spots if sk == "PASTURE" else c_spots
                            if emp or bspots:
                                a = ["PICKUP", atype, 1]
                                picked = True
                                break
                    if not picked and shed.get("WHEAT", 0) > 0 and unfed:
                        a = ["PICKUP", "WHEAT", min(shed.get("WHEAT", 0), 3)]
                        picked = True
                    if not picked:
                        # Check if we need to build a structure here
                        if need_pasture > 0 and (wx, wy) in p_spots:
                            a = ["BUILD_PASTURE"]
                            need_pasture -= 1
                        elif need_coop > 0 and (wx, wy) in c_spots:
                            a = ["BUILD_COOP"]
                            need_coop -= 1
                        elif _unlocked(wx, wy, uq) and not endgame and dleft >= 3:
                            a = _plant(seeds, su, day, dleft)
                            if a[0] == "PLANT":
                                su[a[1]] = su.get(a[1], 0) + 1
                            else:
                                a = _move(wx, wy, *_work(wx, wy, water, harvest, empty, unfed, afert, aharvest, claimed))
                        else:
                            a = _move(wx, wy, *_work(wx, wy, water, harvest, empty, unfed, afert, aharvest, claimed))
                # Not shed-adjacent: build structure if needed, else plant/work
                elif _unlocked(wx, wy, uq):
                    if need_pasture > 0 and (wx, wy) in p_spots:
                        a = ["BUILD_PASTURE"]
                        need_pasture -= 1
                    elif need_coop > 0 and (wx, wy) in c_spots:
                        a = ["BUILD_COOP"]
                        need_coop -= 1
                    elif not endgame and dleft >= 3:
                        a = _plant(seeds, su, day, dleft)
                        if a[0] == "PLANT":
                            su[a[1]] = su.get(a[1], 0) + 1
                        else:
                            a = _move(wx, wy, *_work(wx, wy, water, harvest, empty, unfed, afert, aharvest, claimed))
                    else:
                        a = _move(wx, wy, *_work(wx, wy, water, harvest, empty, unfed, afert, aharvest, claimed))
                else:
                    a = _move(wx, wy, *_work(wx, wy, water, harvest, empty, unfed, afert, aharvest, claimed))
                acts.append(a)
                continue

            # --- fallback ---
            a = _move(wx, wy, *_work(wx, wy, water, harvest, empty, unfed, afert, aharvest, claimed))
            acts.append(a)

        farmer = acts[0] if acts else ["PASS"]
        hands = acts[1:] if len(acts) > 1 else []

        return {
            "farmer": list(farmer),
            "hands": [list(h) for h in hands],
            "market": orders[:10],
        }
    except Exception:
        return FB

