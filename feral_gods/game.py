"""Main game loop for the Feral Gods turn-based RPG."""

from __future__ import annotations

import random
import sys

from .enums import GodName, StatusEffect
from .gods import ALL_GODS, ALL_SPIRITS, GODS_BY_NAME, Spirit
from .characters import Character, create_character, create_enemy
from .abilities import GOD_ABILITIES, Ability, AbilityType
from .combat import Combat, CombatResult
from .ceremony import Ceremony, SHRINE_CHALLENGES


def print_separator() -> None:
    print("=" * 55)


def print_header(text: str) -> None:
    print_separator()
    print(f"  {text}")
    print_separator()


def display_gods() -> None:
    """Display all gods and their descriptions."""
    print_header("THE EIGHT GODS OF THE FERAL WORLD")
    for i, god in enumerate(ALL_GODS, 1):
        print(f"\n  {i}. {god.name.value} — {god.title}")
        print(f"     Domain: {god.domain}")
        print(f"     Traits: {', '.join(god.personality_traits[:4])}")
        spirits_preview = [s.name for s in god.spirits[:3]]
        print(f"     Spirits: {', '.join(spirits_preview)}...")


def display_character(char: Character) -> None:
    """Display character info."""
    print(f"\n  {char}")
    if char.spirit:
        print(f"  Spirit: {char.spirit.name} ({char.spirit.rarity.value})")
        print(f"  God: {char.god.name.value if char.god else 'None'} — "
              f"{char.god.title if char.god else ''}")
    if char.physical_traits:
        print(f"  Physical traits: {', '.join(char.physical_traits)}")
    print(f"  ATK:{char.attack} DEF:{char.defense} SPD:{char.speed} ACC:{char.accuracy}")
    if char.status_effects:
        effects = [f"{s.effect.value}({s.remaining_turns}t)" for s in char.status_effects]
        print(f"  Status: {', '.join(effects)}")


def character_creation() -> Character:
    """Interactive character creation."""
    print_header("CHARACTER CREATION")
    print("\n  Welcome to the world of Feral Gods.")
    print("  You are about to undergo the Ceremony.\n")

    name = input("  Enter your character's name: ").strip()
    if not name:
        name = "Elodie"

    # Diviner's Mark check (1/1000 normally, but we give a gameplay option)
    print("\n  The Diviners examine you for the Mark...")
    has_mark = random.randint(1, 50) == 1  # ~2% for gameplay
    if has_mark:
        print("  ✦ You bear the DIVINER'S MARK! A rare birthmark signifying great potential!")
    else:
        print("  No Diviner's Mark detected. You are among the many.")

    char = create_character(name, has_diviners_mark=has_mark)

    print(f"\n  {name}, age 16, prepares for the Ceremony...")
    return char


def run_ceremony_interactive(character: Character) -> Spirit | None:
    """Run the Ceremony interactively."""
    print_header("THE CEREMONY")
    ceremony = Ceremony(season=random.choice(["Spring", "Autumn"]))

    print(f"\n  Season: {ceremony.season}")
    print("  The feast was held last night. Today, you journey to the shrines.\n")

    # Let player choose shrine order
    gods = list(SHRINE_CHALLENGES.keys())
    print("  Choose the order to visit the shrines:")
    for i, god_name in enumerate(gods, 1):
        shrine = SHRINE_CHALLENGES[god_name]
        print(f"    {i}. {god_name} — {shrine.name}")

    print(f"\n  Enter shrine numbers in order (e.g., '1 3 5 2 4 6 7 8'),")
    print("  or press Enter for random order:")

    choice = input("  > ").strip()
    if choice:
        try:
            indices = [int(x) - 1 for x in choice.split()]
            shrine_order = [gods[i] for i in indices if 0 <= i < len(gods)]
            # Add any missing shrines
            for g in gods:
                if g not in shrine_order:
                    shrine_order.append(g)
        except (ValueError, IndexError):
            shrine_order = None
    else:
        shrine_order = None

    spirit = ceremony.run_ceremony(character, shrine_order)

    for line in ceremony.log:
        print(line)

    return spirit


