"""Procedural pixel-art sprite generation for the Feral Gods GUI.

Generates all character, enemy, and tile sprites at runtime so no external
asset files are required.  Inspired by classic 16-bit JRPG aesthetics.
"""

from __future__ import annotations

import math
from typing import Sequence

import pygame

from .constants import (
    TILE_SIZE, GOD_COLORS, BLACK, WHITE, GREY, DARK_GREY, LIGHT_GREY,
    GREEN, BLUE, YELLOW, RED, BROWN, CYAN,
    TILE_GRASS, TILE_PATH, TILE_WATER, TILE_TREE, TILE_STONE,
    TILE_SHRINE, TILE_WALL, TILE_DOOR, TILE_SAND,
)


# ── helpers ────────────────────────────────────────────────────────────

def _rect(surf: pygame.Surface, color: Sequence[int],
          x: int, y: int, w: int, h: int) -> None:
    pygame.draw.rect(surf, color, (x, y, w, h))


def _pixel(surf: pygame.Surface, color: Sequence[int],
           x: int, y: int, size: int = 1) -> None:
    pygame.draw.rect(surf, color, (x, y, size, size))


def _circle(surf: pygame.Surface, color: Sequence[int],
            cx: int, cy: int, r: int) -> None:
    pygame.draw.circle(surf, color, (cx, cy), r)


def _shade(base: tuple[int, ...], factor: float) -> tuple[int, ...]:
    """Darken / lighten a colour.  factor < 1 = darker, > 1 = lighter."""
    return tuple(max(0, min(255, int(c * factor))) for c in base)


# ── tile sprites ───────────────────────────────────────────────────────

_tile_cache: dict[int, pygame.Surface] = {}


