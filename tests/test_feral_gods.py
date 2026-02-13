"""Tests for the Feral Gods RPG core mechanics."""

import random
import pytest

from feral_gods.enums import GodName, Rarity, AbilityType, StatusEffect, DamageType
from feral_gods.abilities import (
    Ability, GOD_ABILITIES, VENOMOUS_BITE, FIRE_BREATH, GUST_SLASH,
    TIDAL_SURGE, SWARM_STRIKE, FERAL_SLASH, GROUND_SLAM, SHADOW_STRIKE,
    PSYCHIC_BLAST, REPTILIAN_SKIN, STONESKIN, BERSERKER_RAGE, BARRIER,
    VANISH, PHOENIX_FLAME,
)
from feral_gods.gods import (
    God, Spirit, ALL_GODS, ALL_SPIRITS, GODS_BY_NAME,
    SNAKE, DRAGON, PHOENIX, WOLF, SPHINX, BEHEMOTH, KRAKEN,
)
from feral_gods.characters import Character, create_character, create_enemy
from feral_gods.combat import Combat, CombatResult
from feral_gods.ceremony import Ceremony, SHRINE_CHALLENGES, _select_spirit


# -----------------------------------------------------------------------
# Enum tests
# -----------------------------------------------------------------------

class TestEnums:
    def test_god_names(self):
        assert len(GodName) == 8
        assert GodName.OPHIDIA.value == "Ophidia"
        assert GodName.SAGAX.value == "Sagax"

    def test_ability_types(self):
        assert AbilityType.PASSIVE.value == "passive"
        assert AbilityType.ACTIVE.value == "active"

    def test_rarity_values(self):
        assert Rarity.COMMON.value == "common"
        assert Rarity.LEGENDARY.value == "legendary"

    def test_damage_types(self):
        assert DamageType.FIRE.value == "fire"
        assert DamageType.PSYCHIC.value == "psychic"


# -----------------------------------------------------------------------
# Spirit tests
# -----------------------------------------------------------------------

class TestSpirit:
    def test_common_spirit_power(self):
        assert SNAKE.effective_power == 10
        assert SNAKE.rarity == Rarity.COMMON

    def test_legendary_spirit_power(self):
        assert DRAGON.effective_power == 60  # 30 * 2.0
        assert DRAGON.rarity == Rarity.LEGENDARY

    def test_spirit_has_physical_traits(self):
        assert len(DRAGON.physical_traits) > 0
        assert "full scale plating" in DRAGON.physical_traits

    def test_spirit_god_assignment(self):
        assert SNAKE.god == GodName.OPHIDIA
        assert PHOENIX.god == GodName.GALANTH
        assert WOLF.god == GodName.KARN


# -----------------------------------------------------------------------
# God tests
# -----------------------------------------------------------------------

class TestGod:
    def test_all_eight_gods_exist(self):
        assert len(ALL_GODS) == 8

    def test_all_gods_have_spirits(self):
        for god in ALL_GODS:
            assert len(god.spirits) > 0, f"{god.name.value} has no spirits"

    def test_all_gods_have_abilities(self):
        for god in ALL_GODS:
            abilities = god.abilities
            assert len(abilities) == 6, f"{god.name.value} should have 6 abilities"

    def test_gods_by_name_lookup(self):
        assert GODS_BY_NAME["Ophidia"].name == GodName.OPHIDIA
        assert GODS_BY_NAME["Sagax"].title == "The Mind"

    def test_god_personality_traits(self):
        ophidia = GODS_BY_NAME["Ophidia"]
        assert "cunning" in ophidia.personality_traits
        assert "adaptive" in ophidia.personality_traits

    def test_each_god_has_passive_and_active_abilities(self):
        for god in ALL_GODS:
            abilities = god.abilities
            passives = [a for a in abilities if a.ability_type == AbilityType.PASSIVE]
            actives = [a for a in abilities if a.ability_type == AbilityType.ACTIVE]
            assert len(passives) >= 1, f"{god.name.value} should have at least 1 passive"
            assert len(actives) >= 1, f"{god.name.value} should have at least 1 active"


# -----------------------------------------------------------------------
# Ability tests
# -----------------------------------------------------------------------

