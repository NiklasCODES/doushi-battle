"""
Combat & Win Probability Engine for Pokémon Battle Simulator.
Calculates live win probabilities based on HP ratios, stat differentials,
elemental type matchups, and selects optimal AI opponent tactics.
"""

import math
import random
from typing import Dict, Any, Tuple
from monsters import TYPE_CHART, MOVES


class CombatEngine:
    """
    Evaluates combat state to calculate dynamic win probabilities
    and optimal AI decision trees.
    """

    def calculate_type_multiplier(self, move_type: str, defender_type: str) -> float:
        return TYPE_CHART.get(move_type, {}).get(defender_type, 1.0)

    def predict_win_probability(self, player: Dict[str, Any], opponent: Dict[str, Any]) -> Tuple[float, str]:
        """
        Features evaluated for combat probability:
        - player_hp_pct vs opponent_hp_pct
        - base attack / defense differential
        - speed priority differential
        - elemental matchup matrix
        
        Returns:
            (player_win_prob, insight_summary)
        """
        # 1. HP ratio feature
        p_hp_ratio = max(0.01, player["hp"] / max(1, player["max_hp"]))
        o_hp_ratio = max(0.01, opponent["hp"] / max(1, opponent["max_hp"]))
        hp_delta = (p_hp_ratio - o_hp_ratio) * 2.5

        # 2. Stat balance feature
        stat_delta = (
            (player["attack"] - opponent["defense"] * 0.8) +
            (player["speed"] - opponent["speed"]) * 0.6
        ) / 25.0

        # 3. Type advantage feature
        p_type_mult = self.calculate_type_multiplier(player["type"], opponent["type"])
        o_type_mult = self.calculate_type_multiplier(opponent["type"], player["type"])
        type_delta = (p_type_mult - o_type_mult) * 1.5

        # 4. Logistic sigmoid activation
        raw_score = hp_delta + stat_delta + type_delta
        prob = 1.0 / (1.0 + math.exp(-raw_score))
        prob = max(0.05, min(0.95, prob))

        # Tactical insight
        if type_delta > 0.5:
            insight = f"Type advantage ({player['type']} > {opponent['type']}) adds +{int(type_delta*20)}% win odds."
        elif hp_delta < -0.8:
            insight = "Critical HP deficit. Immediate recovery or high-power strike recommended."
        elif player["speed"] > opponent["speed"] + 10:
            insight = "Speed initiative guarantees turn priority advantage."
        else:
            insight = "Balanced matchup. Accuracy and critical hits will decide the outcome."

        return prob, insight

    def calculate_damage(self, attacker: Dict[str, Any], defender: Dict[str, Any], move_name: str) -> Tuple[int, bool, float, str]:
        """
        Computes damage using power, stats, type effectiveness, and critical roll.
        Returns: (damage_dealt, is_crit, multiplier, effect_message)
        """
        move = MOVES.get(move_name, {"power": 20, "type": "Normal", "accuracy": 90})
        
        # Accuracy check
        roll = random.randint(1, 100)
        if roll > move.get("accuracy", 100):
            return 0, False, 0.0, "Missed!"

        if move.get("power", 0) == 0:
            return 0, False, 1.0, "Stat buff activated!"

        # Base formula
        level_factor = 22.0
        base_dmg = ((level_factor * move["power"] * (attacker["attack"] / max(1, defender["defense"]))) / 50.0) + 2.0
        
        # Type effectiveness
        mult = self.calculate_type_multiplier(move["type"], defender["type"])
        
        # Critical hit roll (12% chance)
        is_crit = random.random() < 0.12
        crit_mult = 1.5 if is_crit else 1.0
        
        # Random variance (0.88 to 1.12)
        variance = random.uniform(0.88, 1.12)
        
        total_damage = int(base_dmg * mult * crit_mult * variance)
        total_damage = max(5, total_damage)

        desc = ""
        if mult >= 1.5:
            desc = "Super effective! 🔥"
        elif mult <= 0.7:
            desc = "Not very effective... 🛡️"
        
        if is_crit:
            desc += " CRITICAL HIT! 💥"

        return total_damage, is_crit, mult, desc.strip()

    def select_ai_move(self, ai_monster: Dict[str, Any], player_monster: Dict[str, Any]) -> str:
        """
        AI opponent chooses the highest expected value move against the player.
        """
        best_move = ai_monster["moves"][0]
        max_score = -999.0

        for move_name in ai_monster["moves"]:
            move = MOVES.get(move_name)
            if not move:
                continue

            if move.get("power", 0) == 0:
                score = 25.0 if ai_monster["hp"] == ai_monster["max_hp"] else 5.0
            else:
                mult = self.calculate_type_multiplier(move["type"], player_monster["type"])
                acc = move.get("accuracy", 100) / 100.0
                expected_dmg = move["power"] * mult * acc
                score = expected_dmg + random.uniform(-3, 3)

            if score > max_score:
                max_score = score
                best_move = move_name

        return best_move


# Backwards compatibility alias
DoushiCombatEngine = CombatEngine
