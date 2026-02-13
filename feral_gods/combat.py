"""Turn-based combat system for the Feral Gods RPG."""

from __future__ import annotations

import random

from .enums import StatusEffect
from .characters import Character


class CombatResult:
    """Result of a combat encounter."""
    def __init__(self, winner: Character, loser: Character, log: list[str]) -> None:
        self.winner = winner
        self.loser = loser
        self.log = log


class Combat:
    """Manages a turn-based combat encounter between two characters."""

    MAX_TURNS = 50  # safety limit

    def __init__(self, player: Character, enemy: Character) -> None:
        self.player = player
        self.enemy = enemy
        self.turn_number = 0
        self.log: list[str] = []
        self.is_player_turn = True

    def _determine_initiative(self) -> None:
        """Determine who acts first based on speed."""
        if self.player.speed > self.enemy.speed:
            self.is_player_turn = True
        elif self.enemy.speed > self.player.speed:
            self.is_player_turn = False
        else:
            self.is_player_turn = random.choice([True, False])

    def _ai_choose_action(self, actor: Character, target: Character) -> tuple[str, int | None]:
        """Simple AI for enemy turns. Returns (action_type, ability_index)."""
        if actor.has_status(StatusEffect.STUNNED):
            return ("stunned", None)

        active_abilities = actor.get_active_abilities()

        # Prioritize healing if low HP
        if actor.current_hp < actor.max_hp * 0.3:
            healing = [a for a in active_abilities if a.healing > 0]
            if healing:
                return ("ability", actor.abilities.index(healing[0]))

        # Use offensive abilities with some probability
        offensive = [a for a in active_abilities if a.is_offensive()]
        if offensive and random.random() < 0.6:
            chosen = random.choice(offensive)
            return ("ability", actor.abilities.index(chosen))

        # Apply status effects
        status_abilities = [a for a in active_abilities
                            if a.status_effect and not a.is_offensive()]
        if status_abilities and random.random() < 0.4:
            chosen = random.choice(status_abilities)
            return ("ability", actor.abilities.index(chosen))

        # Rest if low on energy
        if actor.current_energy < 15:
            return ("rest", None)

        # Default to basic attack
        return ("attack", None)

    def execute_turn(self, action: str, ability_index: int | None = None) -> list[str]:
        """Execute a single turn's action. Returns messages."""
        self.turn_number += 1
        messages = []

        if self.is_player_turn:
            actor = self.player
            target = self.enemy
        else:
            actor = self.enemy
            target = self.player

        messages.append(f"\n--- Turn {self.turn_number}: {actor.name}'s turn ---")

        # Process status effects at start of turn
        status_msgs = actor.tick_status_effects()
        messages.extend(status_msgs)

        if not actor.is_alive:
            messages.append(f"  {actor.name} has fallen!")
            return messages

        # Check if stunned
        if actor.has_status(StatusEffect.STUNNED):
            messages.append(f"  {actor.name} is stunned and cannot act!")
            actor.tick_cooldowns()
            self.is_player_turn = not self.is_player_turn
            return messages

        # Execute chosen action
        if action == "attack":
            messages.extend(actor.basic_attack(target))
        elif action == "ability" and ability_index is not None:
            active = [a for a in actor.abilities if a.ability_type.value == "active"]
            all_abilities = actor.abilities
            if 0 <= ability_index < len(all_abilities):
                ability = all_abilities[ability_index]
                messages.extend(actor.use_ability(ability, target))
            else:
                messages.append("  Invalid ability!")
                messages.extend(actor.basic_attack(target))
        elif action == "rest":
            messages.extend(actor.rest())
        elif action == "stunned":
            pass  # Already handled above
        else:
            messages.append("  Invalid action, performing basic attack.")
            messages.extend(actor.basic_attack(target))

        # Tick cooldowns
        actor.tick_cooldowns()

        # Check for defeat
        if not target.is_alive:
            messages.append(f"\n  {target.name} has been defeated!")

        self.is_player_turn = not self.is_player_turn
        return messages

    def run_auto_combat(self) -> CombatResult:
        """Run a fully automated combat (both sides AI-controlled)."""
        self.log = [f"\n{'='*50}",
                    f"COMBAT: {self.player.name} vs {self.enemy.name}",
                    f"{'='*50}"]
        self._determine_initiative()

        while self.player.is_alive and self.enemy.is_alive and self.turn_number < self.MAX_TURNS:
            if self.is_player_turn:
                action, idx = self._ai_choose_action(self.player, self.enemy)
            else:
                action, idx = self._ai_choose_action(self.enemy, self.player)

            messages = self.execute_turn(action, idx)
            self.log.extend(messages)

        if not self.enemy.is_alive:
            self.log.append(f"\n{self.player.name} wins!")
            return CombatResult(self.player, self.enemy, self.log)
        elif not self.player.is_alive:
            self.log.append(f"\n{self.enemy.name} wins!")
            return CombatResult(self.enemy, self.player, self.log)
        else:
            # Draw after max turns
            self.log.append("\nThe battle ends in a draw!")
            return CombatResult(self.player, self.enemy, self.log)

    def get_player_options(self) -> dict[str, list[str]]:
        """Get available actions for the player."""
        options: dict[str, list[str]] = {"actions": ["attack", "rest"]}
        active = self.player.get_active_abilities()
        if active:
            options["abilities"] = [
                f"{a.name} (DMG:{a.damage} HEAL:{a.healing} COST:{a.energy_cost})"
                for a in active
            ]
        return options