class TestAbility:
    def test_offensive_ability(self):
        assert VENOMOUS_BITE.is_offensive()
        assert VENOMOUS_BITE.damage == 25
        assert VENOMOUS_BITE.damage_type == DamageType.POISON

    def test_supportive_ability(self):
        assert PHOENIX_FLAME.is_supportive()
        assert PHOENIX_FLAME.healing == 35

    def test_can_use_with_energy(self):
        assert VENOMOUS_BITE.can_use(15)
        assert not VENOMOUS_BITE.can_use(10)

    def test_passive_ability_no_cost(self):
        assert REPTILIAN_SKIN.energy_cost == 0
        assert REPTILIAN_SKIN.ability_type == AbilityType.PASSIVE

    def test_all_god_abilities_exist(self):
        assert len(GOD_ABILITIES) == 8
        for god_name, abilities in GOD_ABILITIES.items():
            assert len(abilities) == 6, f"{god_name} should have 6 abilities"


# -----------------------------------------------------------------------
# Character tests
# -----------------------------------------------------------------------

class TestCharacter:
    def test_create_ungifted_character(self):
        char = create_character("Elodie")
        assert char.is_ungifted
        assert char.spirit is None
        assert char.name == "Elodie"
        assert char.is_alive

    def test_create_character_with_spirit(self):
        char = create_character("Kael", spirit=WOLF)
        assert not char.is_ungifted
        assert char.spirit == WOLF
        assert char.god.name == GodName.KARN

    def test_character_stats_boosted_by_spirit(self):
        char_base = create_character("Base")
        char_spirit = create_character("Spirit", spirit=DRAGON)
        assert char_spirit.max_hp > char_base.max_hp
        assert char_spirit.max_energy > char_base.max_energy

    def test_legendary_spirit_gives_more_stats(self):
        common = create_character("Common", spirit=SNAKE)
        legendary = create_character("Legendary", spirit=DRAGON)
        assert legendary.max_hp > common.max_hp

    def test_receive_spirit(self):
        char = create_character("Ungifted")
        assert char.is_ungifted
        char.receive_spirit(PHOENIX)
        assert not char.is_ungifted
        assert char.spirit == PHOENIX
        assert char.god.name == GodName.GALANTH

    def test_character_has_abilities_from_spirit(self):
        char = create_character("Kael", spirit=WOLF)
        assert len(char.abilities) == 6
        ability_names = [a.name for a in char.abilities]
        assert "Retractable Claws" in ability_names
        assert "Feral Slash" in ability_names

    def test_physical_traits_from_spirit(self):
        char = create_character("Kael", spirit=WOLF)
        assert "yellow eyes" in char.physical_traits

    def test_passive_bonuses(self):
        char = create_character("Tank", spirit=BEHEMOTH)
        # Stoneskin gives defense_bonus=12, Tireless gives speed_bonus=3
        assert char.defense > char.base_defense

    def test_basic_attack(self):
        random.seed(42)
        attacker = create_character("Attacker", spirit=WOLF)
        target = create_character("Target", spirit=SNAKE)
        initial_hp = target.current_hp
        attacker.basic_attack(target)
        # With seed 42, we can check it went through
        assert target.current_hp <= initial_hp

    def test_status_effects(self):
        char = create_character("Test", spirit=WOLF)
        char.apply_status(StatusEffect.POISONED, 3)
        assert char.has_status(StatusEffect.POISONED)
        initial_hp = char.current_hp
        char.tick_status_effects()
        assert char.current_hp < initial_hp  # poison does damage

    def test_status_effect_wears_off(self):
        char = create_character("Test", spirit=WOLF)
        char.apply_status(StatusEffect.POISONED, 1)
        char.tick_status_effects()
        assert not char.has_status(StatusEffect.POISONED)

    def test_experience_and_level_up(self):
        char = create_character("Test", spirit=WOLF)
        assert char.level == 1
        char.gain_experience(100)  # Level 1 needs 100 XP
        assert char.level == 2
        assert char.max_hp > 100  # HP increased from level and spirit

    def test_rest_recovers_energy(self):
        char = create_character("Test", spirit=WOLF)
        char.current_energy = 10
        char.rest()
        assert char.current_energy == 30  # recovers 20

    def test_cooldowns(self):
        char = create_character("Test", spirit=WOLF)
        char.cooldowns["Predator Pounce"] = 2
        char.tick_cooldowns()
        assert char.cooldowns["Predator Pounce"] == 1
        char.tick_cooldowns()
        assert "Predator Pounce" not in char.cooldowns

    def test_get_active_abilities(self):
        char = create_character("Test", spirit=WOLF)
        active = char.get_active_abilities()
        assert all(a.ability_type == AbilityType.ACTIVE for a in active)
        assert len(active) > 0

    def test_create_enemy(self):
        enemy = create_enemy("Boss", DRAGON, level=5)
        assert enemy.level == 5
        assert enemy.spirit == DRAGON
        assert enemy.max_hp > 100  # boosted by level and legendary spirit

    def test_diviners_mark(self):
        char = create_character("Marked", has_diviners_mark=True)
        assert char.has_diviners_mark

    def test_character_string(self):
        char = create_character("Kael", spirit=WOLF)
        s = str(char)
        assert "Kael" in s
        assert "Wolf" in s
        assert "Karn" in s

    def test_berserker_status_boosts_attack_reduces_defense(self):
        char = create_character("Rage", spirit=WOLF)
        base_atk = char.attack
        base_def = char.defense
        char.apply_status(StatusEffect.BERSERKER, 2)
        assert char.attack > base_atk
        assert char.defense < base_def

    def test_blinded_reduces_accuracy(self):
        char = create_character("Blind", spirit=WOLF)
        base_acc = char.accuracy
        char.apply_status(StatusEffect.BLINDED, 2)
        assert char.accuracy < base_acc