def run_combat_interactive(player: Character, enemy: Character) -> CombatResult:
    """Run combat with player input."""
    combat = Combat(player, enemy)
    combat._determine_initiative()

    print_header(f"COMBAT: {player.name} vs {enemy.name}")
    print()
    display_character(player)
    print("  VS")
    display_character(enemy)
    print()

    while player.is_alive and enemy.is_alive and combat.turn_number < combat.MAX_TURNS:
        if combat.is_player_turn:
            # Player turn
            print(f"\n--- Turn {combat.turn_number + 1}: YOUR TURN ---")

            # Show status
            status_msgs = player.tick_status_effects()
            for msg in status_msgs:
                print(msg)

            if not player.is_alive:
                print(f"  {player.name} has fallen!")
                break

            if player.has_status(StatusEffect.STUNNED):
                print(f"  {player.name} is stunned and cannot act!")
                player.tick_cooldowns()
                combat.is_player_turn = False
                combat.turn_number += 1
                continue

            # Show options
            print(f"\n  {player}")
            print(f"  Enemy: {enemy}")
            print("\n  Actions:")
            print("    1. Basic Attack")
            print("    2. Use Ability")
            print("    3. Rest (recover energy)")

            action_choice = input("  Choose action (1-3): ").strip()

            if action_choice == "2":
                active = player.get_active_abilities()
                if not active:
                    print("  No abilities available! Performing basic attack.")
                    messages = combat.execute_turn("attack")
                else:
                    print("\n  Available Abilities:")
                    for i, a in enumerate(active, 1):
                        desc = f"DMG:{a.damage}" if a.damage else ""
                        if a.healing:
                            desc += f" HEAL:{a.healing}"
                        if a.defense_bonus:
                            desc += f" DEF+{a.defense_bonus}"
                        desc += f" COST:{a.energy_cost}"
                        if a.cooldown:
                            desc += f" CD:{a.cooldown}"
                        print(f"    {i}. {a.name} — {a.description} [{desc}]")

                    ability_choice = input(f"  Choose ability (1-{len(active)}): ").strip()
                    try:
                        idx = int(ability_choice) - 1
                        if 0 <= idx < len(active):
                            real_idx = player.abilities.index(active[idx])
                            messages = combat.execute_turn("ability", real_idx)
                        else:
                            print("  Invalid choice. Basic attack.")
                            messages = combat.execute_turn("attack")
                    except ValueError:
                        print("  Invalid input. Basic attack.")
                        messages = combat.execute_turn("attack")
            elif action_choice == "3":
                messages = combat.execute_turn("rest")
            else:
                messages = combat.execute_turn("attack")

            for msg in messages:
                print(msg)

        else:
            # Enemy turn
            action, idx = combat._ai_choose_action(enemy, player)
            messages = combat.execute_turn(action, idx)
            for msg in messages:
                print(msg)

    # Determine result
    if not enemy.is_alive:
        print(f"\n  ★ {player.name} is victorious! ★")
        result = CombatResult(player, enemy, [])
    elif not player.is_alive:
        print(f"\n  ✗ {player.name} has been defeated... ✗")
        result = CombatResult(enemy, player, [])
    else:
        print("\n  The battle ends in a draw!")
        result = CombatResult(player, enemy, [])

    return result


def generate_random_enemy(level: int) -> Character:
    """Generate a random enemy at the given level."""
    enemy_names = [
        "Wild Beastkin", "Rogue Spiritbearer", "Feral Guardian",
        "Shadow Stalker", "Swarm Drone", "Pack Hunter",
        "Deep Lurker", "Sky Raider", "Stone Sentinel",
        "Mind Weaver", "Flame Wyrm Kin", "Tide Caller",
    ]
    name = random.choice(enemy_names)

    # Pick a random spirit
    god_name = random.choice(list(ALL_SPIRITS.keys()))
    spirit = random.choice(ALL_SPIRITS[god_name])

    return create_enemy(name, spirit, level)


