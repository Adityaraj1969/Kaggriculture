"""
TITAN-1 Bayesian Opponent Belief & Mass-Balance Reconciler
FR-02, FR-03, FR-04: Solves information asymmetry by reconstructing hidden shed stockpiles.
"""

import math
from typing import Any

from .constants import MARKET_I0, PRODUCTS, SHOPS


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
        """Record own emitted orders to isolate opponent market participation."""
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

    def update(
        self,
        opp_tiles: list[list[Any]] | None,
        market_inv: dict[str, int],
        step: int,
        shops: list[str],
    ) -> None:
        """Update Bayesian belief with new step observation."""
        # 1. Harvest detection from public opponent tile state transitions
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

        # 2. Multi-force market inventory reconciliation
        if self.prev_market_inv is not None and market_inv:
            drain = self._calc_town_drain(step, shops)
            for c in self.commodities:
                curr_i = market_inv.get(c, MARKET_I0)
                prev_i = self.prev_market_inv.get(c, MARKET_I0)
                delta = curr_i - prev_i
                opp_sales = (
                    delta + drain.get(c, 0) - self.our_sales.get(c, 0) + self.our_buys.get(c, 0)
                )
                if opp_sales > 0:
                    self.hoarded_shed_est[c] = max(0, self.hoarded_shed_est[c] - opp_sales)

        self.prev_opp_tiles = [row[:] for row in opp_tiles] if opp_tiles else None
        self.prev_market_inv = dict(market_inv) if market_inv else None

    def _calc_town_drain(self, step: int, shops: list[str]) -> dict[str, int]:
        """Compute theoretical town shop absorption for this turn."""
        drain: dict[str, int] = {c: 0 for c in self.commodities}
        # Town Center: 1 unit every 24 turns
        if step % 24 == 0:
            for c in self.commodities:
                drain[c] += 1
        # Town Shops: consume every 4 turns
        if step % 4 == 0:
            for shop_name in shops:
                products = SHOPS.get(shop_name, [])
                mult = 2 if len(products) == 1 else 1
                for item in products:
                    if item in drain:
                        drain[item] += mult
        return drain

    def get_dump_hazard(self, commodity: str) -> float:
        """Hazard function: probability of opponent dumping hoarded inventory."""
        stock = self.hoarded_shed_est.get(commodity, 0)
        return float(1.0 - math.exp(-stock / 12.0))

