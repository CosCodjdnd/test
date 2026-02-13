"""Tile-based overworld maps for the Feral Gods GUI.

Each map is a 2-D list of tile IDs plus metadata (NPC positions, shrine
locations, encounter zones).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .constants import (
    TILE_GRASS, TILE_PATH, TILE_WATER, TILE_TREE, TILE_STONE,
    TILE_SHRINE, TILE_WALL, TILE_DOOR, TILE_SAND,
    TILE_SIZE, PASSABLE_TILES,
)


@dataclass
class MapPortal:
    """A door / transition between maps."""
    x: int       # tile x
    y: int       # tile y
    target_map: str
    target_x: int
    target_y: int


@dataclass
class MapEnemy:
    """An enemy encounter zone on the map."""
    x: int
    y: int
    min_level: int = 1
    max_level: int = 3


@dataclass
class GameMap:
    """A single tile-based map."""
    name: str
    width: int   # in tiles
    height: int  # in tiles
    tiles: list[list[int]]
    start_x: int = 3
    start_y: int = 3
    portals: list[MapPortal] = field(default_factory=list)
    shrines: list[tuple[int, int, str]] = field(default_factory=list)  # (x, y, god_name)
    encounter_zone: bool = True  # random encounters on grass

    def get_tile(self, tx: int, ty: int) -> int:
        if 0 <= ty < self.height and 0 <= tx < self.width:
            return self.tiles[ty][tx]
        return TILE_WALL  # out of bounds = wall

    def is_passable(self, tx: int, ty: int) -> bool:
        return self.get_tile(tx, ty) in PASSABLE_TILES

    def get_portal(self, tx: int, ty: int) -> MapPortal | None:
        for p in self.portals:
            if p.x == tx and p.y == ty:
                return p
        return None

    def get_shrine(self, tx: int, ty: int) -> str | None:
        for sx, sy, god_name in self.shrines:
            if sx == tx and sy == ty:
                return god_name
        return None


# ── pre-built maps ────────────────────────────────────────────────────

G = TILE_GRASS
P = TILE_PATH
W = TILE_WATER
T = TILE_TREE
S = TILE_STONE
H = TILE_SHRINE  # shrine
X = TILE_WALL
D = TILE_DOOR
A = TILE_SAND

def _village_map() -> GameMap:
    """Starting village – Ceremony grounds."""
    tiles = [
        [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
        [T, G, G, G, G, P, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, T],
        [T, G, G, G, G, P, G, G, G, G, G, G, T, G, G, G, G, G, G, T, G, G, G, G, T],
        [T, G, G, S, S, P, S, S, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, T],
        [T, G, G, S, G, P, G, S, G, G, T, G, G, G, G, G, T, G, G, G, G, T, G, G, T],
        [T, P, P, P, P, P, P, P, P, P, P, P, P, P, P, P, P, P, P, P, P, P, P, P, T],
        [T, G, G, S, G, P, G, S, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, T],
        [T, G, G, S, S, P, S, S, G, G, G, G, T, G, G, G, G, G, G, G, G, G, G, G, T],
        [T, G, G, G, G, P, G, G, G, G, G, G, G, G, G, G, G, G, T, G, G, G, G, G, T],
        [T, G, G, G, G, P, G, G, G, G, T, G, G, G, G, G, G, G, G, G, G, T, G, G, T],
        [T, G, G, G, G, P, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, T],
        [T, G, G, G, G, P, G, G, G, G, G, G, G, G, W, W, G, G, G, G, G, G, G, G, T],
        [T, G, G, G, G, P, G, G, G, G, G, G, G, W, W, W, W, G, G, G, G, G, G, G, T],
        [T, G, T, G, G, P, G, G, G, G, G, G, G, G, W, W, G, G, G, G, G, G, G, G, T],
        [T, G, G, G, G, P, P, P, P, P, P, P, P, P, P, P, P, P, P, P, D, G, G, G, T],
        [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    ]
    return GameMap(
        name="Eldergrove Village",
        width=25,
        height=16,
        tiles=tiles,
        start_x=5,
        start_y=8,
        portals=[
            MapPortal(20, 14, "wilds", 2, 1),
        ],
        encounter_zone=False,  # no random encounters in village
    )


def _wilds_map() -> GameMap:
    """Wilderness – random encounters, shrine entrances."""
    tiles = [
        [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
        [T, D, G, G, G, G, G, G, T, G, G, G, G, G, G, T, G, G, G, G, G, G, G, G, T],
        [T, G, G, G, G, G, G, G, G, G, G, G, T, G, G, G, G, G, G, G, G, G, T, G, T],
        [T, G, G, P, P, P, P, G, G, G, G, G, G, G, G, G, G, T, G, G, G, G, G, G, T],
        [T, G, G, P, G, G, P, G, G, T, G, G, G, G, G, G, G, G, G, G, H, G, G, G, T],
        [T, G, G, P, G, G, P, P, P, P, P, P, P, P, P, P, P, P, G, G, G, G, G, G, T],
        [T, G, G, P, G, G, G, G, G, G, G, G, T, G, G, G, G, P, G, G, G, G, G, G, T],
        [T, T, G, P, G, G, G, T, G, G, G, G, G, G, G, G, G, P, G, G, G, T, G, G, T],
        [T, G, G, P, G, G, G, G, G, G, T, G, G, G, G, G, G, P, G, G, G, G, G, G, T],
        [T, G, G, P, P, P, P, P, P, G, G, G, G, G, G, G, G, P, G, G, G, G, G, G, T],
        [T, G, G, G, G, G, G, G, P, G, G, T, G, G, G, G, G, P, G, G, G, T, G, G, T],
        [T, G, G, G, T, G, G, G, P, G, G, G, G, G, G, T, G, P, P, P, G, G, G, G, T],
        [T, G, G, G, G, G, G, G, P, P, P, P, P, P, G, G, G, G, G, P, G, G, G, G, T],
        [T, G, T, G, G, G, G, G, G, G, T, G, G, P, G, G, G, G, G, P, G, G, T, G, T],
        [T, G, G, G, G, H, G, G, G, G, G, G, G, P, P, P, P, P, P, P, P, P, D, G, T],
        [T, G, G, G, G, G, G, G, G, T, G, G, G, G, G, G, T, G, G, G, G, G, G, G, T],
        [T, G, G, G, G, G, G, T, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, T],
        [T, G, G, G, G, G, G, G, G, G, G, T, G, G, G, G, G, G, G, T, G, G, G, G, T],
        [T, G, G, H, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, G, T],
        [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    ]
    return GameMap(
        name="The Wilds",
        width=25,
        height=20,
        tiles=tiles,
        start_x=2,
        start_y=1,
        portals=[
            MapPortal(1, 1, "village", 19, 14),
            MapPortal(22, 14, "deep_wilds", 2, 1),
        ],
        shrines=[
            (20, 4, "Galanth"),
            (5, 14, "Ophidia"),
            (3, 18, "Karn"),
        ],
        encounter_zone=True,
    )


def _deep_wilds_map() -> GameMap:
    """Deeper wilderness – harder encounters, more shrines."""
    tiles = [
        [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
        [T, D, G, G, G, G, T, G, G, G, G, G, G, T, G, G, G, G, G, G, G, G, G, G, T],
        [T, G, G, G, G, G, G, G, G, T, G, G, G, G, G, G, G, G, T, G, G, G, G, G, T],
        [T, G, G, P, P, P, G, G, G, G, G, G, G, G, G, G, G, G, G, G, H, G, G, G, T],
        [T, G, G, P, G, P, G, G, T, G, G, G, G, G, G, T, G, G, G, G, G, G, T, G, T],
        [T, G, G, P, G, P, P, P, P, P, P, P, P, G, G, G, G, G, G, G, G, G, G, G, T],
        [T, G, G, P, G, G, G, G, T, G, G, G, P, G, G, G, G, G, G, G, G, G, G, G, T],
        [T, G, G, P, G, G, G, G, G, G, G, G, P, G, G, G, T, G, G, G, G, G, G, G, T],
        [T, T, G, P, G, T, G, G, G, G, G, G, P, G, G, G, G, G, G, G, G, G, G, G, T],
        [T, G, G, P, P, P, P, P, P, P, G, G, P, G, G, G, G, G, G, G, G, T, G, G, T],
        [T, G, G, G, G, G, G, G, G, P, G, G, P, P, P, P, G, G, G, G, G, G, G, G, T],
        [T, G, G, H, G, G, G, G, G, P, G, G, G, G, G, P, G, G, G, G, G, G, G, G, T],
        [T, G, G, G, G, W, W, G, G, P, G, G, G, G, G, P, G, G, G, G, G, T, G, G, T],
        [T, G, G, G, W, W, W, W, G, P, G, G, G, G, G, P, G, G, G, G, G, G, G, G, T],
        [T, G, G, G, G, W, W, G, G, P, P, P, G, G, G, P, P, P, P, P, G, G, G, G, T],
        [T, G, G, G, G, G, H, G, G, G, G, P, G, G, G, G, G, G, G, P, G, G, G, G, T],
        [T, G, G, G, G, G, G, G, G, G, G, P, P, P, P, P, G, G, G, P, G, G, G, G, T],
        [T, G, T, G, G, G, G, G, G, G, G, G, G, G, G, P, G, G, G, P, G, G, T, G, T],
        [T, G, G, G, G, G, G, G, T, G, G, G, G, G, G, P, P, P, P, P, G, H, G, G, T],
        [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    ]
    return GameMap(
        name="Deep Wilds",
        width=25,
        height=20,
        tiles=tiles,
        start_x=2,
        start_y=1,
        portals=[
            MapPortal(1, 1, "wilds", 21, 14),
        ],
        shrines=[
            (20, 3, "Pelagon"),
            (3, 11, "Myriad"),
            (6, 15, "Pachymos"),
            (21, 18, "Skulk"),
        ],
    )


# ── map registry ──────────────────────────────────────────────────────

def get_all_maps() -> dict[str, GameMap]:
    return {
        "village": _village_map(),
        "wilds": _wilds_map(),
        "deep_wilds": _deep_wilds_map(),
    }
