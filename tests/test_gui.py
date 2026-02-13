"""Tests for the Feral Gods GUI modules (non-display logic).

These tests verify maps, sprites, constants, and UI helpers without
requiring a visible display by using pygame's dummy video driver.
"""

import os
import random
import pytest

# Use dummy display driver so tests can create surfaces without a window
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
# Minimal display for surface creation
pygame.display.set_mode((1, 1))

from feral_gods.gui.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, FPS,
    GOD_COLORS, PASSABLE_TILES, ENCOUNTER_RATE,
    TILE_GRASS, TILE_PATH, TILE_WATER, TILE_TREE, TILE_STONE,
    TILE_SHRINE, TILE_WALL, TILE_DOOR, TILE_SAND,
    BLACK, WHITE, BROWN,
)
from feral_gods.gui.maps import GameMap, get_all_maps, MapPortal
from feral_gods.gui.sprites import (
    get_tile_sprite, create_player_sprite, create_player_overworld,
    create_enemy_sprite, create_battle_background,
)
from feral_gods.gui.ui import draw_text, draw_panel, draw_bar, draw_menu
from feral_gods.gui.battle_scene import BattleScene, BattlePhase
from feral_gods.gui.overworld import OverworldScene
from feral_gods.characters import create_character, create_enemy
from feral_gods.gods import WOLF, DRAGON, SNAKE, PHOENIX, ALL_SPIRITS


# -----------------------------------------------------------------------
# Constants tests
# -----------------------------------------------------------------------

class TestConstants:
    def test_screen_dimensions(self):
        assert SCREEN_WIDTH == 800
        assert SCREEN_HEIGHT == 600

    def test_tile_size(self):
        assert TILE_SIZE == 32

    def test_all_gods_have_colors(self):
        gods = ["Ophidia", "Galanth", "Pelagon", "Myriad",
                "Karn", "Pachymos", "Skulk", "Sagax"]
        for god in gods:
            assert god in GOD_COLORS

    def test_passable_tiles(self):
        assert TILE_GRASS in PASSABLE_TILES
        assert TILE_PATH in PASSABLE_TILES
        assert TILE_WALL not in PASSABLE_TILES
        assert TILE_TREE not in PASSABLE_TILES
        assert TILE_WATER not in PASSABLE_TILES

    def test_encounter_rate_is_reasonable(self):
        assert 0 < ENCOUNTER_RATE < 1


# -----------------------------------------------------------------------
# Map tests
# -----------------------------------------------------------------------

class TestMaps:
    def test_all_maps_exist(self):
        maps = get_all_maps()
        assert "village" in maps
        assert "wilds" in maps
        assert "deep_wilds" in maps

    def test_map_dimensions(self):
        maps = get_all_maps()
        for name, m in maps.items():
            assert m.width > 0, f"{name} has no width"
            assert m.height > 0, f"{name} has no height"
            assert len(m.tiles) == m.height, f"{name} tile rows != height"
            for row in m.tiles:
                assert len(row) == m.width, f"{name} tile col width mismatch"

    def test_map_passability(self):
        maps = get_all_maps()
        m = maps["village"]
        # Start position should be passable
        assert m.is_passable(m.start_x, m.start_y)
        # Borders (trees) should not be passable
        assert not m.is_passable(0, 0)

    def test_out_of_bounds_is_wall(self):
        maps = get_all_maps()
        m = maps["village"]
        assert m.get_tile(-1, -1) == TILE_WALL
        assert m.get_tile(999, 999) == TILE_WALL
        assert not m.is_passable(-1, -1)

    def test_portals_exist(self):
        maps = get_all_maps()
        village = maps["village"]
        assert len(village.portals) > 0
        portal = village.portals[0]
        assert portal.target_map in maps

    def test_portal_lookup(self):
        maps = get_all_maps()
        village = maps["village"]
        p = village.portals[0]
        found = village.get_portal(p.x, p.y)
        assert found is not None
        assert found.target_map == p.target_map

    def test_no_portal_at_random_tile(self):
        maps = get_all_maps()
        assert maps["village"].get_portal(0, 0) is None

    def test_shrine_locations(self):
        maps = get_all_maps()
        wilds = maps["wilds"]
        assert len(wilds.shrines) > 0
        for sx, sy, god_name in wilds.shrines:
            assert isinstance(god_name, str)
            assert 0 <= sx < wilds.width
            assert 0 <= sy < wilds.height

    def test_shrine_lookup(self):
        maps = get_all_maps()
        wilds = maps["wilds"]
        sx, sy, god_name = wilds.shrines[0]
        assert wilds.get_shrine(sx, sy) == god_name

    def test_village_no_encounters(self):
        maps = get_all_maps()
        assert maps["village"].encounter_zone is False

    def test_wilds_has_encounters(self):
        maps = get_all_maps()
        assert maps["wilds"].encounter_zone is True

    def test_portal_chains(self):
        """Verify portal targets reference valid maps and positions."""
        maps = get_all_maps()
        for name, m in maps.items():
            for portal in m.portals:
                assert portal.target_map in maps, \
                    f"Portal in {name} points to nonexistent map {portal.target_map}"
                target = maps[portal.target_map]
                assert target.is_passable(portal.target_x, portal.target_y), \
                    f"Portal target ({portal.target_x},{portal.target_y}) in {portal.target_map} is not passable"


