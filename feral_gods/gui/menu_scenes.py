"""Main menu and character creation screens for the Feral Gods GUI."""

from __future__ import annotations

import random
import math

import pygame

from ..characters import Character, create_character
from ..gods import ALL_GODS, ALL_SPIRITS
from ..ceremony import Ceremony
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    BLACK, WHITE, GOLD, TEXT_COLOR, TEXT_DIM,
    GOD_COLORS, PANEL_BG,
)
from .ui import draw_text, draw_panel, draw_menu
from .sprites import create_player_sprite


class MenuResult:
    """What the main menu decided."""
    def __init__(self, action: str, player: Character | None = None) -> None:
        self.action = action      # "new_game", "quick_battle", "lore", "quit"
        self.player = player


def run_main_menu(screen: pygame.Surface) -> MenuResult:
    """Display the main menu and return the player's choice."""
    clock = pygame.time.Clock()
    selected = 0
    options = ["New Game", "Quick Battle", "Lore", "Quit"]
    time_acc = 0.0

    while True:
        dt = clock.tick(FPS) / 1000.0
        time_acc += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return MenuResult("quit")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                    choice = options[selected].lower().replace(" ", "_")
                    return MenuResult(choice)

        # Draw
        screen.fill(BLACK)

        # Animated background
        for i in range(50):
            x = int(SCREEN_WIDTH / 2 + math.cos(time_acc * 0.3 + i * 0.7) * 300)
            y = int(SCREEN_HEIGHT / 2 + math.sin(time_acc * 0.2 + i * 0.5) * 200)
            r = int(2 + math.sin(time_acc + i) * 1.5)
            alpha = int(40 + 20 * math.sin(time_acc * 0.5 + i))
            color = list(GOD_COLORS.values())[i % len(GOD_COLORS)]
            dot = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot, (*color, alpha), (r, r), r)
            screen.blit(dot, (x - r, y - r))

        # Title
        draw_text(screen, "FERAL GODS", SCREEN_WIDTH // 2, 120,
                  GOLD, 48, center=True, shadow=True)
        draw_text(screen, "A Turn-Based RPG", SCREEN_WIDTH // 2, 175,
                  TEXT_DIM, 18, center=True)

        # Subtitle
        draw_text(screen, "In a world where gods grant spirit companions...",
                  SCREEN_WIDTH // 2, 210, TEXT_DIM, 13, center=True)

        # Menu
        menu_x = SCREEN_WIDTH // 2 - 100
        menu_y = 280
        draw_menu(screen, options, selected, menu_x, menu_y, 200, item_h=36)

        # Footer
        draw_text(screen, "Arrow Keys: Navigate    Enter/Z: Select",
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, TEXT_DIM, 12, center=True)

        pygame.display.flip()


def run_character_creation(screen: pygame.Surface) -> Character:
    """Interactive character creation with visual UI."""
    clock = pygame.time.Clock()
    name = ""
    phase = "name"  # "name" -> "mark" -> "ceremony" -> "done"
    char: Character | None = None
    has_mark = False
    mark_revealed = False
    ceremony_log: list[str] = []
    spirit_received = False
    log_scroll = 0

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if phase == "name":
                    if event.key == pygame.K_RETURN:
                        if not name:
                            name = "Elodie"
                        char = create_character(name)
                        phase = "mark"
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        if event.unicode.isprintable() and len(name) < 20:
                            name += event.unicode

                elif phase == "mark":
                    if event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                        if not mark_revealed:
                            has_mark = random.randint(1, 50) == 1
                            char.has_diviners_mark = has_mark
                            mark_revealed = True
                        else:
                            phase = "ceremony"
                            ceremony = Ceremony(season=random.choice(["Spring", "Autumn"]))
                            spirit = ceremony.run_auto_ceremony(char)
                            ceremony_log = [line.strip() for line in ceremony.log if line.strip()]
                            if spirit:
                                spirit_received = True
                            else:
                                # Give default spirit
                                god_name = random.choice(list(ALL_SPIRITS.keys()))
                                s = random.choice(ALL_SPIRITS[god_name])
                                char.receive_spirit(s)
                                ceremony_log.append(f"A mysterious force grants you a {s.name}!")
                                spirit_received = True

                elif phase == "ceremony":
                    if event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                        if spirit_received:
                            return char
                    elif event.key == pygame.K_UP:
                        log_scroll = max(0, log_scroll - 1)
                    elif event.key == pygame.K_DOWN:
                        log_scroll = min(max(0, len(ceremony_log) - 15), log_scroll + 1)

        # Draw
        screen.fill(BLACK)

        if phase == "name":
            draw_panel(screen, 100, 100, SCREEN_WIDTH - 200, 300)
            draw_text(screen, "CHARACTER CREATION", SCREEN_WIDTH // 2, 120,
                      GOLD, 24, center=True, shadow=True)
            draw_text(screen, "Welcome to the world of Feral Gods.",
                      SCREEN_WIDTH // 2, 165, TEXT_DIM, 14, center=True)
            draw_text(screen, "You are about to undergo the sacred Ceremony.",
                      SCREEN_WIDTH // 2, 185, TEXT_DIM, 14, center=True)

            draw_text(screen, "Enter your name:", SCREEN_WIDTH // 2, 240,
                      TEXT_COLOR, 16, center=True)
            # Name input box
            box_w = 250
            box_x = SCREEN_WIDTH // 2 - box_w // 2
            pygame.draw.rect(screen, (40, 40, 60), (box_x, 265, box_w, 32))
            pygame.draw.rect(screen, GOLD, (box_x, 265, box_w, 32), 2)
            display_name = name + ("_" if int(pygame.time.get_ticks() / 500) % 2 == 0 else "")
            draw_text(screen, display_name, box_x + 10, 270, WHITE, 18)

            draw_text(screen, "Press Enter to continue",
                      SCREEN_WIDTH // 2, 340, TEXT_DIM, 12, center=True)

        elif phase == "mark":
            draw_panel(screen, 100, 100, SCREEN_WIDTH - 200, 300)
            draw_text(screen, f"The Diviners examine {char.name}...",
                      SCREEN_WIDTH // 2, 130, TEXT_COLOR, 18, center=True)

            if mark_revealed:
                if has_mark:
                    draw_text(screen, "✦ DIVINER'S MARK DETECTED! ✦",
                              SCREEN_WIDTH // 2, 200, GOLD, 24, center=True, shadow=True)
                    draw_text(screen, "A rare birthmark signifying great potential!",
                              SCREEN_WIDTH // 2, 240, TEXT_DIM, 14, center=True)
                else:
                    draw_text(screen, "No Diviner's Mark detected.",
                              SCREEN_WIDTH // 2, 200, TEXT_DIM, 18, center=True)
                    draw_text(screen, "You are among the many. Your journey awaits.",
                              SCREEN_WIDTH // 2, 240, TEXT_DIM, 14, center=True)
                draw_text(screen, "Press Enter to begin the Ceremony",
                          SCREEN_WIDTH // 2, 340, TEXT_DIM, 12, center=True)
            else:
                draw_text(screen, "Press Enter to reveal...",
                          SCREEN_WIDTH // 2, 300, TEXT_DIM, 14, center=True)

        elif phase == "ceremony":
            draw_panel(screen, 20, 20, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40)
            draw_text(screen, "THE CEREMONY", SCREEN_WIDTH // 2, 35,
                      GOLD, 22, center=True, shadow=True)

            visible = ceremony_log[log_scroll:log_scroll + 15]
            for i, line in enumerate(visible):
                color = GOLD if "blessed" in line.lower() or "spirit" in line.lower() else TEXT_DIM
                if "overcomes" in line.lower():
                    color = (100, 255, 100)
                elif "struggles" in line.lower():
                    color = (255, 100, 100)
                draw_text(screen, line, 40, 65 + i * 24, color, 13)

            if char.spirit:
                # Show result
                draw_panel(screen, 40, SCREEN_HEIGHT - 130, SCREEN_WIDTH - 80, 100)
                draw_text(screen, f"Spirit: {char.spirit.name} ({char.spirit.rarity.value})",
                          60, SCREEN_HEIGHT - 120, WHITE, 16)
                god_name = char.god.name.value if char.god else ""
                god_color = GOD_COLORS.get(god_name, TEXT_COLOR)
                draw_text(screen, f"God: {god_name}",
                          60, SCREEN_HEIGHT - 98, god_color, 14)
                if char.physical_traits:
                    draw_text(screen, f"Traits: {', '.join(char.physical_traits)}",
                              60, SCREEN_HEIGHT - 76, TEXT_DIM, 12)
                draw_text(screen, "Press Enter to begin your journey!",
                          60, SCREEN_HEIGHT - 52, GOLD, 13)

            # Scroll hint
            if len(ceremony_log) > 15:
                draw_text(screen, "↑↓ Scroll", SCREEN_WIDTH - 100, SCREEN_HEIGHT - 30,
                          TEXT_DIM, 11)

        pygame.display.flip()


def run_lore_screen(screen: pygame.Surface) -> None:
    """Display lore about the eight gods."""
    clock = pygame.time.Clock()
    selected = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_x:
                    return
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(ALL_GODS)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(ALL_GODS)

        screen.fill(BLACK)
        draw_text(screen, "THE EIGHT GODS", SCREEN_WIDTH // 2, 20,
                  GOLD, 24, center=True, shadow=True)

        # God list
        for i, god in enumerate(ALL_GODS):
            y = 60 + i * 28
            color = GOD_COLORS.get(god.name.value, TEXT_COLOR)
            if i == selected:
                pygame.draw.rect(screen, (40, 40, 60), (20, y - 2, 250, 26))
                draw_text(screen, f"▶ {god.name.value} — {god.title}",
                          28, y, color, 14)
            else:
                draw_text(screen, f"  {god.name.value} — {god.title}",
                          28, y, TEXT_DIM, 14)

        # Detail panel
        god = ALL_GODS[selected]
        color = GOD_COLORS.get(god.name.value, TEXT_COLOR)
        draw_panel(screen, 280, 50, SCREEN_WIDTH - 300, SCREEN_HEIGHT - 80)
        draw_text(screen, god.name.value, 300, 60, color, 22, shadow=True)
        draw_text(screen, god.title, 300, 88, WHITE, 16)
        draw_text(screen, f"Domain: {god.domain}", 300, 112, TEXT_DIM, 13)

        # Description word-wrap
        desc = god.description
        words = desc.split()
        line = ""
        ly = 140
        for w in words:
            test = line + " " + w if line else w
            if len(test) > 50:
                draw_text(screen, line, 300, ly, TEXT_DIM, 12)
                ly += 16
                line = w
            else:
                line = test
        if line:
            draw_text(screen, line, 300, ly, TEXT_DIM, 12)
        ly += 24

        draw_text(screen, "Traits: " + ", ".join(god.personality_traits[:5]),
                  300, ly, TEXT_DIM, 12)
        ly += 22

        draw_text(screen, "Spirits:", 300, ly, WHITE, 13)
        ly += 18
        for s in god.spirits:
            rarity_color = {
                "common": TEXT_DIM, "uncommon": (100, 200, 100),
                "rare": (100, 150, 255), "legendary": GOLD,
            }.get(s.rarity.value, TEXT_DIM)
            draw_text(screen, f"  {s.name} ({s.rarity.value})", 300, ly,
                      rarity_color, 12)
            ly += 16

        draw_text(screen, "ESC: Return", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25,
                  TEXT_DIM, 11, center=True)

        pygame.display.flip()
        clock.tick(FPS)
