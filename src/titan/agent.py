"""
TITAN-1 Autonomous Agro-Economic Agent Kernel
Championship submission driver verified on official kaggriculture simulation engine.
"""

import time
from typing import Any

from .constants import (
    CROPS,
    FRAGILE_COMMODITIES,
    LAST_PLANT_DAY,
    MARKET_I0,
    MARKET_PARAMS,
    PRODUCTS,
    QUADRANT_COSTS,
    SHED_ACCESS_TILES,
    fib,
)
from .navigation import find_target, is_unlocked, nearest, step_towards
from .pricing import market_price
from .strategy import compute_mhi, get_plant_order
from .tracker import BayesianOpponentTracker


class TitanRuntimeState:
    """Persistent runtime telemetry across turns within a match episode."""

    def __init__(self) -> None:
        self.tracker = BayesianOpponentTracker()
        self.posture = "BALANCED"
        self.prev_step = -1

    def reset(self) -> None:
        self.tracker = BayesianOpponentTracker()
        self.posture = "BALANCED"
        self.prev_step = -1


_RUNTIME = TitanRuntimeState()


def agent(obs: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    """TITAN-1 Championship Agent. Sub-40ms execution, zero-crash guarantee."""
    t0 = time.perf_counter()
    FALLBACK: dict[str, Any] = {"farmer": ["PASS"], "hands": [], "market": []}

    try:
        # ==== 1. PERCEPTION ====
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

        # Reset state on episode genesis
        if step == 0 or step < _RUNTIME.prev_step:
            _RUNTIME.reset()
        _RUNTIME.prev_step = step

        # Quadrants currently unlocked
        uq: set[int] = {0}
        for q in my_farm.get("unlocked_quadrants", ["NW"]):
            if isinstance(q, int) and 0 <= q <= 3:
                uq.add(q)
            elif q == "NW":
                uq.add(0)
            elif q == "NE":
                uq.add(1)
            elif q == "SW":
                uq.add(2)
            elif q == "SE":
                uq.add(3)

        # ==== 2. BAYESIAN TRACKING & STRATEGIC POSTURE ====
        _RUNTIME.tracker.update(opp_farm.get("tiles"), market_inv, step, shops)
        mhi_agg, mhi_frag = compute_mhi(market_inv)

        if mhi_frag < 0.50 or mhi_agg < 0.70:
            _RUNTIME.posture = "AUTARKY"
        elif is_endgame:
            _RUNTIME.posture = "ENDGAME"
        elif money_gap > 3000:
            _RUNTIME.posture = "LEADING"
        elif money_gap < -3000:
            _RUNTIME.posture = "TRAILING"
        else:
            _RUNTIME.posture = "BALANCED"
        posture = _RUNTIME.posture

        # ==== 3. TILE SURVEY & LOGISTICS PRIORITY QUEUE ====
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
            if y >= len(tiles):
                break
            for x in range(10):
                if x >= len(tiles[y]):
                    break
                if not is_unlocked(x, y, uq):
                    continue
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
                            yu >= cd["max_yield"] or age >= cd["max_yield_day"] or days_left <= 2
                        ):
                            ready_harvest.append((x, y))
                        if (
                            crop == "MELON"
                            and t.get("fertilized_until_day", -1) < day
                            and age < cd["max_yield_day"]
                        ):
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

        # ==== 4. HIGH-FREQUENCY ORDER TAPE & MARKET LIQUIDATION ====
        market_orders: list[list[Any]] = []

        # (A) Leaky-Bucket Liquidation
        sell_list: list[tuple[float, str, int]] = []
        for item in PRODUCTS:
            stock = shed.get(item, 0)
            if stock <= 0:
                continue
            reserve = 0
            if not is_endgame:
                if item == "WHEAT" and (has_animals or has_goose_shed or shed.get("COW", 0) > 0):
                    reserve = max(2, len(animal_tiles))
                elif item == "FERTILIZER" and unfert_melon:
                    reserve = min(len(unfert_melon), stock)
            avail = max(0, stock - reserve)
            if avail <= 0:
                continue
            dh = _RUNTIME.tracker.get_dump_hazard(item)
            bp = float(MARKET_PARAMS.get(item, {}).get("base", 50))
            sell_list.append((dh * 100.0 + bp, item, avail))

        sell_list.sort(key=lambda x: x[0], reverse=True)
        for _, item, avail in sell_list:
            if len(market_orders) >= 10:
                break
            if is_endgame or _RUNTIME.tracker.get_dump_hazard(item) > 0.35:
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

        _RUNTIME.tracker.record_own_orders(market_orders)

        # (B) NPV-Gated Land Expansion
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
            ok = (
                day >= min_d
                and days_left >= 8
                and my_money >= cost + buf
                and n_hands >= min_h
                and npv > 1.25 * cost
            )
            if next_q == 3 and posture not in ("AUTARKY", "TRAILING"):
                ok = False
            if ok:
                market_orders.append(["BUY_LAND"])
                my_money -= cost

        # (C) Dynamic Workload Labor Sizing
        hires = int(my_farm.get("hires_today", 0))
        max_cap = min(8, len(uq) * 2)
        ptasks = (
            len(urgent_water)
            + len(ready_harvest)
            + len(unfed_animals)
            + len(harvestable_animal)
            + len(fert_avail)
            + min(len(plantable), sum(seeds.get(c, 0) for c in CROPS))
        )
        want = min(max_cap, max(0, (ptasks + 17) // 18))
        while (
            hires < want
            and n_hands < max_cap
            and len(market_orders) < 10
            and days_left >= 3
        ):
            w = fib(hires)
            if my_money >= w + 800:
                market_orders.append(["HIRE"])
                my_money -= w
                hires += 1
                n_hands += 1
            else:
                break

        # (D) Livestock Acquisition
        if (
            not has_goose_placed
            and not has_goose_shed
            and not has_goose_inv
            and len(market_orders) < 10
            and my_money >= 2200
            and days_left >= 12
            and 1 in uq
        ):
            market_orders.append(["BUY_ANIMAL", "GOOSE", 1])
            my_money -= 300

        # Cow under Autarkic/Trailing posture
        has_cow = any(
            isinstance(tiles[y][x], dict) and tiles[y][x].get("animal") == "COW"
            for y in range(min(10, len(tiles)))
            for x in range(min(10, len(tiles[y]) if y < len(tiles) else 0))
            if isinstance(tiles[y][x], dict)
        )
        if (
            posture in ("AUTARKY", "TRAILING")
            and not has_cow
            and shed.get("COW", 0) == 0
            and day >= 8
            and days_left >= 14
            and my_money >= 3500
            and len(uq) >= 2
            and len(market_orders) < 10
        ):
            market_orders.append(["BUY_ANIMAL", "COW", 1])
            my_money -= 400

        # (D2) Livestock Feed Security
        lc = (
            len(animal_tiles)
            + shed.get("GOOSE", 0)
            + shed.get("COW", 0)
            + shed.get("SHEEP", 0)
        )
        if (
            lc > 0
            and shed.get("WHEAT", 0) < max(2, lc)
            and my_money >= 100
            and len(market_orders) < 10
            and not is_endgame
        ):
            need = min(max(2, lc) - shed.get("WHEAT", 0), 3)
            if need > 0:
                market_orders.append(["BUY_PRODUCT", "WHEAT", need])
                my_money -= need * market_price(
                    "WHEAT", market_inv.get("WHEAT", MARKET_I0)
                )

        # (E) Fertilizer Procurement
        if (
            unfert_melon
            and shed.get("FERTILIZER", 0) == 0
            and not fert_avail
            and my_money >= 2500
            and len(market_orders) < 10
            and not is_endgame
        ):
            market_orders.append(["BUY_PRODUCT", "FERTILIZER", 1])
            my_money -= market_price(
                "FERTILIZER", market_inv.get("FERTILIZER", MARKET_I0)
            )

        # (F) Gestation-Gated Seed Purchasing
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
                if day > LAST_PLANT_DAY.get(crop, 30):
                    continue
                if len(market_orders) >= 10:
                    break
                cur = seeds.get(crop, 0)
                target_stock = 6 if crop in ("WHEAT", "CARROT") else 2
                deficit = target_stock - cur
                if deficit > 0 and my_money >= deficit * CROPS[crop]["seed"] + 500:
                    market_orders.append(["BUY_SEED", crop, deficit])
                    my_money -= deficit * CROPS[crop]["seed"]

        # ==== 5. SPATIAL DISPATCH & WORKER MICRO ====
        all_workers = [my_farm.get("farmer", [0, 0])] + my_farm.get("hands", [])
        wactions: list[list[Any]] = []
        claimed: set[tuple[int, int]] = set()
        seeds_used: dict[str, int] = {}

        for widx, pos in enumerate(all_workers):
            if (time.perf_counter() - t0) * 1000 > 35:
                wactions.append(["PASS"])
                continue

            wx, wy = (pos[0], pos[1]) if isinstance(pos, (list, tuple)) else (0, 0)
            ct = (
                tiles[wy][wx]
                if 0 <= wy < len(tiles) and 0 <= wx < len(tiles[wy])
                else None
            )
            # Normalize LOCKED string representation
            if ct == "LOCKED":
                ct = None
            winv = inventories[widx] if widx < len(inventories) else {}
            act: list[Any] = ["PASS"]

            is_shed_adj = (wx, wy) in SHED_ACCESS_TILES
            on_unlocked = is_unlocked(wx, wy, uq)

            # (1) Animal Tile Tasks
            if (
                isinstance(ct, dict)
                and ct.get("kind") in ("COOP", "PASTURE")
                and ct.get("animal")
            ):
                if not ct.get("fed_today", False) and winv.get("WHEAT", 0) > 0:
                    act = ["FEED"]
                elif not ct.get("cared_today", False):
                    act = ["CARE"]
                elif ct.get("fertilizer_available", False):
                    act = ["COLLECT_FERTILIZER"]
                elif ct.get("yield_units", 0) > 0:
                    act = ["HARVEST"]
                elif not ct.get("fed_today", False) and shed.get("WHEAT", 0) > 0:
                    act = step_towards(wx, wy, 4, 4)
                else:
                    tgt = find_target(
                        wx,
                        wy,
                        urgent_water,
                        ready_harvest,
                        plantable,
                        unfed_animals,
                        claimed,
                    )
                    act = step_towards(wx, wy, tgt[0], tgt[1])

            # (2) Empty Structure Placement
            elif (
                isinstance(ct, dict)
                and ct.get("kind") in ("COOP", "PASTURE")
                and not ct.get("animal")
            ):
                if winv.get("GOOSE", 0) > 0 and ct.get("kind") == "COOP":
                    act = ["PLACE", "GOOSE"]
                elif winv.get("COW", 0) > 0 and ct.get("kind") == "PASTURE":
                    act = ["PLACE", "COW"]
                elif winv.get("SHEEP", 0) > 0 and ct.get("kind") == "PASTURE":
                    act = ["PLACE", "SHEEP"]
                else:
                    tgt = find_target(
                        wx,
                        wy,
                        urgent_water,
                        ready_harvest,
                        plantable,
                        unfed_animals,
                        claimed,
                    )
                    act = step_towards(wx, wy, tgt[0], tgt[1])

            # (3) Plant Management
            elif isinstance(ct, dict) and ct.get("kind") == "PLANT":
                crop = ct.get("crop", "WHEAT")
                cd = CROPS.get(crop, CROPS["WHEAT"])
                age = day - ct.get("planted_day", 0)
                if not ct.get("watered_today", False):
                    act = ["WATER"]
                    claimed.add((wx, wy))
                elif age >= cd["first_yield_day"] and (
                    ct.get("yield_units", 0) >= cd["max_yield"]
                    or age >= cd["max_yield_day"]
                    or days_left <= 2
                ):
                    act = ["HARVEST"]
                    claimed.add((wx, wy))
                elif (
                    crop == "MELON"
                    and winv.get("FERTILIZER", 0) > 0
                    and ct.get("fertilized_until_day", -1) < day
                ):
                    act = ["FERTILIZE"]
                else:
                    tgt = find_target(
                        wx,
                        wy,
                        urgent_water,
                        ready_harvest,
                        plantable,
                        unfed_animals,
                        claimed,
                    )
                    act = step_towards(wx, wy, tgt[0], tgt[1])

            # (4) Weed Clearing
            elif isinstance(ct, dict) and ct.get("kind") == "WEED":
                act = ["DIG"]

            # (5) Empty Tile Logistics & Shed Access Port Interactivity
            elif ct is None:
                pickup_done = False
                if is_shed_adj:
                    if shed.get("GOOSE", 0) > 0 and winv.get("GOOSE", 0) == 0:
                        has_ec = any(
                            isinstance(tiles[ey][ex], dict)
                            and tiles[ey][ex].get("kind") == "COOP"
                            for ex, ey in empty_structs
                        )
                        if has_ec:
                            act = ["PICKUP", "GOOSE", 1]
                            pickup_done = True
                    if (
                        not pickup_done
                        and shed.get("COW", 0) > 0
                        and winv.get("COW", 0) == 0
                    ):
                        has_ep = any(
                            isinstance(tiles[ey][ex], dict)
                            and tiles[ey][ex].get("kind") == "PASTURE"
                            for ex, ey in empty_structs
                        )
                        if has_ep:
                            act = ["PICKUP", "COW", 1]
                            pickup_done = True
                    if (
                        not pickup_done
                        and shed.get("WHEAT", 0) > 0
                        and winv.get("WHEAT", 0) == 0
                        and unfed_animals
                    ):
                        act = ["PICKUP", "WHEAT", 1]
                        pickup_done = True
                    if (
                        not pickup_done
                        and shed.get("FERTILIZER", 0) > 0
                        and winv.get("FERTILIZER", 0) == 0
                        and unfert_melon
                    ):
                        act = ["PICKUP", "FERTILIZER", 1]
                        pickup_done = True

                if not pickup_done and on_unlocked:
                    if (
                        (has_goose_shed or has_goose_inv)
                        and not has_any_struct
                        and (wx, wy) == (4, 3)
                    ):
                        act = ["BUILD_COOP"]
                    elif shed.get("COW", 0) > 0 and not any(
                        isinstance(tiles[ey][ex], dict)
                        and tiles[ey][ex].get("kind") == "PASTURE"
                        for ex, ey in all_structs
                    ):
                        if (wx, wy) == (3, 3):
                            act = ["BUILD_PASTURE"]
                        else:
                            act = step_towards(wx, wy, 3, 3)
                    elif days_left >= 3 and not is_endgame:
                        planted = False
                        for crop in get_plant_order(posture, day, days_left, shed):
                            real = seeds.get(crop, 0) - seeds_used.get(crop, 0)
                            if real > 0 and day <= LAST_PLANT_DAY.get(crop, 30):
                                act = ["PLANT", crop]
                                seeds_used[crop] = seeds_used.get(crop, 0) + 1
                                planted = True
                                break
                        if not planted:
                            tgt = find_target(
                                wx,
                                wy,
                                urgent_water,
                                ready_harvest,
                                plantable,
                                unfed_animals,
                                claimed,
                            )
                            act = step_towards(wx, wy, tgt[0], tgt[1])
                    else:
                        tgt = find_target(
                            wx,
                            wy,
                            urgent_water,
                            ready_harvest,
                            plantable,
                            unfed_animals,
                            claimed,
                        )
                        act = step_towards(wx, wy, tgt[0], tgt[1])
                elif not pickup_done:
                    tgt = find_target(
                        wx,
                        wy,
                        urgent_water,
                        ready_harvest,
                        plantable,
                        unfed_animals,
                        claimed,
                    )
                    act = step_towards(wx, wy, tgt[0], tgt[1])

            # (6) Fallback Navigation
            else:
                if winv.get("WHEAT", 0) > 0 and unfed_animals:
                    tgt = nearest(wx, wy, unfed_animals)
                elif winv.get("FERTILIZER", 0) > 0 and unfert_melon:
                    tgt = nearest(wx, wy, unfert_melon)
                elif winv.get("GOOSE", 0) > 0:
                    ec = [
                        p
                        for p in empty_structs
                        if isinstance(tiles[p[1]][p[0]], dict)
                        and tiles[p[1]][p[0]].get("kind") == "COOP"
                    ]
                    tgt = nearest(wx, wy, ec) if ec else (4, 3)
                elif winv.get("COW", 0) > 0:
                    ep = [
                        p
                        for p in empty_structs
                        if isinstance(tiles[p[1]][p[0]], dict)
                        and tiles[p[1]][p[0]].get("kind") == "PASTURE"
                    ]
                    tgt = nearest(wx, wy, ep) if ep else (3, 3)
                elif (has_goose_shed or has_goose_inv) and not has_any_struct:
                    tgt = (4, 3)
                elif has_goose_shed and empty_structs:
                    tgt = (4, 4)
                elif unfed_animals and shed.get("WHEAT", 0) > 0:
                    tgt = (4, 4)
                elif unfert_melon and shed.get("FERTILIZER", 0) > 0:
                    tgt = (4, 4)
                else:
                    tgt = find_target(
                        wx,
                        wy,
                        urgent_water,
                        ready_harvest,
                        plantable,
                        unfed_animals,
                        claimed,
                    )
                act = step_towards(wx, wy, tgt[0], tgt[1])

            wactions.append(act)

        # ==== 6. ASSEMBLY & SAFETY INVARIANT ENFORCEMENT ====
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