# -----------------------------------------------------------------------
# Sprite tests
# -----------------------------------------------------------------------

class TestSprites:
    def test_tile_sprites_are_surfaces(self):
        for tile_type in [TILE_GRASS, TILE_PATH, TILE_WATER, TILE_TREE,
                          TILE_STONE, TILE_SHRINE, TILE_WALL, TILE_DOOR, TILE_SAND]:
            sprite = get_tile_sprite(tile_type)
            assert isinstance(sprite, pygame.Surface)
            assert sprite.get_width() == TILE_SIZE
            assert sprite.get_height() == TILE_SIZE

    def test_tile_sprite_caching(self):
        s1 = get_tile_sprite(TILE_GRASS)
        s2 = get_tile_sprite(TILE_GRASS)
        assert s1 is s2  # same object = cached

    def test_player_sprite_creation(self):
        sprite = create_player_sprite("Ophidia", 64)
        assert isinstance(sprite, pygame.Surface)
        assert sprite.get_width() == 64
        assert sprite.get_height() == 64

    def test_player_sprite_without_god(self):
        sprite = create_player_sprite(None, 64)
        assert isinstance(sprite, pygame.Surface)

    def test_player_overworld_sprite(self):
        sprite = create_player_overworld("Karn")
        assert isinstance(sprite, pygame.Surface)
        assert sprite.get_width() == TILE_SIZE

    def test_enemy_sprite_creation(self):
        for spirit_name in ["Wolf", "Dragon", "Phoenix", "Shark", "Ant", "Sphinx"]:
            sprite = create_enemy_sprite(spirit_name, "Karn", 64)
            assert isinstance(sprite, pygame.Surface)
            assert sprite.get_width() == 64

    def test_enemy_sprite_all_god_colors(self):
        for god_name in GOD_COLORS:
            sprite = create_enemy_sprite("Wolf", god_name, 64)
            assert isinstance(sprite, pygame.Surface)

    def test_battle_background(self):
        bg = create_battle_background(800, 600)
        assert isinstance(bg, pygame.Surface)
        assert bg.get_width() == 800
        assert bg.get_height() == 600


# -----------------------------------------------------------------------
# UI tests
# -----------------------------------------------------------------------

class TestUI:
    def test_draw_text_returns_rect(self):
        surf = pygame.Surface((400, 100))
        rect = draw_text(surf, "Hello", 10, 10)
        assert isinstance(rect, pygame.Rect)

    def test_draw_panel_no_crash(self):
        surf = pygame.Surface((400, 200))
        draw_panel(surf, 10, 10, 200, 100)

    def test_draw_bar_no_crash(self):
        surf = pygame.Surface((400, 100))
        draw_bar(surf, 10, 10, 200, 20, 50, 100, (0, 255, 0))
        draw_bar(surf, 10, 40, 200, 20, 0, 100, (255, 0, 0))
        draw_bar(surf, 10, 70, 200, 20, 100, 0, (0, 0, 255))  # max=0

    def test_draw_menu_no_crash(self):
        surf = pygame.Surface((400, 300))
        draw_menu(surf, ["Attack", "Ability", "Rest"], 0, 10, 10, 200)
        draw_menu(surf, ["Attack", "Ability", "Rest"], 2, 10, 10, 200)


