"""
TITAN-1 Macroeconomic Strategy & Dynamic Posture Engine
FR-05, FR-08, FR-20: Relative objective theorem, gestation gates, and MHI calculation.
"""


from .constants import (
    FRAGILE_COMMODITIES,
    MARKET_I0,
    MARKET_PARAMS,
    PRODUCTS,
)
from .pricing import market_price


def compute_mhi(market_inv: dict[str, int]) -> tuple[float, float]:
    """Compute dual Market Health Index: (MHI_aggregate, MHI_fragile).
    MHI_agg: unweighted average of price ratios across 8 agricultural goods.
    MHI_fragile: minimum price ratio among fragile commodities (Melon, Strawberry, Milk, Wool).
    """
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


def get_plant_order(
    posture: str,
    days_left: int,
    shed: dict[str, int],
) -> list[str]:
    """Determine dynamic crop planting sequence gated by strategic posture and gestation timing."""
    if posture == "AUTARKY":
        return ["WHEAT"]
    if posture == "LEADING":
        return ["WHEAT", "CARROT"]
    if posture == "ENDGAME":
        return ["WHEAT", "CARROT"] if days_left >= 3 else []
    if posture == "TRAILING":
        result: list[str] = []
        if days_left >= 12:
            result.append("MELON")
        if days_left >= 16:
            result.append("STRAWBERRY")
        if days_left >= 11:
            result.append("TOMATO")
        if shed.get("WHEAT", 0) < 2:
            result.append("WHEAT")
        result.append("CARROT")
        if "WHEAT" not in result:
            result.append("WHEAT")
        return result

    # BALANCED posture
    result = []
    if days_left >= 12:
        result.append("MELON")
    if shed.get("WHEAT", 0) < 2:
        result.append("WHEAT")
    result.append("CARROT")
    if "WHEAT" not in result:
        result.append("WHEAT")
    return result

