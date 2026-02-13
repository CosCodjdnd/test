"""Visual turn-based battle scene for the Feral Gods GUI.

Inspired by classic side-view JRPG combat (Final Fantasy, Dragon Quest):
player party on the right, enemies on the left, command menu at the bottom.
"""

from __future__ import annotations

import random
import time
from enum import Enum, auto

import pygame

from ..enums import AbilityType, StatusEffect
from ..characters import Character
from ..combat import Combat, CombatResult
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, GOLD, RED, GREEN,
    PANEL_BG, TEXT_COLOR, TEXT_DIM, ATTACK_ANIM_TIME, DAMAGE_FLASH_TIME,
    MESSAGE_DISPLAY_TIME, GOD_COLORS,
)
from .sprites import create_player_sprite, create_enemy_sprite, create_battle_background
from .ui import (
    draw_text, draw_panel, draw_menu, draw_hp_bar, draw_energy_bar,
    draw_character_hud, draw_message_log,
)


class BattlePhase(Enum):
    PLAYER_MENU = auto()
    PLAYER_ABILITY_SELECT = auto()
    PLAYER_ACTION = auto()
    ENEMY_ACTION = auto()
    ANIMATION = auto()
    MESSAGE = auto()
    VICTORY = auto()
    DEFEAT = auto()