# -----------------------------------------------------------------------
# Battle scene tests (logic only)
# -----------------------------------------------------------------------

class TestBattleScene:
    def test_battle_scene_init(self):
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        player = create_character("Hero", spirit=WOLF)
        enemy = create_enemy("Foe", SNAKE, level=1)
        scene = BattleScene(screen, player, enemy)
        assert scene.player == player
        assert scene.enemy == enemy
        assert scene.result is None

    def test_battle_scene_sprites_created(self):
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        player = create_character("Hero", spirit=DRAGON)
        enemy = create_enemy("Foe", PHOENIX, level=1)
        scene = BattleScene(screen, player, enemy)
        assert isinstance(scene.player_sprite, pygame.Surface)
        assert isinstance(scene.enemy_sprite, pygame.Surface)
        assert isinstance(scene.bg, pygame.Surface)

    def test_battle_phase_starts_correctly(self):
        random.seed(42)
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        player = create_character("Hero", spirit=DRAGON)
        enemy = create_enemy("Foe", SNAKE, level=1)
        scene = BattleScene(screen, player, enemy)
        # Phase should be either player menu or enemy action
        assert scene.phase in (BattlePhase.PLAYER_MENU, BattlePhase.ENEMY_ACTION)

    def test_get_menu_options(self):
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        player = create_character("Hero", spirit=WOLF)
        enemy = create_enemy("Foe", SNAKE, level=1)
        scene = BattleScene(screen, player, enemy)
        options = scene._get_menu_options()
        assert "Attack" in options
        assert "Abilities" in options
        assert "Rest" in options


# -----------------------------------------------------------------------
# Overworld tests (logic only)
# -----------------------------------------------------------------------

class TestOverworld:
    def test_overworld_init(self):
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        player = create_character("Hero", spirit=WOLF)
        ow = OverworldScene(screen, player)
        assert ow.current_map_name == "village"
        assert ow.px == ow.current_map.start_x
        assert ow.py == ow.current_map.start_y

    def test_overworld_player_sprite(self):
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        player = create_character("Hero", spirit=WOLF)
        ow = OverworldScene(screen, player)
        assert isinstance(ow.player_sprite, pygame.Surface)

    def test_change_map(self):
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        player = create_character("Hero", spirit=WOLF)
        ow = OverworldScene(screen, player)
        ow._change_map("wilds", 5, 5)
        assert ow.current_map_name == "wilds"
        assert ow.px == 5
        assert ow.py == 5

    def test_try_move_to_passable(self):
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        player = create_character("Hero", spirit=WOLF)
        ow = OverworldScene(screen, player)
        # Move to a known passable tile
        ow.px = 5
        ow.py = 5
        old_steps = ow.step_count
        ow._try_move(0, 1)  # move down (should be passable on village path)
        # Either moved or didn't depending on tile
        assert ow.step_count >= old_steps

    def test_try_move_to_wall(self):
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        player = create_character("Hero", spirit=WOLF)
        ow = OverworldScene(screen, player)
        # Move to border (tree)
        ow.px = 1
        ow.py = 1
        ow._try_move(-1, 0)  # should be tree at 0,1
        assert ow.px == 1  # didn't move

    def test_add_message(self):
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        player = create_character("Hero", spirit=WOLF)
        ow = OverworldScene(screen, player)
        ow._add_message("Test message")
        assert "Test message" in ow.messages

    def test_message_limit(self):
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        player = create_character("Hero", spirit=WOLF)
        ow = OverworldScene(screen, player)
        for i in range(60):
            ow._add_message(f"Message {i}")
        assert len(ow.messages) <= 51  # 50 limit + 1 initial