def get_tile_sprite(tile_type: int) -> pygame.Surface:
    """Return a cached TILE_SIZE × TILE_SIZE surface for the tile type."""
    if tile_type in _tile_cache:
        return _tile_cache[tile_type]

    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    ts = TILE_SIZE

    if tile_type == TILE_GRASS:
        surf.fill((60, 140, 50))
        # dithered texture
        for i in range(0, ts, 4):
            for j in range(0, ts, 4):
                if (i + j) % 8 == 0:
                    _pixel(surf, (50, 130, 40), i, j, 2)
        # tufts
        for x in (6, 18, 26):
            pygame.draw.line(surf, (40, 110, 30), (x, ts - 2), (x - 1, ts - 6), 1)
            pygame.draw.line(surf, (40, 110, 30), (x, ts - 2), (x + 1, ts - 6), 1)

    elif tile_type == TILE_PATH:
        surf.fill((170, 150, 110))
        for i in range(0, ts, 6):
            for j in range(0, ts, 6):
                if (i * 3 + j * 7) % 11 < 3:
                    _pixel(surf, (150, 130, 95), i, j, 3)

    elif tile_type == TILE_WATER:
        surf.fill((40, 90, 180))
        for i in range(0, ts, 4):
            y_off = 2 if (i // 4) % 2 == 0 else 0
            pygame.draw.line(surf, (60, 120, 210), (i, 8 + y_off), (i + 3, 8 + y_off), 1)
            pygame.draw.line(surf, (60, 120, 210), (i, 20 + y_off), (i + 3, 20 + y_off), 1)

    elif tile_type == TILE_TREE:
        surf.fill((60, 140, 50))  # grass base
        # trunk
        _rect(surf, (100, 70, 30), ts // 2 - 2, ts // 2, 4, ts // 2)
        # canopy
        _circle(surf, (30, 100, 30), ts // 2, ts // 3, ts // 3)
        _circle(surf, (40, 120, 40), ts // 2 - 3, ts // 3 + 2, ts // 4)
        _circle(surf, (40, 120, 40), ts // 2 + 3, ts // 3 + 2, ts // 4)

    elif tile_type == TILE_STONE:
        surf.fill((120, 120, 120))
        for i in range(0, ts, 8):
            for j in range(0, ts, 4):
                offset = 4 if (j // 4) % 2 == 0 else 0
                pygame.draw.rect(surf, (100, 100, 100),
                                 (i + offset, j, 7, 3), 1)

    elif tile_type == TILE_SHRINE:
        surf.fill((60, 140, 50))  # grass base
        # stone platform
        _rect(surf, (160, 150, 140), 4, 8, ts - 8, ts - 12)
        # pillar
        _rect(surf, (200, 190, 170), ts // 2 - 3, 4, 6, ts - 12)
        # glow
        _circle(surf, (255, 255, 180), ts // 2, 6, 4)

    elif tile_type == TILE_WALL:
        surf.fill((80, 70, 60))
        for j in range(0, ts, 8):
            for i in range(0, ts, 16):
                offset = 8 if (j // 8) % 2 == 0 else 0
                pygame.draw.rect(surf, (70, 60, 50),
                                 (i + offset, j, 15, 7), 1)

    elif tile_type == TILE_DOOR:
        surf.fill((80, 70, 60))  # wall bg
        _rect(surf, (120, 80, 40), 6, 2, ts - 12, ts - 2)
        # door handle
        _pixel(surf, YELLOW, ts // 2 + 4, ts // 2, 2)

    elif tile_type == TILE_SAND:
        surf.fill((210, 190, 130))
        for i in range(0, ts, 5):
            for j in range(0, ts, 5):
                if (i * 7 + j * 3) % 13 < 4:
                    _pixel(surf, (200, 180, 120), i, j, 2)

    else:
        surf.fill(BLACK)

    _tile_cache[tile_type] = surf
    return surf


# ── character / enemy sprites (64×64 battle view) ─────────────────────

def _draw_humanoid(surf: pygame.Surface, skin: tuple, hair: tuple,
                   shirt: tuple, pants: tuple, w: int, h: int,
                   facing_left: bool = False) -> None:
    """Draw a simple JRPG-style humanoid sprite onto *surf*."""
    cx = w // 2
    # head
    head_r = w // 6
    head_y = h // 5
    _circle(surf, skin, cx, head_y, head_r)
    # hair
    _circle(surf, hair, cx, head_y - 2, head_r + 1)
    _rect(surf, skin, cx - head_r + 1, head_y - 1, head_r * 2 - 2, head_r)
    # eyes
    eye_off = -3 if facing_left else 3
    _pixel(surf, BLACK, cx - 3, head_y - 1, 2)
    _pixel(surf, BLACK, cx + 2, head_y - 1, 2)
    # body / shirt
    body_top = head_y + head_r
    body_h = h // 3
    _rect(surf, shirt, cx - w // 5, body_top, w * 2 // 5, body_h)
    # arms
    arm_w = w // 8
    _rect(surf, shirt, cx - w // 5 - arm_w, body_top + 2, arm_w, body_h - 4)
    _rect(surf, shirt, cx + w // 5, body_top + 2, arm_w, body_h - 4)
    # hands
    _rect(surf, skin, cx - w // 5 - arm_w, body_top + body_h - 4, arm_w, 4)
    _rect(surf, skin, cx + w // 5, body_top + body_h - 4, arm_w, 4)
    # legs / pants
    leg_top = body_top + body_h
    leg_h = h - leg_top - 4
    leg_w = w // 6
    _rect(surf, pants, cx - leg_w - 1, leg_top, leg_w, leg_h)
    _rect(surf, pants, cx + 1, leg_top, leg_w, leg_h)
    # boots
    _rect(surf, DARK_GREY, cx - leg_w - 2, leg_top + leg_h, leg_w + 2, 4)
    _rect(surf, DARK_GREY, cx, leg_top + leg_h, leg_w + 2, 4)


def create_player_sprite(god_name: str | None = None,
                         size: int = 64) -> pygame.Surface:
    """Generate a player battle sprite coloured by god affiliation."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    color = GOD_COLORS.get(god_name or "", (100, 140, 200))
    skin = (230, 190, 150)
    hair = _shade(color, 0.6)
    shirt = color
    pants = _shade(color, 0.5)
    _draw_humanoid(surf, skin, hair, shirt, pants, size, size)
    return surf


def create_player_overworld(god_name: str | None = None,
                            direction: int = 0) -> pygame.Surface:
    """Generate a small 32×32 overworld walking sprite."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    color = GOD_COLORS.get(god_name or "", (100, 140, 200))
    skin = (230, 190, 150)
    ts = TILE_SIZE
    cx, cy = ts // 2, ts // 2

    # head
    _circle(surf, skin, cx, cy - 6, 5)
    # hair
    _circle(surf, _shade(color, 0.6), cx, cy - 8, 5)
    _rect(surf, skin, cx - 4, cy - 7, 8, 5)
    # eyes
    _pixel(surf, BLACK, cx - 2, cy - 7, 2)
    _pixel(surf, BLACK, cx + 1, cy - 7, 2)
    # body
    _rect(surf, color, cx - 5, cy, 10, 10)
    # legs
    _rect(surf, _shade(color, 0.5), cx - 4, cy + 10, 3, 5)
    _rect(surf, _shade(color, 0.5), cx + 1, cy + 10, 3, 5)
    # boots
    _rect(surf, DARK_GREY, cx - 5, cy + 14, 4, 2)
    _rect(surf, DARK_GREY, cx + 1, cy + 14, 4, 2)

    return surf


# ── enemy sprites ──────────────────────────────────────────────────────

def _draw_beast(surf: pygame.Surface, color: tuple, w: int, h: int,
                beast_type: str = "generic") -> None:
    """Draw a beast / monster sprite."""
    cx, cy = w // 2, h // 2

    if beast_type in ("snake", "lizard", "crocodile", "basilisk", "dragon", "wyvern", "komodo"):
        # Reptilian body
        body_color = color
        _rect(surf, body_color, cx - w // 4, cy - 4, w // 2, h // 4)
        # head
        _circle(surf, body_color, cx + w // 5, cy - 6, w // 6)
        # eye
        _pixel(surf, RED, cx + w // 5 + 2, cy - 8, 3)
        # tail
        pygame.draw.line(surf, _shade(body_color, 0.8),
                         (cx - w // 4, cy), (cx - w // 3 - 4, cy + 8), 3)
        if beast_type in ("dragon", "wyvern"):
            # wings
            pts = [(cx - 4, cy - 8), (cx - 16, cy - 24), (cx + 8, cy - 16)]
            pygame.draw.polygon(surf, _shade(body_color, 1.2), pts)
            # flames
            for i in range(3):
                _circle(surf, (255, 160, 40), cx + w // 5 + 8 + i * 3, cy - 6, 3 - i)

    elif beast_type in ("wolf", "dog", "lion", "panther", "sabertooth", "cerberus"):
        # Quadruped body
        body_color = color
        _rect(surf, body_color, cx - w // 4, cy - 6, w // 2, h // 5)
        # head
        _circle(surf, body_color, cx + w // 5, cy - 8, w // 7)
        # ears
        _rect(surf, _shade(body_color, 0.8), cx + w // 5 - 4, cy - 16, 3, 5)
        _rect(surf, _shade(body_color, 0.8), cx + w // 5 + 2, cy - 16, 3, 5)
        # eye
        _pixel(surf, YELLOW, cx + w // 5 + 2, cy - 9, 2)
        # legs
        for lx in (cx - w // 5, cx - w // 8, cx + w // 10, cx + w // 5):
            _rect(surf, _shade(body_color, 0.7), lx, cy + h // 10, 3, h // 4)
        # tail
        pygame.draw.line(surf, _shade(body_color, 0.8),
                         (cx - w // 4, cy - 2), (cx - w // 3 - 6, cy - 10), 2)
        if beast_type == "cerberus":
            _circle(surf, body_color, cx + w // 5, cy - 18, w // 9)
            _circle(surf, body_color, cx + w // 5 + 8, cy - 14, w // 9)

    elif beast_type in ("hawk", "eagle", "sparrow", "owl", "phoenix", "griffin", "pteranodon"):
        # Bird
        body_color = color
        # body
        _circle(surf, body_color, cx, cy, w // 5)
        # head
        _circle(surf, body_color, cx + w // 6, cy - w // 5, w // 8)
        # beak
        _rect(surf, YELLOW, cx + w // 4, cy - w // 5 - 1, 5, 3)
        # eye
        _pixel(surf, BLACK, cx + w // 6 + 2, cy - w // 5 - 1, 2)
        # wings
        pts_l = [(cx - 2, cy - 4), (cx - w // 3, cy - w // 3), (cx - w // 5, cy + 4)]
        pts_r = [(cx + 2, cy - 4), (cx + w // 3, cy - w // 3), (cx + w // 5, cy + 4)]
        pygame.draw.polygon(surf, _shade(body_color, 1.1), pts_l)
        pygame.draw.polygon(surf, _shade(body_color, 1.1), pts_r)
        # tail feathers
        pygame.draw.line(surf, _shade(body_color, 0.7),
                         (cx, cy + w // 5), (cx - 4, cy + w // 3), 2)
        pygame.draw.line(surf, _shade(body_color, 0.7),
                         (cx, cy + w // 5), (cx + 4, cy + w // 3), 2)
        if beast_type == "phoenix":
            for i in range(4):
                _circle(surf, (255, 180, 40), cx - 2 + i * 3, cy + w // 3 - 2, 3)

    elif beast_type in ("fish", "shark", "dolphin", "jellyfish", "octopus", "kraken", "leviathan"):
        # Aquatic
        body_color = color
        _circle(surf, body_color, cx, cy, w // 4)
        if beast_type in ("shark", "dolphin", "fish", "leviathan"):
            # fins
            pts = [(cx, cy - w // 6), (cx - 4, cy - w // 3), (cx + 4, cy - w // 3)]
            pygame.draw.polygon(surf, _shade(body_color, 0.8), pts)
            # tail
            pts = [(cx - w // 4, cy), (cx - w // 3, cy - 6), (cx - w // 3, cy + 6)]
            pygame.draw.polygon(surf, _shade(body_color, 0.9), pts)
            _pixel(surf, BLACK, cx + 4, cy - 2, 2)
        elif beast_type in ("octopus", "kraken"):
            # tentacles
            for i in range(6):
                angle = math.pi / 2 + (i - 2.5) * 0.4
                ex = int(cx + math.cos(angle) * w // 3)
                ey = int(cy + math.sin(angle) * h // 3)
                pygame.draw.line(surf, _shade(body_color, 0.8), (cx, cy + w // 6), (ex, ey), 2)
            _pixel(surf, WHITE, cx - 3, cy - 3, 3)
            _pixel(surf, WHITE, cx + 2, cy - 3, 3)
            _pixel(surf, BLACK, cx - 2, cy - 2, 2)
            _pixel(surf, BLACK, cx + 3, cy - 2, 2)
        elif beast_type == "jellyfish":
            # dome
            _circle(surf, _shade(body_color, 1.2), cx, cy - 4, w // 5)
            for i in range(5):
                sx = cx - 8 + i * 4
                pygame.draw.line(surf, _shade(body_color, 0.8), (sx, cy + 4), (sx, cy + h // 3), 1)

    elif beast_type in ("ant", "bee", "beetle", "spider", "scorpion", "dragonfly"):
        # Insect
        body_color = color
        # body segments
        _circle(surf, body_color, cx - 4, cy, w // 8)
        _circle(surf, body_color, cx + 4, cy, w // 7)
        _circle(surf, _shade(body_color, 0.8), cx + 12, cy, w // 8)
        # legs
        for side in (-1, 1):
            for i in range(3):
                lx = cx - 4 + i * 6
                pygame.draw.line(surf, _shade(body_color, 0.6),
                                 (lx, cy + 4), (lx + side * 6, cy + 12), 2)
        # eyes
        _pixel(surf, RED, cx + 14, cy - 3, 2)
        if beast_type in ("bee", "dragonfly"):
            # wings
            pygame.draw.ellipse(surf, (200, 200, 255, 160),
                                (cx - 8, cy - 16, 12, 10))
            pygame.draw.ellipse(surf, (200, 200, 255, 160),
                                (cx + 2, cy - 16, 12, 10))
        if beast_type == "scorpion":
            # tail
            pts = [(cx - 8, cy), (cx - 16, cy - 12), (cx - 18, cy - 18)]
            pygame.draw.lines(surf, _shade(body_color, 0.7), False, pts, 3)
            _circle(surf, RED, cx - 18, cy - 20, 3)

    elif beast_type in ("horse", "rhino", "elephant", "mammoth", "triceratops", "behemoth"):
        # Large herbivore
        body_color = color
        _rect(surf, body_color, cx - w // 4, cy - 8, w // 2, h // 4)
        _circle(surf, body_color, cx + w // 5, cy - 10, w // 7)
        # legs
        for lx in (cx - w // 5, cx - w // 10, cx + w // 12, cx + w // 5):
            _rect(surf, _shade(body_color, 0.7), lx, cy + h // 10 - 4, 5, h // 3)
        # eye
        _pixel(surf, BLACK, cx + w // 5 + 3, cy - 12, 2)
        if beast_type in ("rhino", "triceratops"):
            _rect(surf, LIGHT_GREY, cx + w // 5 + 6, cy - 14, 6, 3)
        if beast_type in ("mammoth", "elephant"):
            pygame.draw.line(surf, _shade(body_color, 0.8),
                             (cx + w // 4, cy - 6), (cx + w // 4 + 4, cy + 6), 3)
        if beast_type == "behemoth":
            _rect(surf, _shade(body_color, 0.6), cx - w // 4 - 4, cy - 12, w // 2 + 8, 4)

    elif beast_type in ("rat", "bat", "raccoon", "monkey", "jackalope"):
        # Small creature
        body_color = color
        _circle(surf, body_color, cx, cy, w // 6)
        _circle(surf, body_color, cx + 6, cy - 6, w // 8)
        _pixel(surf, BLACK, cx + 8, cy - 7, 2)
        # ears
        _rect(surf, _shade(body_color, 1.1), cx + 3, cy - 14, 3, 5)
        _rect(surf, _shade(body_color, 1.1), cx + 8, cy - 14, 3, 5)
        if beast_type == "bat":
            pts_l = [(cx - 4, cy - 2), (cx - 20, cy - 14), (cx - 6, cy + 6)]
            pts_r = [(cx + 4, cy - 2), (cx + 20, cy - 14), (cx + 6, cy + 6)]
            pygame.draw.polygon(surf, _shade(body_color, 0.8), pts_l)
            pygame.draw.polygon(surf, _shade(body_color, 0.8), pts_r)
        if beast_type == "jackalope":
            pygame.draw.line(surf, (200, 180, 140), (cx + 4, cy - 14), (cx + 2, cy - 22), 2)
            pygame.draw.line(surf, (200, 180, 140), (cx + 9, cy - 14), (cx + 11, cy - 22), 2)

    elif beast_type in ("fox", "otter", "chimpanzee", "gorilla", "sphinx"):
        body_color = color
        if beast_type in ("chimpanzee", "gorilla"):
            # Ape - upright
            _circle(surf, body_color, cx, cy - 8, w // 6)
            _rect(surf, body_color, cx - w // 6, cy, w // 3, h // 4)
            _rect(surf, _shade(body_color, 0.7), cx - w // 6 - 4, cy + 2, 4, h // 5)
            _rect(surf, _shade(body_color, 0.7), cx + w // 6, cy + 2, 4, h // 5)
            _rect(surf, _shade(body_color, 0.8), cx - 4, cy + h // 4, 3, h // 5)
            _rect(surf, _shade(body_color, 0.8), cx + 2, cy + h // 4, 3, h // 5)
            _pixel(surf, BLACK, cx - 2, cy - 10, 2)
            _pixel(surf, BLACK, cx + 2, cy - 10, 2)
        elif beast_type == "sphinx":
            # Mythical: lion body + human-ish head
            _rect(surf, body_color, cx - w // 4, cy, w // 2, h // 5)
            _circle(surf, (220, 180, 140), cx + w // 6, cy - 10, w // 7)
            for lx in (cx - w // 5, cx + w // 6):
                _rect(surf, _shade(body_color, 0.7), lx, cy + h // 6, 4, h // 4)
            _pixel(surf, BLUE, cx + w // 6 + 2, cy - 12, 3)
            # headdress
            _rect(surf, YELLOW, cx + w // 6 - 6, cy - 18, 12, 4)
        else:
            # Fox / otter
            _circle(surf, body_color, cx, cy, w // 6)
            _circle(surf, body_color, cx + 8, cy - 6, w // 8)
            _pixel(surf, BLACK, cx + 10, cy - 7, 2)
            _rect(surf, _shade(body_color, 1.1), cx + 5, cy - 14, 3, 5)
            _rect(surf, _shade(body_color, 1.1), cx + 10, cy - 14, 3, 5)
            pygame.draw.line(surf, _shade(body_color, 0.7),
                             (cx - w // 6, cy + 2), (cx - w // 4, cy + 8), 2)

    else:
        # Generic blob
        _circle(surf, color, cx, cy, w // 4)
        _pixel(surf, BLACK, cx - 3, cy - 3, 3)
        _pixel(surf, BLACK, cx + 2, cy - 3, 3)


def create_enemy_sprite(spirit_name: str, god_name: str,
                        size: int = 64) -> pygame.Surface:
    """Generate an enemy battle sprite based on spirit name and god."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    base_color = GOD_COLORS.get(god_name, (150, 150, 150))
    beast_key = spirit_name.lower().split()[0]  # first word
    # Map to beast type
    beast_map = {
        "snake": "snake", "turtle": "snake", "lizard": "lizard",
        "crocodile": "crocodile", "komodo": "komodo", "basilisk": "basilisk",
        "wyvern": "wyvern", "dragon": "dragon",
        "sparrow": "sparrow", "hawk": "hawk", "eagle": "eagle", "owl": "owl",
        "griffin": "griffin", "pteranodon": "pteranodon", "phoenix": "phoenix",
        "fish": "fish", "jellyfish": "jellyfish", "shark": "shark",
        "octopus": "octopus", "dolphin": "dolphin", "kraken": "kraken",
        "leviathan": "leviathan",
        "ant": "ant", "bee": "bee", "beetle": "beetle", "spider": "spider",
        "giant": "scorpion", "ancient": "dragonfly",
        "wolf": "wolf", "wild": "dog", "lion": "lion", "panther": "panther",
        "sabertooth": "sabertooth", "cerberus": "cerberus",
        "horse": "horse", "rhino": "rhino", "elephant": "elephant",
        "mammoth": "mammoth", "triceratops": "triceratops", "behemoth": "behemoth",
        "rat": "rat", "bat": "bat", "raccoon": "raccoon", "monkey": "monkey",
        "jackalope": "jackalope",
        "fox": "fox", "otter": "otter", "chimpanzee": "chimpanzee",
        "gorilla": "gorilla", "sphinx": "sphinx",
    }
    beast_type = beast_map.get(beast_key, "generic")
    _draw_beast(surf, base_color, size, size, beast_type)
    return surf


# ── UI sprites ─────────────────────────────────────────────────────────

def create_battle_background(width: int, height: int) -> pygame.Surface:
    """Generate a JRPG-style battle background (grassy field)."""
    surf = pygame.Surface((width, height))
    # Sky gradient
    for y in range(height // 2):
        t = y / (height // 2)
        r = int(80 + 100 * t)
        g = int(140 + 80 * t)
        b = int(220 - 40 * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (width, y))
    # Ground
    for y in range(height // 2, height):
        t = (y - height // 2) / (height // 2)
        r = int(60 + 40 * t)
        g = int(130 - 30 * t)
        b = int(50 + 20 * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (width, y))
    # Horizon detail
    pygame.draw.line(surf, (90, 150, 70), (0, height // 2), (width, height // 2), 2)
    # Distant mountains
    pts = [(0, height // 2)]
    for x in range(0, width + 40, 40):
        peak = height // 2 - 20 - int(15 * math.sin(x * 0.03))
        pts.append((x, peak))
    pts.append((width, height // 2))
    pygame.draw.polygon(surf, (70, 110, 60), pts)
    return surf
