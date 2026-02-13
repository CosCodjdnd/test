"""Main entry point for the Feral Gods 2D GUI.

Launches a Pygame window with a visual, JRPG-inspired interface:
  • Main menu with title screen
  • Character creation with Ceremony
  • Overworld exploration (walk around, encounter enemies)
  • Visual turn-based combat (side-view, menus, HP bars)
"""

from __future__ import annotations

import random

import pygame

from ..characters import create_character, create_enemy
from ..gods import ALL_SPIRITS
from ..combat import Combat
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK
from .menu_scenes import run_main_menu, run_character_creation, run_lore_screen
from .overworld import OverworldScene, OverworldResult
from .battle_scene import BattleScene


def run_quick_battle(screen: pygame.Surface) -> None:
    """Generate two random characters and run a visual battle."""
    god1 = random.choice(list(ALL_SPIRITS.keys()))
    spirit1 = random.choice(ALL_SPIRITS[god1])
    god2 = random.choice(list(ALL_SPIRITS.keys()))
    spirit2 = random.choice(ALL_SPIRITS[god2])

    player = create_character("Champion", spirit=spirit1)
    enemy = create_enemy("Challenger", spirit2, level=random.randint(1, 3))

    battle = BattleScene(screen, player, enemy)
    battle.run()


def main_gui() -> None:
    """Main GUI entry point."""
    pygame.init()
    pygame.display.set_caption("Feral Gods — A Turn-Based RPG")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    running = True
    while running:
        result = run_main_menu(screen)

        if result.action == "quit":
            running = False

        elif result.action == "new_game":
            player = run_character_creation(screen)
            overworld = OverworldScene(screen, player)
            ow_result = overworld.run()
            if ow_result == OverworldResult.QUIT_TO_MENU:
                continue

        elif result.action == "quick_battle":
            run_quick_battle(screen)

        elif result.action == "lore":
            run_lore_screen(screen)

    pygame.quit()