# -----------------------------------------------------------------------
# Combat tests
# -----------------------------------------------------------------------

class TestCombat:
    def test_combat_init(self):
        p = create_character("Player", spirit=WOLF)
        e = create_enemy("Enemy", SNAKE, level=1)
        combat = Combat(p, e)
        assert combat.player == p
        assert combat.enemy == e

    def test_auto_combat_produces_result(self):
        random.seed(42)
        p = create_character("Player", spirit=DRAGON)
        e = create_enemy("Enemy", SNAKE, level=1)
        combat = Combat(p, e)
        result = combat.run_auto_combat()
        assert isinstance(result, CombatResult)
        assert result.winner is not None
        assert len(result.log) > 0

    def test_stronger_character_wins_more(self):
        """Legendary spirit should beat common spirit most of the time."""
        wins = 0
        for i in range(20):
            random.seed(i)
            p = create_character("Player", spirit=DRAGON)
            e = create_enemy("Enemy", SNAKE, level=1)
            combat = Combat(p, e)
            result = combat.run_auto_combat()
            if result.winner.name == "Player":
                wins += 1
        assert wins >= 15, f"Dragon should beat Snake most times, won {wins}/20"

    def test_combat_respects_max_turns(self):
        random.seed(123)
        p = create_character("Player", spirit=WOLF)
        e = create_enemy("Enemy", BEHEMOTH, level=10)
        combat = Combat(p, e)
        combat.MAX_TURNS = 5
        result = combat.run_auto_combat()
        assert combat.turn_number <= 5

    def test_player_options(self):
        p = create_character("Player", spirit=WOLF)
        e = create_enemy("Enemy", SNAKE, level=1)
        combat = Combat(p, e)
        options = combat.get_player_options()
        assert "actions" in options
        assert "attack" in options["actions"]
        assert "rest" in options["actions"]
        assert "abilities" in options

    def test_execute_turn_attack(self):
        random.seed(42)
        p = create_character("Player", spirit=WOLF)
        e = create_enemy("Enemy", SNAKE, level=1)
        combat = Combat(p, e)
        combat.is_player_turn = True
        messages = combat.execute_turn("attack")
        assert len(messages) > 0

    def test_execute_turn_rest(self):
        p = create_character("Player", spirit=WOLF)
        p.current_energy = 10
        e = create_enemy("Enemy", SNAKE, level=1)
        combat = Combat(p, e)
        combat.is_player_turn = True
        messages = combat.execute_turn("rest")
        assert any("rest" in m.lower() or "recover" in m.lower() for m in messages)


# -----------------------------------------------------------------------
# Ceremony tests
# -----------------------------------------------------------------------