class BattleScene:
    """Full visual battle scene manager."""

    def __init__(self, screen: pygame.Surface, player: Character,
                 enemy: Character) -> None:
        self.screen = screen
        self.player = player
        self.enemy = enemy
        self.combat = Combat(player, enemy)
        self.combat._determine_initiative()

        self.phase = BattlePhase.PLAYER_MENU
        if not self.combat.is_player_turn:
            self.phase = BattlePhase.ENEMY_ACTION

        self.menu_index = 0
        self.ability_index = 0
        self.messages: list[str] = [f"A wild {enemy.name} appears!"]
        self.pending_messages: list[str] = []
        self.message_timer = 0.0
        self.anim_timer = 0.0
        self.result: CombatResult | None = None

        # Sprites
        god_name = player.god.name.value if player.god else None
        self.player_sprite = create_player_sprite(god_name, 80)
        enemy_spirit = enemy.spirit.name if enemy.spirit else "Unknown"
        enemy_god = enemy.god.name.value if enemy.god else "Unknown"
        self.enemy_sprite = create_enemy_sprite(enemy_spirit, enemy_god, 80)

        self.bg = create_battle_background(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Positions
        self.player_pos = [SCREEN_WIDTH - 160, SCREEN_HEIGHT // 2 - 60]
        self.enemy_pos = [80, SCREEN_HEIGHT // 2 - 80]
        self.player_base_x = self.player_pos[0]
        self.enemy_base_x = self.enemy_pos[0]

        # Flash
        self.player_flash = 0.0
        self.enemy_flash = 0.0

        self.clock = pygame.time.Clock()

    # ── main loop ─────────────────────────────────────────────────

    def run(self) -> CombatResult:
        """Run the battle scene until completion. Returns CombatResult."""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    self._handle_input(event.key)

            self._update(dt)
            self._draw()
            pygame.display.flip()

            if self.result is not None and self.phase in (BattlePhase.VICTORY, BattlePhase.DEFEAT):
                # Wait for keypress to dismiss
                if self._wait_for_key(2.0):
                    running = False

        return self.result  # type: ignore[return-value]

    def _wait_for_key(self, timeout: float) -> bool:
        """Wait for keypress or timeout. Returns True if should exit."""
        start = time.time()
        while time.time() - start < timeout:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    return True
            self.clock.tick(FPS)
        return True

    # ── input ─────────────────────────────────────────────────────

    def _handle_input(self, key: int) -> None:
        if self.phase == BattlePhase.PLAYER_MENU:
            options = self._get_menu_options()
            if key == pygame.K_UP:
                self.menu_index = (self.menu_index - 1) % len(options)
            elif key == pygame.K_DOWN:
                self.menu_index = (self.menu_index + 1) % len(options)
            elif key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                self._select_menu_option(options[self.menu_index])

        elif self.phase == BattlePhase.PLAYER_ABILITY_SELECT:
            abilities = self.player.get_active_abilities()
            if not abilities:
                self.phase = BattlePhase.PLAYER_MENU
                return
            if key == pygame.K_UP:
                self.ability_index = (self.ability_index - 1) % len(abilities)
            elif key == pygame.K_DOWN:
                self.ability_index = (self.ability_index + 1) % len(abilities)
            elif key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                ability = abilities[self.ability_index]
                real_idx = self.player.abilities.index(ability)
                msgs = self.combat.execute_turn("ability", real_idx)
                self._queue_messages(msgs)
                self.phase = BattlePhase.ANIMATION
                self.anim_timer = 0.4
                self.enemy_flash = 0.3
            elif key in (pygame.K_ESCAPE, pygame.K_x, pygame.K_BACKSPACE):
                self.phase = BattlePhase.PLAYER_MENU

        elif self.phase in (BattlePhase.VICTORY, BattlePhase.DEFEAT):
            pass  # handled by _wait_for_key

    def _get_menu_options(self) -> list[str]:
        return ["Attack", "Abilities", "Rest"]

    def _select_menu_option(self, option: str) -> None:
        if option == "Attack":
            msgs = self.combat.execute_turn("attack")
            self._queue_messages(msgs)
            self.phase = BattlePhase.ANIMATION
            self.anim_timer = 0.4
            self.enemy_flash = 0.3
        elif option == "Abilities":
            abilities = self.player.get_active_abilities()
            if abilities:
                self.ability_index = 0
                self.phase = BattlePhase.PLAYER_ABILITY_SELECT
            else:
                self.messages.append("No abilities available!")
        elif option == "Rest":
            msgs = self.combat.execute_turn("rest")
            self._queue_messages(msgs)
            self.phase = BattlePhase.ANIMATION
            self.anim_timer = 0.3

    def _queue_messages(self, msgs: list[str]) -> None:
        cleaned = [m.strip() for m in msgs if m.strip()]
        self.pending_messages.extend(cleaned)

    # ── update ────────────────────────────────────────────────────

    def _update(self, dt: float) -> None:
        # Flash timers
        self.player_flash = max(0, self.player_flash - dt)
        self.enemy_flash = max(0, self.enemy_flash - dt)

        if self.phase == BattlePhase.ANIMATION:
            self.anim_timer -= dt
            if self.anim_timer <= 0:
                self._process_pending_messages()

        elif self.phase == BattlePhase.MESSAGE:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self._process_pending_messages()

        elif self.phase == BattlePhase.ENEMY_ACTION:
            # Small delay before enemy acts
            self.anim_timer -= dt
            if self.anim_timer <= 0:
                action, idx = self.combat._ai_choose_action(self.enemy, self.player)
                msgs = self.combat.execute_turn(action, idx)
                self._queue_messages(msgs)
                self.phase = BattlePhase.ANIMATION
                self.anim_timer = 0.4
                self.player_flash = 0.3

    def _process_pending_messages(self) -> None:
        if self.pending_messages:
            msg = self.pending_messages.pop(0)
            self.messages.append(msg)
            self.message_timer = 0.8
            self.phase = BattlePhase.MESSAGE
        else:
            self._check_battle_end()

    def _check_battle_end(self) -> None:
        if not self.enemy.is_alive:
            self.messages.append(f"★ {self.player.name} wins! ★")
            self.result = CombatResult(self.player, self.enemy, self.messages)
            self.phase = BattlePhase.VICTORY
        elif not self.player.is_alive:
            self.messages.append(f"✗ {self.player.name} has been defeated... ✗")
            self.result = CombatResult(self.enemy, self.player, self.messages)
            self.phase = BattlePhase.DEFEAT
        elif self.combat.is_player_turn:
            self.phase = BattlePhase.PLAYER_MENU
            self.menu_index = 0
        else:
            self.phase = BattlePhase.ENEMY_ACTION
            self.anim_timer = 0.5

    # ── draw ──────────────────────────────────────────────────────

    def _draw(self) -> None:
        self.screen.blit(self.bg, (0, 0))

        # Draw enemy sprite
        ex, ey = self.enemy_pos
        if self.enemy_flash > 0 and int(self.enemy_flash * 20) % 2 == 0:
            flash_surf = self.enemy_sprite.copy()
            flash_surf.fill((255, 80, 80, 120), special_flags=pygame.BLEND_RGBA_ADD)
            self.screen.blit(flash_surf, (ex, ey))
        else:
            self.screen.blit(self.enemy_sprite, (ex, ey))

        # Draw player sprite
        px, py = self.player_pos
        if self.player_flash > 0 and int(self.player_flash * 20) % 2 == 0:
            flash_surf = self.player_sprite.copy()
            flash_surf.fill((255, 80, 80, 120), special_flags=pygame.BLEND_RGBA_ADD)
            self.screen.blit(flash_surf, (px, py))
        else:
            self.screen.blit(self.player_sprite, (px, py))

        # HUD - Player
        draw_character_hud(self.screen, self.player, SCREEN_WIDTH - 240, 10)
        # HUD - Enemy
        draw_character_hud(self.screen, self.enemy, 10, 10)

        # Status effects display
        self._draw_status_effects(self.player, SCREEN_WIDTH - 240, 85)
        self._draw_status_effects(self.enemy, 10, 85)

        # Bottom panel: messages + menu
        panel_y = SCREEN_HEIGHT - 180
        draw_panel(self.screen, 0, panel_y, SCREEN_WIDTH, 180)

        # Message log
        draw_message_log(self.screen, self.messages,
                         10, panel_y + 4, SCREEN_WIDTH // 2 - 20, 170, max_lines=8)

        # Command menu (right side)
        menu_x = SCREEN_WIDTH // 2 + 20
        menu_y = panel_y + 12

        if self.phase == BattlePhase.PLAYER_MENU:
            draw_text(self.screen, "COMMAND", menu_x, menu_y - 2, GOLD, 14, shadow=True)
            options = self._get_menu_options()
            draw_menu(self.screen, options, self.menu_index,
                      menu_x, menu_y + 18, 200, item_h=32)

        elif self.phase == BattlePhase.PLAYER_ABILITY_SELECT:
            draw_text(self.screen, "ABILITIES", menu_x, menu_y - 2, GOLD, 14, shadow=True)
            abilities = self.player.get_active_abilities()
            labels = []
            for a in abilities:
                parts = [a.name]
                if a.damage:
                    parts.append(f"DMG:{a.damage}")
                if a.healing:
                    parts.append(f"HEAL:{a.healing}")
                parts.append(f"EN:{a.energy_cost}")
                labels.append("  ".join(parts))
            draw_menu(self.screen, labels, self.ability_index,
                      menu_x, menu_y + 18, 360, item_h=26)

        elif self.phase in (BattlePhase.VICTORY, BattlePhase.DEFEAT):
            msg = "VICTORY!" if self.phase == BattlePhase.VICTORY else "DEFEAT..."
            color = GOLD if self.phase == BattlePhase.VICTORY else RED
            draw_text(self.screen, msg, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40,
                      color, 32, center=True, shadow=True)
            draw_text(self.screen, "Press any key to continue",
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10,
                      TEXT_DIM, 16, center=True)

        else:
            draw_text(self.screen, "...", menu_x + 20, menu_y + 20, TEXT_DIM, 14)

    def _draw_status_effects(self, char: Character, x: int, y: int) -> None:
        if not char.status_effects:
            return
        for i, s in enumerate(char.status_effects):
            color = {
                StatusEffect.POISONED: (100, 200, 50),
                StatusEffect.BURNING: (255, 120, 30),
                StatusEffect.FROZEN: (100, 200, 255),
                StatusEffect.STUNNED: (200, 200, 50),
                StatusEffect.BLINDED: (150, 150, 150),
                StatusEffect.BERSERKER: (255, 50, 50),
                StatusEffect.SHIELDED: (100, 150, 255),
                StatusEffect.REGENERATING: (50, 255, 100),
                StatusEffect.INTIMIDATED: (180, 100, 50),
                StatusEffect.HIDDEN: (80, 80, 120),
            }.get(s.effect, TEXT_DIM)
            draw_text(self.screen, f"{s.effect.value}({s.remaining_turns})",
                      x + i * 80, y, color, 11)
