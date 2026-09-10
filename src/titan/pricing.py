"""
TITAN-1 Market Micro-Structure & Exact Price Simulation
Replicates the official continuous non-linear elasticity formulation.
"""

import math

from .constants import HINGE_GAIN, MARKET_PARAMS, PRICE_FLOOR


def shape(func: str, x: float, T: float = 0.0) -> float:
    """Exact mathematical replica of kaggriculture.py _shape function."""
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
    """Compute exact spot market price matching the engine. Floored at PRICE_FLOOR."""
    p = MARKET_PARAMS[item]
    base = float(p["base"])
    I0 = float(p["I0"])
    T = float(p["T"])
    if inventory < I0:
        f = str(p["below_func"])
        below_target = float(p["below_target"])
        amp = below_target * base / shape(f, T, T)
        price = base + amp * shape(f, I0 - inventory, T)
    else:
        f = str(p["above_func"])
        above_target = float(p["above_target"])
        amp = above_target * base / shape(f, T, T)
        price = base - amp * shape(f, inventory - I0, T)
    return max(PRICE_FLOOR, int(round(price)))


def compute_sell_revenue(item: str, quantity: int, current_inv: int) -> int:
    """Simulate exact cumulative revenue when liquidating quantity units sequentially."""
    total = 0
    inv = current_inv
    for _ in range(quantity):
        p = market_price(item, inv)
        total += p
        if p > PRICE_FLOOR:
            inv += 1
    return total