class TestCeremony:
    def test_ceremony_creates_log(self):
        char = create_character("Novice")
        ceremony = Ceremony(season="Spring")
        random.seed(42)
        ceremony.run_ceremony(char)
        assert len(ceremony.log) > 0

    def test_ceremony_grants_spirit(self):
        """With enough attempts, ceremony should grant a spirit."""
        granted = False
        for i in range(50):
            random.seed(i)
            char = create_character("Novice")
            ceremony = Ceremony()
            spirit = ceremony.run_auto_ceremony(char)
            if spirit is not None:
                assert char.spirit is not None
                granted = True
                break
        assert granted, "Ceremony should grant a spirit at least once in 50 tries"

    def test_ceremony_all_shrines_exist(self):
        assert len(SHRINE_CHALLENGES) == 8
        for god_name in SHRINE_CHALLENGES:
            assert god_name in GODS_BY_NAME

    def test_shrine_challenges_have_descriptions(self):
        for name, shrine in SHRINE_CHALLENGES.items():
            assert len(shrine.description) > 0
            assert len(shrine.name) > 0

    def test_diviners_mark_biases_rare_spirits(self):
        """Diviner's mark should give rarer spirits on average."""
        rare_count_with_mark = 0
        rare_count_without = 0
        god = GODS_BY_NAME["Ophidia"]

        for i in range(200):
            random.seed(i)
            spirit = _select_spirit(god, has_mark=True)
            if spirit.rarity in (Rarity.RARE, Rarity.LEGENDARY):
                rare_count_with_mark += 1

        for i in range(200):
            random.seed(i + 1000)
            spirit = _select_spirit(god, has_mark=False)
            if spirit.rarity in (Rarity.RARE, Rarity.LEGENDARY):
                rare_count_without += 1

        assert rare_count_with_mark > rare_count_without

    def test_ceremony_with_specific_shrine_order(self):
        random.seed(10)
        char = create_character("Ordered")
        ceremony = Ceremony(season="Autumn")
        spirit = ceremony.run_ceremony(char, shrine_order=["Galanth", "Ophidia", "Karn"])
        # With this seed + order, we should visit shrines in order
        assert "Galanth" in ceremony.shrines_visited

    def test_select_spirit_returns_valid_spirit(self):
        god = GODS_BY_NAME["Karn"]
        spirit = _select_spirit(god, has_mark=False)
        assert spirit.god == GodName.KARN
        assert spirit.name in [s.name for s in ALL_SPIRITS["Karn"]]


# -----------------------------------------------------------------------
# Integration tests
# -----------------------------------------------------------------------

class TestIntegration:
    def test_full_flow_ceremony_then_combat(self):
        """Test a complete flow: create character, ceremony, then combat."""
        random.seed(7)
        char = create_character("Hero")

        # Ceremony
        ceremony = Ceremony()
        spirit = ceremony.run_auto_ceremony(char)

        if spirit is None:
            # Force spirit for testing
            char.receive_spirit(WOLF)

        assert char.spirit is not None
        assert char.is_alive

        # Combat
        enemy = create_enemy("Foe", SNAKE, level=1)
        combat = Combat(char, enemy)
        result = combat.run_auto_combat()
        assert result.winner is not None

    def test_all_spirits_have_correct_god(self):
        for god_name, spirits in ALL_SPIRITS.items():
            expected_god = GodName(god_name)
            for spirit in spirits:
                assert spirit.god == expected_god, \
                    f"{spirit.name} should belong to {god_name}"

    def test_all_spirits_have_rarity(self):
        for god_name, spirits in ALL_SPIRITS.items():
            for spirit in spirits:
                assert isinstance(spirit.rarity, Rarity)

    def test_each_god_has_common_spirits(self):
        for god_name, spirits in ALL_SPIRITS.items():
            commons = [s for s in spirits if s.rarity == Rarity.COMMON]
            assert len(commons) >= 1, f"{god_name} should have common spirits"

    def test_character_death(self):
        char = create_character("Weak", spirit=SNAKE)
        char.current_hp = 1
        enemy = create_enemy("Strong", DRAGON, level=10)
        combat = Combat(char, enemy)
        result = combat.run_auto_combat()
        assert result.winner.name == "Strong"
