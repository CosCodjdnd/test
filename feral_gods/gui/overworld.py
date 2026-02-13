"""Overworld exploration scene for the Feral Gods GUI.

The player walks around a tile-based map, encounters enemies, and can visit
shrines and portals.  Inspired by classic 2D JRPG overworlds.
"""

from __future__ import annotations

import random
from enum import Enum, auto

import pygame

from ..characters import Character, create_enemy
from ..gods import ALL_SPIRITS
from ..ceremony import SHRINE_CHALLENGES, Ceremony
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SIZE,
    BLACK, WHITE, GOLD, TEXT_COLOR, TEXT_DIM,
    PASSABLE_TILES, ENCOUNTER_RATE, GOD_COLORS, MESSAGE_HISTORY_LIMIT,
    TILE_GRASS, TILE_SHRINE,
)
from .maps import GameMap, get_all_maps
from .sprites import get_tile_sprite, create_player_overworld
from .ui import draw_text, draw_panel, draw_character_hud, draw_menu
from .battle_scene import BattleScene


class OverworldResult(Enum):
    CONTINUE = auto()
    QUIT_TO_MENU = auto()
    GAME_OVER = auto()


class OverworldScene:
    """Top-down tile-based exploration scene."""

    def __init__(self, screen: pygame.Surface, player: Character) -> None:
        self.screen = screen
        self.player = player
        self.clock = pygame.time.Clock()
        self.maps = get_all_maps()
        self.current_map_name = "village"
        self.current_map = self.maps[self.current_map_name]

        # Player tile position
        self.px = self.current_map.start_x
        self.py = self.current_map.start_y

        # Camera
        self.cam_x = 0
        self.cam_y = 0

        # Player sprite
        god_name = player.god.name.value if player.god else None
        self.player_sprite = create_player_overworld(god_name)

        self.step_count = 0
        self.battles_won = 0
        self.messages: list[str] = [f"Welcome to {self.current_map.name}!"]
        self.message_timer = 2.0
        self.show_pause_menu = False
        self.pause_index = 0

        # Shrine interaction
        self.shrine_active: str | None = None
        self.ceremony: Ceremony | None = None

    def run(self) -> OverworldResult:
        """Run the overworld until the player quits or game over."""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return OverworldResult.QUIT_TO_MENU
                if event.type == pygame.KEYDOWN:
                    result = self._handle_input(event.key)
                    if result is not None:
                        return result

            self._update(dt)
            self._draw()
            pygame.display.flip()

        return OverworldResult.QUIT_TO_MENU

    # ── input ─────────────────────────────────────────────────────

    def _handle_input(self, key: int) -> OverworldResult | None:
        if self.shrine_active:
            if key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE, pygame.K_ESCAPE):
                self.shrine_active = None
            return None

        if self.show_pause_menu:
            return self._handle_pause_input(key)

        if key == pygame.K_ESCAPE:
            self.show_pause_menu = True
            self.pause_index = 0
            return None

        # Movement
        dx, dy = 0, 0
        if key == pygame.K_UP or key == pygame.K_w:
            dy = -1
        elif key == pygame.K_DOWN or key == pygame.K_s:
            dy = 1
        elif key == pygame.K_LEFT or key == pygame.K_a:
            dx = -1
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            dx = 1

        if dx != 0 or dy != 0:
            self._try_move(dx, dy)

        return None

    def _handle_pause_input(self, key: int) -> OverworldResult | None:
        pause_options = ["Resume", "Character", "Abilities", "Rest", "Quit to Menu"]
        if key == pygame.K_UP:
            self.pause_index = (self.pause_index - 1) % len(pause_options)
        elif key == pygame.K_DOWN:
            self.pause_index = (self.pause_index + 1) % len(pause_options)
        elif key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
            choice = pause_options[self.pause_index]
            if choice == "Resume":
                self.show_pause_menu = False
            elif choice == "Character":
                self.show_pause_menu = False
                self._show_character_screen()
            elif choice == "Abilities":
                self.show_pause_menu = False
                self._show_abilities_screen()
            elif choice == "Rest":
                self.player.current_hp = self.player.max_hp
                self.player.current_energy = self.player.max_energy
                self.player.status_effects = []
                self.player.cooldowns = {}
                self._add_message("Fully rested and recovered!")
                self.show_pause_menu = False
            elif choice == "Quit to Menu":
                return OverworldResult.QUIT_TO_MENU
        elif key in (pygame.K_ESCAPE, pygame.K_x):
            self.show_pause_menu = False
        return None

    # ── movement & encounters ─────────────────────────────────────

    def _try_move(self, dx: int, dy: int) -> None:
        nx, ny = self.px + dx, self.py + dy
        if not self.current_map.is_passable(nx, ny):
            # Check if it's a shrine
            shrine_god = self.current_map.get_shrine(nx, ny)
            if shrine_god:
                self._interact_shrine(shrine_god)
            return

        self.px, self.py = nx, ny
        self.step_count += 1

        # Check portal
        portal = self.current_map.get_portal(nx, ny)
        if portal:
            self._change_map(portal.target_map, portal.target_x, portal.target_y)
            return

        # Check shrine on same tile
        shrine_god = self.current_map.get_shrine(nx, ny)
        if shrine_god:
            self._interact_shrine(shrine_god)
            return

        # Random encounter
        if self.current_map.encounter_zone and self.current_map.get_tile(nx, ny) == TILE_GRASS:
            if random.random() < ENCOUNTER_RATE:
                self._start_random_encounter()

    def _change_map(self, map_name: str, tx: int, ty: int) -> None:
        if map_name in self.maps:
            self.current_map_name = map_name
            self.current_map = self.maps[map_name]
            self.px, self.py = tx, ty
            self._add_message(f"Entered {self.current_map.name}")

    def _interact_shrine(self, god_name: str) -> None:
        self.shrine_active = god_name
        self._add_message(f"You stand before the Shrine of {god_name}.")

    def _start_random_encounter(self) -> None:
        # Generate enemy based on player level
        level = max(1, self.player.level + random.randint(-1, 1))
        enemy_names = [
            "Wild Beastkin", "Rogue Spiritbearer", "Feral Guardian",
            "Shadow Stalker", "Swarm Drone", "Pack Hunter",
            "Deep Lurker", "Sky Raider", "Stone Sentinel",
        ]
        name = random.choice(enemy_names)
        god_key = random.choice(list(ALL_SPIRITS.keys()))
        spirit = random.choice(ALL_SPIRITS[god_key])
        enemy = create_enemy(name, spirit, level)

        # Run battle
        battle = BattleScene(self.screen, self.player, enemy)
        result = battle.run()

        if result.winner == self.player:
            xp = enemy.level * 30 + 20
            msgs = self.player.gain_experience(xp)
            for m in msgs:
                self._add_message(m.strip())
            self.battles_won += 1
        else:
            self._add_message("Defeated... but the spirits revive you.")
            self.player.current_hp = self.player.max_hp // 2
            self.player.current_energy = self.player.max_energy // 2

    # ── sub-screens ───────────────────────────────────────────────

    def _show_character_screen(self) -> None:
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    waiting = False

            self.screen.fill(BLACK)
            draw_panel(self.screen, 40, 30, SCREEN_WIDTH - 80, SCREEN_HEIGHT - 60)

            p = self.player
            y = 50
            draw_text(self.screen, f"{p.name}", 60, y, GOLD, 24, shadow=True)
            y += 30
            if p.spirit:
                draw_text(self.screen, f"Spirit: {p.spirit.name} ({p.spirit.rarity.value})",
                          60, y, TEXT_COLOR, 16)
                y += 22
            if p.god:
                draw_text(self.screen, f"God: {p.god.name.value} — {p.god.title}",
                          60, y, GOD_COLORS.get(p.god.name.value, TEXT_COLOR), 16)
                y += 22
            draw_text(self.screen, f"Level: {p.level}  XP: {p.experience}/{p.level*100}",
                      60, y, TEXT_COLOR, 16)
            y += 22
            draw_text(self.screen, f"HP: {p.current_hp}/{p.max_hp}  "
                      f"Energy: {p.current_energy}/{p.max_energy}", 60, y, TEXT_COLOR, 16)
            y += 22
            draw_text(self.screen, f"ATK: {p.attack}  DEF: {p.defense}  "
                      f"SPD: {p.speed}  ACC: {p.accuracy}", 60, y, TEXT_COLOR, 16)
            y += 28
            if p.physical_traits:
                draw_text(self.screen, f"Traits: {', '.join(p.physical_traits)}",
                          60, y, TEXT_DIM, 14)
                y += 22
            draw_text(self.screen, f"Battles won: {self.battles_won}", 60, y, TEXT_DIM, 14)
            y += 30
            draw_text(self.screen, "Press any key to return", 60, y, TEXT_DIM, 13)

            pygame.display.flip()
            self.clock.tick(FPS)

    def _show_abilities_screen(self) -> None:
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    waiting = False

            self.screen.fill(BLACK)
            draw_panel(self.screen, 40, 30, SCREEN_WIDTH - 80, SCREEN_HEIGHT - 60)
            draw_text(self.screen, "ABILITIES", 60, 45, GOLD, 20, shadow=True)

            y = 80
            for a in self.player.abilities:
                type_tag = "[P]" if a.ability_type.value == "passive" else "[A]"
                label = f"{type_tag} {a.name}"
                draw_text(self.screen, label, 60, y, WHITE, 14)
                # Details
                parts = []
                if a.damage:
                    parts.append(f"DMG:{a.damage}")
                if a.healing:
                    parts.append(f"HEAL:{a.healing}")
                if a.defense_bonus:
                    parts.append(f"DEF+{a.defense_bonus}")
                if a.energy_cost:
                    parts.append(f"EN:{a.energy_cost}")
                if a.cooldown:
                    parts.append(f"CD:{a.cooldown}")
                draw_text(self.screen, "  ".join(parts), 260, y, TEXT_DIM, 12)
                draw_text(self.screen, a.description, 60, y + 16, TEXT_DIM, 11)
                y += 36

            draw_text(self.screen, "Press any key to return", 60,
                      SCREEN_HEIGHT - 70, TEXT_DIM, 13)
            pygame.display.flip()
            self.clock.tick(FPS)

    # ── helpers ───────────────────────────────────────────────────

    def _add_message(self, msg: str) -> None:
        self.messages.append(msg)
        self.message_timer = 2.0
        if len(self.messages) > MESSAGE_HISTORY_LIMIT:
            self.messages = self.messages[-MESSAGE_HISTORY_LIMIT:]

    # ── update ────────────────────────────────────────────────────

    def _update(self, dt: float) -> None:
        self.message_timer = max(0, self.message_timer - dt)
        # Camera follows player
        target_cam_x = self.px * TILE_SIZE - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        target_cam_y = self.py * TILE_SIZE - SCREEN_HEIGHT // 2 + TILE_SIZE // 2
        # Clamp camera
        max_cam_x = self.current_map.width * TILE_SIZE - SCREEN_WIDTH
        max_cam_y = self.current_map.height * TILE_SIZE - SCREEN_HEIGHT
        target_cam_x = max(0, min(target_cam_x, max_cam_x))
        target_cam_y = max(0, min(target_cam_y, max_cam_y))
        # Smooth camera
        self.cam_x += (target_cam_x - self.cam_x) * min(1.0, dt * 8)
        self.cam_y += (target_cam_y - self.cam_y) * min(1.0, dt * 8)

    # ── draw ──────────────────────────────────────────────────────

    def _draw(self) -> None:
        self.screen.fill(BLACK)

        cam_x = int(self.cam_x)
        cam_y = int(self.cam_y)

        # Determine visible tile range
        start_tx = max(0, cam_x // TILE_SIZE)
        start_ty = max(0, cam_y // TILE_SIZE)
        end_tx = min(self.current_map.width, start_tx + SCREEN_WIDTH // TILE_SIZE + 2)
        end_ty = min(self.current_map.height, start_ty + SCREEN_HEIGHT // TILE_SIZE + 2)

        # Draw tiles
        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                tile = self.current_map.get_tile(tx, ty)
                sprite = get_tile_sprite(tile)
                sx = tx * TILE_SIZE - cam_x
                sy = ty * TILE_SIZE - cam_y
                self.screen.blit(sprite, (sx, sy))

        # Draw shrines with glow
        for sx, sy, god_name in self.current_map.shrines:
            screen_x = sx * TILE_SIZE - cam_x
            screen_y = sy * TILE_SIZE - cam_y
            color = GOD_COLORS.get(god_name, GOLD)
            glow = pygame.Surface((TILE_SIZE + 8, TILE_SIZE + 8), pygame.SRCALPHA)
            glow.fill((*color, 40))
            self.screen.blit(glow, (screen_x - 4, screen_y - 4))

        # Draw player
        player_sx = self.px * TILE_SIZE - cam_x
        player_sy = self.py * TILE_SIZE - cam_y
        self.screen.blit(self.player_sprite, (player_sx, player_sy))

        # HUD
        draw_character_hud(self.screen, self.player, 10, 10)

        # Map name
        draw_text(self.screen, self.current_map.name,
                  SCREEN_WIDTH - 10, 10, TEXT_DIM, 13)

        # Messages
        if self.message_timer > 0 and self.messages:
            last_msg = self.messages[-1]
            draw_panel(self.screen, 10, SCREEN_HEIGHT - 50, SCREEN_WIDTH - 20, 40)
            draw_text(self.screen, last_msg, 20, SCREEN_HEIGHT - 42, TEXT_COLOR, 14)

        # Shrine popup
        if self.shrine_active:
            self._draw_shrine_popup()

        # Pause menu
        if self.show_pause_menu:
            self._draw_pause_menu()

    def _draw_shrine_popup(self) -> None:
        god_name = self.shrine_active
        color = GOD_COLORS.get(god_name, GOLD)
        pw, ph = 500, 200
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2
        draw_panel(self.screen, px, py, pw, ph)
        draw_text(self.screen, f"⛩ Shrine of {god_name}", px + 20, py + 16, color, 20, shadow=True)
        if god_name in SHRINE_CHALLENGES:
            shrine = SHRINE_CHALLENGES[god_name]
            draw_text(self.screen, shrine.name, px + 20, py + 46, WHITE, 14)
            # Word-wrap description
            desc = shrine.description
            words = desc.split()
            line = ""
            line_y = py + 68
            for w in words:
                test = line + " " + w if line else w
                if len(test) > 60:
                    draw_text(self.screen, line, px + 20, line_y, TEXT_DIM, 12)
                    line_y += 16
                    line = w
                else:
                    line = test
            if line:
                draw_text(self.screen, line, px + 20, line_y, TEXT_DIM, 12)
        draw_text(self.screen, "Press any key to continue", px + 20, py + ph - 30, TEXT_DIM, 12)

    def _draw_pause_menu(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        options = ["Resume", "Character", "Abilities", "Rest", "Quit to Menu"]
        menu_w = 220
        menu_x = (SCREEN_WIDTH - menu_w) // 2
        menu_y = SCREEN_HEIGHT // 2 - len(options) * 16
        draw_text(self.screen, "MENU", SCREEN_WIDTH // 2, menu_y - 30, GOLD, 22,
                  center=True, shadow=True)
        draw_menu(self.screen, options, self.pause_index,
                  menu_x, menu_y, menu_w, item_h=32)
