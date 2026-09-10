"""
TITAN-1 Spatial Navigation & Mesh Pathfinding
FR-09, FR-10: Global walkable mesh navigation and priority targeting.
"""



def get_quadrant(x: int, y: int) -> int:
    """Return quadrant index for coordinates (0: NW, 1: NE, 2: SW, 3: SE)."""
    if x < 5 and y < 5:
        return 0
    if x >= 5 and y < 5:
        return 1
    if x < 5 and y >= 5:
        return 2
    return 3


def is_unlocked(x: int, y: int, uq: set[int]) -> bool:
    """Check if coordinate resides in currently unlocked quadrant."""
    return get_quadrant(x, y) in uq


def manhattan(x1: int, y1: int, x2: int, y2: int) -> int:
    """Manhattan distance between two 2D points."""
    return abs(x1 - x2) + abs(y1 - y2)


def step_towards(cx: int, cy: int, tx: int, ty: int) -> list[str]:
    """Single greedy step towards target coordinate over the global walkable mesh.
    All tiles are walkable in the engine; locked status only gates field actions.
    """
    if cx == tx and cy == ty:
        return ["PASS"]
    best_dir = "PASS"
    best_dist = manhattan(cx, cy, tx, ty)
    for dx, dy, name in [(0, -1, "NORTH"), (0, 1, "SOUTH"), (-1, 0, "WEST"), (1, 0, "EAST")]:
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < 10 and 0 <= ny < 10:
            d = manhattan(nx, ny, tx, ty)
            if d < best_dist:
                best_dist = d
                best_dir = name
    return [best_dir]


def nearest(wx: int, wy: int, tiles_list: list[tuple[int, int]]) -> tuple[int, int]:
    """Find nearest coordinate from a list of candidates."""
    if not tiles_list:
        return (0, 0)
    return min(tiles_list, key=lambda t: manhattan(wx, wy, t[0], t[1]))


def find_target(
    wx: int,
    wy: int,
    urgent_water: list[tuple[int, int]],
    ready_harvest: list[tuple[int, int]],
    plantable: list[tuple[int, int]],
    unfed: list[tuple[int, int]],
    claimed: set[tuple[int, int]],
) -> tuple[int, int]:
    """Find the nearest high-priority unclaimed task tile."""
    for tile_list in [unfed, urgent_water, ready_harvest, plantable]:
        unclaimed = [t for t in tile_list if t not in claimed]
        if unclaimed:
            return nearest(wx, wy, unclaimed)
    return (0, 0)

