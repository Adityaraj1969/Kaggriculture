"""
TITAN-1: Autonomous Championship Agro-Economic Simulation Kernel
Kaggle Simulations // Google LLC Kaggriculture Tournament Pool
"""

from .agent import agent
from .constants import (
    ANIMALS,
    CROPS,
    FRAGILE_COMMODITIES,
    LAST_PLANT_DAY,
    MARKET_I0,
    MARKET_PARAMS,
    PRODUCTS,
    QUADRANT_COSTS,
    SHED_ACCESS_TILES,
    SHOPS,
)
from .pricing import compute_sell_revenue, market_price, shape
from .strategy import compute_mhi, get_plant_order
from .tracker import BayesianOpponentTracker

__version__ = "2.0.0"
__all__ = [
    "agent",
    "market_price",
    "compute_sell_revenue",
    "shape",
    "compute_mhi",
    "get_plant_order",
    "BayesianOpponentTracker",
    "CROPS",
    "ANIMALS",
    "PRODUCTS",
    "MARKET_PARAMS",
    "MARKET_I0",
    "FRAGILE_COMMODITIES",
    "LAST_PLANT_DAY",
    "QUADRANT_COSTS",
    "SHED_ACCESS_TILES",
    "SHOPS",
]