def main_menu() -> None:
    """Display the main menu."""
    print_header("FERAL GODS — A Turn-Based RPG")
    print()
    print("  In this world, each person receives a spirit companion")
    print("  from one of eight gods during the sacred Ceremony.")
    print("  Your spirit grants you abilities, physical traits,")
    print("  and a bond that lasts a lifetime.")
    print()
    print("  1. New Game")
    print("  2. Quick Battle (auto-generated characters)")
    print("  3. Lore — The Eight Gods")
    print("  4. Quit")
    print()


def quick_battle() -> None:
    """Run a quick auto-battle between two random characters."""
    print_header("QUICK BATTLE")
    player = generate_random_enemy(random.randint(1, 5))
    player.name = "Champion"
    enemy = generate_random_enemy(random.randint(1, 5))

    display_character(player)
    print("  VS")
    display_character(enemy)

    combat = Combat(player, enemy)
    result = combat.run_auto_combat()

    for line in result.log:
        print(line)

    print(f"\n  Winner: {result.winner.name} ({result.winner.spirit.name if result.winner.spirit else 'Unknown'})")


def game_loop(player: Character) -> None:
    """Main game loop after character creation and ceremony."""
    battle_count = 0

    while player.is_alive:
        print_separator()
        print(f"\n  {player}")
        print(f"  Battles won: {battle_count}")
        print()
        print("  What would you like to do?")
        print("    1. Seek a battle")
        print("    2. View character")
        print("    3. View abilities")
        print("    4. Rest (full heal)")
        print("    5. Return to main menu")
        print()

        choice = input("  > ").strip()

        if choice == "1":
            enemy_level = max(1, player.level + random.randint(-1, 1))
            enemy = generate_random_enemy(enemy_level)
            result = run_combat_interactive(player, enemy)

            if result.winner == player:
                xp = enemy.level * 30 + 20
                msgs = player.gain_experience(xp)
                for msg in msgs:
                    print(msg)
                battle_count += 1
            else:
                print("\n  You have fallen in battle...")
                print("  But the spirit world grants you another chance.")
                player.current_hp = player.max_hp // 2
                player.current_energy = player.max_energy // 2

        elif choice == "2":
            display_character(player)

        elif choice == "3":
            print("\n  Your Abilities:")
            for a in player.abilities:
                type_str = f"[{a.ability_type.value}]"
                desc = f"DMG:{a.damage}" if a.damage else ""
                if a.healing:
                    desc += f" HEAL:{a.healing}"
                if a.defense_bonus:
                    desc += f" DEF+{a.defense_bonus}"
                if a.speed_bonus:
                    desc += f" SPD+{a.speed_bonus}"
                if a.accuracy and a.ability_type == AbilityType.PASSIVE:
                    desc += f" ACC+{a.accuracy}"
                if a.energy_cost:
                    desc += f" COST:{a.energy_cost}"
                print(f"    {type_str} {a.name}: {a.description} [{desc}]")

        elif choice == "4":
            player.current_hp = player.max_hp
            player.current_energy = player.max_energy
            player.status_effects = []
            player.cooldowns = {}
            print("  You rest and fully recover.")

        elif choice == "5":
            break

        else:
            print("  Invalid choice.")


def main() -> None:
    """Main entry point for the Feral Gods RPG."""
    while True:
        main_menu()
        choice = input("  > ").strip()

        if choice == "1":
            player = character_creation()
            spirit = run_ceremony_interactive(player)
            if spirit:
                print(f"\n  Your journey begins with {spirit.name} at your side!")
                game_loop(player)
            else:
                print("\n  You are ungifted... but your story is not over.")
                print("  (In the full game, you would follow Elodie's path to find your spirit.)")
                # Give a default spirit for gameplay
                print("  For now, a mysterious force grants you a companion...")
                god_name = random.choice(list(ALL_SPIRITS.keys()))
                spirit = random.choice(ALL_SPIRITS[god_name])
                player.receive_spirit(spirit)
                print(f"  A {spirit.name} appears!")
                game_loop(player)

        elif choice == "2":
            quick_battle()

        elif choice == "3":
            display_gods()

        elif choice == "4":
            print("\n  Farewell, spiritbearer. May the gods watch over you.\n")
            break

        else:
            print("  Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
