"""Reusable UI drawing helpers for the Feral Gods GUI."""

from __future__ import annotations

import pygame

from .constants import (
    BLACK, WHITE, GREY, DARK_GREY, TEXT_COLOR, TEXT_DIM,
    PANEL_BG, PANEL_BORDER, MENU_HIGHLIGHT, MENU_BG,
    HP_GREEN, HP_RED, ENERGY_BLUE, XP_YELLOW, BAR_BG,
    GOLD, SHADOW, GOD_COLORS,
    SCREEN_WIDTH, SCREEN_HEIGHT,
)


def get_font(size: int = 16) -> pygame.font.Font:
    """Return a default font at the given size."""
    return pygame.font.SysFont("arial", size)


def draw_text(surface: pygame.Surface, text: str, x: int, y: int,
              color: tuple = TEXT_COLOR, size: int = 16,
              center: bool = False, shadow: bool = False) -> pygame.Rect:
    """Draw text and return its bounding rect."""
    font = get_font(size)
    if shadow:
        shadow_surf = font.render(text, True, SHADOW)
        surface.blit(shadow_surf, (x + 1, y + 1))
    rendered = font.render(text, True, color)
    if center:
        rect = rendered.get_rect(center=(x, y))
    else:
        rect = rendered.get_rect(topleft=(x, y))
    surface.blit(rendered, rect)
    return rect


def draw_panel(surface: pygame.Surface, x: int, y: int,
               w: int, h: int, alpha: int = 220) -> None:
    """Draw a semi-transparent UI panel with border."""
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((*PANEL_BG, alpha))
    surface.blit(panel, (x, y))
    pygame.draw.rect(surface, PANEL_BORDER, (x, y, w, h), 2)


def draw_bar(surface: pygame.Surface, x: int, y: int, w: int, h: int,
             current: int, maximum: int, fg_color: tuple,
             bg_color: tuple = BAR_BG, label: str = "") -> None:
    """Draw a resource bar (HP, energy, XP)."""
    pygame.draw.rect(surface, bg_color, (x, y, w, h))
    if maximum > 0:
        fill_w = max(0, int(w * current / maximum))
        pygame.draw.rect(surface, fg_color, (x, y, fill_w, h))
    pygame.draw.rect(surface, GREY, (x, y, w, h), 1)
    if label:
        font = get_font(h - 2)
        text = font.render(label, True, WHITE)
        surface.blit(text, (x + 4, y))


def draw_hp_bar(surface: pygame.Surface, x: int, y: int,
                w: int, h: int, current_hp: int, max_hp: int) -> None:
    ratio = current_hp / max_hp if max_hp > 0 else 0
    color = HP_GREEN if ratio > 0.5 else (GOLD if ratio > 0.25 else HP_RED)
    draw_bar(surface, x, y, w, h, current_hp, max_hp, color,
             label=f"HP {current_hp}/{max_hp}")


def draw_energy_bar(surface: pygame.Surface, x: int, y: int,
                    w: int, h: int, current: int, maximum: int) -> None:
    draw_bar(surface, x, y, w, h, current, maximum, ENERGY_BLUE,
             label=f"EN {current}/{maximum}")


def draw_menu(surface: pygame.Surface, options: list[str],
              selected: int, x: int, y: int, w: int,
              item_h: int = 28, show_cursor: bool = True) -> None:
    """Draw a selectable menu list."""
    draw_panel(surface, x - 4, y - 4, w + 8, len(options) * item_h + 8)
    for i, opt in enumerate(options):
        iy = y + i * item_h
        if i == selected:
            pygame.draw.rect(surface, MENU_HIGHLIGHT, (x, iy, w, item_h - 2))
            if show_cursor:
                draw_text(surface, "▶", x + 4, iy + 2, GOLD, 16)
            draw_text(surface, opt, x + 22, iy + 4, WHITE, 14)
        else:
            draw_text(surface, opt, x + 22, iy + 4, TEXT_DIM, 14)


def draw_message_log(surface: pygame.Surface, messages: list[str],
                     x: int, y: int, w: int, h: int,
                     max_lines: int = 6) -> None:
    """Draw a scrolling message log panel."""
    draw_panel(surface, x, y, w, h)
    visible = messages[-max_lines:] if len(messages) > max_lines else messages
    for i, msg in enumerate(visible):
        draw_text(surface, msg, x + 8, y + 6 + i * 18, TEXT_DIM, 13)


def draw_character_hud(surface: pygame.Surface, char, x: int, y: int,
                       w: int = 220) -> None:
    """Draw compact character status HUD."""
    draw_panel(surface, x, y, w, 70)
    name_label = char.name
    if char.spirit:
        name_label += f" [{char.spirit.name}]"
    draw_text(surface, name_label, x + 8, y + 4, WHITE, 13, shadow=True)
    draw_text(surface, f"Lv.{char.level}", x + w - 50, y + 4, GOLD, 13)
    draw_hp_bar(surface, x + 8, y + 24, w - 16, 16, char.current_hp, char.max_hp)
    draw_energy_bar(surface, x + 8, y + 44, w - 16, 16,
                    char.current_energy, char.max_energy)
