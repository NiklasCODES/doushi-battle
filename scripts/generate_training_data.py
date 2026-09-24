"""
Generate Match Telemetry Dataset for Training ML Models with Doushi.ai.
Simulates thousands of Pokémon battles and exports a clean tabular CSV dataset:
'pokemon_battles.csv'

Usage:
    python scripts/generate_training_data.py --samples 10000

Then train with Doushi CLI:
    pip install doushi-cli
    dsh login
    dsh projects create --name "Pokemon Win Predictor" --file pokemon_battles.csv --target winner --prompt "Predict the winning pokemon based on stats, HP, and type advantages"
"""

import os
import sys
import csv
import random
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from monsters import MONSTERS, TYPE_CHART, MOVES


def get_type_multiplier(attacker_type: str, defender_type: str) -> float:
    return TYPE_CHART.get(attacker_type, {}).get(defender_type, 1.0)


def simulate_single_match(p1: dict, p2: dict) -> dict:
    """Simulates a fast mathematical battle between two Pokemon."""
    hp1 = p1["hp"]
    hp2 = p2["hp"]

    # Calculate type multipliers
    t_mult_1 = get_type_multiplier(p1["type"], p2["type"])
    t_mult_2 = get_type_multiplier(p2["type"], p1["type"])

    # Simulate turns
    turn = 0
    max_turns = 30
    while hp1 > 0 and hp2 > 0 and turn < max_turns:
        turn += 1
        
        # Turn priority
        p1_first = p1["speed"] >= p2["speed"] if p1["speed"] != p2["speed"] else random.random() < 0.5

        if p1_first:
            # P1 attacks
            dmg1 = max(4, int(((22 * 35 * (p1["attack"] / max(1, p2["defense"]))) / 50.0 + 2.0) * t_mult_1 * random.uniform(0.85, 1.15)))
            hp2 -= dmg1
            if hp2 <= 0:
                break
            # P2 attacks
            dmg2 = max(4, int(((22 * 35 * (p2["attack"] / max(1, p1["defense"]))) / 50.0 + 2.0) * t_mult_2 * random.uniform(0.85, 1.15)))
            hp1 -= dmg2
        else:
            # P2 attacks
            dmg2 = max(4, int(((22 * 35 * (p2["attack"] / max(1, p1["defense"]))) / 50.0 + 2.0) * t_mult_2 * random.uniform(0.85, 1.15)))
            hp1 -= dmg2
            if hp1 <= 0:
                break
            # P1 attacks
            dmg1 = max(4, int(((22 * 35 * (p1["attack"] / max(1, p2["defense"]))) / 50.0 + 2.0) * t_mult_1 * random.uniform(0.85, 1.15)))
            hp2 -= dmg1

    winner = 1 if hp1 > hp2 else 0

    return {
        "pokemon_1": p1["name"],
        "type_1": p1["type"],
        "hp_1": p1["hp"],
        "attack_1": p1["attack"],
        "defense_1": p1["defense"],
        "speed_1": p1["speed"],
        "pokemon_2": p2["name"],
        "type_2": p2["type"],
        "hp_2": p2["hp"],
        "attack_2": p2["attack"],
        "defense_2": p2["defense"],
        "speed_2": p2["speed"],
        "type_mult_1_vs_2": round(t_mult_1, 2),
        "type_mult_2_vs_1": round(t_mult_2, 2),
        "hp_diff": p1["hp"] - p2["hp"],
        "attack_diff": p1["attack"] - p2["attack"],
        "defense_diff": p1["defense"] - p2["defense"],
        "speed_diff": p1["speed"] - p2["speed"],
        "stat_total_diff": (p1["hp"] + p1["attack"] + p1["defense"] + p1["speed"]) - (p2["hp"] + p2["attack"] + p2["defense"] + p2["speed"]),
        "turns": turn,
        "winner": winner  # 1 if Pokemon 1 won, 0 if Pokemon 2 won
    }


def generate_dataset(num_samples: int = 10000, output_file: str = "pokemon_battles.csv"):
    poke_keys = [k for k in MONSTERS.keys() if k.startswith("poke_")]
    if not poke_keys:
        poke_keys = list(MONSTERS.keys())

    print(f"🎲 Simulating {num_samples} Pokémon battles across {len(poke_keys)} combatants...")
    records = []

    for _ in range(num_samples):
        p1_id, p2_id = random.sample(poke_keys, 2)
        row = simulate_single_match(MONSTERS[p1_id], MONSTERS[p2_id])
        records.append(row)

    fieldnames = list(records[0].keys())
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"✨ Successfully generated {num_samples} battle records in '{output_file}'!")
    print("\n🚀 Next: Train an ML model with Doushi CLI:")
    print("--------------------------------------------------")
    print("  pip install doushi-cli")
    print("  dsh login")
    print(f'  dsh projects create --name "Pokemon Battle Predictor" --file "{output_file}" --target winner')
    print("--------------------------------------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Pokémon combat dataset for ML training")
    parser.add_argument("--samples", type=int, default=5000, help="Number of battle matches to simulate")
    parser.add_argument("--output", type=str, default="pokemon_battles.csv", help="Output CSV path")
    args = parser.parse_args()

    out_path = os.path.join(os.path.dirname(__file__), "..", args.output)
    out_path = os.path.abspath(out_path)
    generate_dataset(args.samples, out_path)
