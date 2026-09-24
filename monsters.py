"""
Monsters & Pokémon Database for Retro Terminal Pokémon Battle Simulator.
Contains ANSI half-block color sprites, base stats, types, and move pools
for all original 151 Pokémon.
"""

import os
import json
from typing import Dict, Any, List, Optional

# Full Pokémon Type Chart Matrix
TYPE_CHART = {
    "Normal": {
        "Rock": 0.5, "Ghost": 0.0, "Steel": 0.5
    },
    "Fire": {
        "Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 2.0, "Bug": 2.0,
        "Rock": 0.5, "Dragon": 0.5, "Steel": 2.0
    },
    "Water": {
        "Fire": 2.0, "Water": 0.5, "Grass": 0.5, "Ground": 2.0, "Rock": 2.0,
        "Dragon": 0.5
    },
    "Grass": {
        "Fire": 0.5, "Water": 2.0, "Grass": 0.5, "Poison": 0.5, "Ground": 2.0,
        "Flying": 0.5, "Bug": 0.5, "Rock": 2.0, "Dragon": 0.5, "Steel": 0.5
    },
    "Electric": {
        "Water": 2.0, "Electric": 0.5, "Grass": 0.5, "Ground": 0.0, "Flying": 2.0,
        "Dragon": 0.5
    },
    "Ice": {
        "Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 0.5, "Ground": 2.0,
        "Flying": 2.0, "Dragon": 2.0, "Steel": 0.5
    },
    "Fighting": {
        "Normal": 2.0, "Ice": 2.0, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5,
        "Bug": 0.5, "Rock": 2.0, "Ghost": 0.0, "Dark": 2.0, "Steel": 2.0, "Fairy": 0.5
    },
    "Poison": {
        "Grass": 2.0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5,
        "Steel": 0.0, "Fairy": 2.0
    },
    "Ground": {
        "Fire": 2.0, "Electric": 2.0, "Grass": 0.5, "Poison": 2.0, "Flying": 0.0,
        "Bug": 0.5, "Rock": 2.0, "Steel": 2.0
    },
    "Flying": {
        "Electric": 0.5, "Grass": 2.0, "Fighting": 2.0, "Bug": 2.0, "Rock": 0.5,
        "Steel": 0.5
    },
    "Psychic": {
        "Fighting": 2.0, "Poison": 2.0, "Psychic": 0.5, "Dark": 0.0, "Steel": 0.5
    },
    "Bug": {
        "Fire": 0.5, "Grass": 2.0, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5,
        "Psychic": 2.0, "Ghost": 0.5, "Dark": 2.0, "Steel": 0.5, "Fairy": 0.5
    },
    "Rock": {
        "Fire": 2.0, "Ice": 2.0, "Fighting": 0.5, "Ground": 0.5, "Flying": 2.0,
        "Bug": 2.0, "Steel": 0.5
    },
    "Ghost": {
        "Normal": 0.0, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5
    },
    "Dragon": {
        "Dragon": 2.0, "Steel": 0.5, "Fairy": 0.0
    },
    "Steel": {
        "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2.0, "Rock": 2.0,
        "Fairy": 2.0, "Steel": 0.5
    },
    "Dark": {
        "Fighting": 0.5, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5, "Fairy": 0.5
    },
    "Fairy": {
        "Fire": 0.5, "Fighting": 2.0, "Poison": 0.5, "Dragon": 2.0, "Dark": 2.0,
        "Steel": 0.5
    }
}

MOVES = {
    # Fire Moves
    "Flamethrower": {"name": "Flamethrower", "type": "Fire", "power": 36, "accuracy": 95, "desc": "Blasts a scorching stream of flame."},
    "Fire Blast": {"name": "Fire Blast", "type": "Fire", "power": 50, "accuracy": 75, "desc": "High power inferno with intense thermal output."},
    "Flame Wheel": {"name": "Flame Wheel", "type": "Fire", "power": 25, "accuracy": 100, "desc": "Spins in a ring of fire. Never misses."},
    "Fire Spin": {"name": "Fire Spin", "type": "Fire", "power": 22, "accuracy": 100, "desc": "Traps the foe in a ring of scorching fire."},

    # Water Moves
    "Hydro Cannon": {"name": "Hydro Cannon", "type": "Water", "power": 46, "accuracy": 85, "desc": "Fires pressurized torrents of water."},
    "Hydro Pump": {"name": "Hydro Pump", "type": "Water", "power": 48, "accuracy": 80, "desc": "Blasts a huge volume of water at high speed."},
    "Aqua Jet": {"name": "Aqua Jet", "type": "Water", "power": 22, "accuracy": 100, "desc": "Fast-priority strike before opponent can react."},
    "Water Pulse": {"name": "Water Pulse", "type": "Water", "power": 30, "accuracy": 95, "desc": "Ultrasonic water waves that can disorient."},
    "Surf": {"name": "Surf", "type": "Water", "power": 38, "accuracy": 95, "desc": "Swamps the arena in a gigantic tidal wave."},

    # Electric Moves
    "Thunderbolt": {"name": "Thunderbolt", "type": "Electric", "power": 36, "accuracy": 95, "desc": "A strong jolt of high-voltage electricity."},
    "Volt Charge": {"name": "Volt Charge", "type": "Electric", "power": 48, "accuracy": 80, "desc": "Discharges massive electrical power."},
    "Spark Dash": {"name": "Spark Dash", "type": "Electric", "power": 22, "accuracy": 100, "desc": "Quick electric dash strike."},
    "Thunder Wave": {"name": "Thunder Wave", "type": "Electric", "power": 20, "accuracy": 100, "desc": "A weak jolt that paralyzes the opponent."},

    # Grass Moves
    "Solar Beam": {"name": "Solar Beam", "type": "Grass", "power": 52, "accuracy": 80, "desc": "Concentrated solar radiation blast."},
    "Vine Whip": {"name": "Vine Whip", "type": "Grass", "power": 25, "accuracy": 100, "desc": "Lashes out with tough, thorny vines."},
    "Giga Drain": {"name": "Giga Drain", "type": "Grass", "power": 30, "accuracy": 90, "desc": "Absorbs half the damage dealt as HP heal."},
    "Razor Leaf": {"name": "Razor Leaf", "type": "Grass", "power": 28, "accuracy": 95, "desc": "Sharp-edged leaves launched with high crit rate."},

    # Psychic Moves
    "Psychic": {"name": "Psychic", "type": "Psychic", "power": 42, "accuracy": 95, "desc": "A powerful telekinetic assault."},
    "Psybeam": {"name": "Psybeam", "type": "Psychic", "power": 32, "accuracy": 95, "desc": "Fires a mind-bending telepathic ray."},
    "Mind Blast": {"name": "Mind Blast", "type": "Psychic", "power": 46, "accuracy": 80, "desc": "Direct psychic assault on the opponent's mind."},
    "Teleport Strike": {"name": "Teleport Strike", "type": "Psychic", "power": 22, "accuracy": 100, "desc": "Phase-shifts instantly behind target."},

    # Ice Moves
    "Ice Beam": {"name": "Ice Beam", "type": "Ice", "power": 36, "accuracy": 95, "desc": "Fires a freezing beam of sub-zero ice."},
    "Blizzard": {"name": "Blizzard", "type": "Ice", "power": 50, "accuracy": 75, "desc": "A howling blizzard that chills to the bone."},
    "Aurora Beam": {"name": "Aurora Beam", "type": "Ice", "power": 28, "accuracy": 100, "desc": "Rainbow-colored freezing beam."},
    "Ice Punch": {"name": "Ice Punch", "type": "Ice", "power": 32, "accuracy": 100, "desc": "A punch packed with freezing ice energy."},

    # Fighting Moves
    "Close Combat": {"name": "Close Combat", "type": "Fighting", "power": 48, "accuracy": 85, "desc": "Unleashes a barrage of rapid-fire strikes."},
    "Dynamic Punch": {"name": "Dynamic Punch", "type": "Fighting", "power": 45, "accuracy": 75, "desc": "Punches with full physical force."},
    "Brick Break": {"name": "Brick Break", "type": "Fighting", "power": 30, "accuracy": 100, "desc": "Hard chop that shatters barriers."},
    "Cross Chop": {"name": "Cross Chop", "type": "Fighting", "power": 40, "accuracy": 90, "desc": "Double-chop strike with high critical rate."},

    # Poison Moves
    "Sludge Bomb": {"name": "Sludge Bomb", "type": "Poison", "power": 36, "accuracy": 95, "desc": "Hurls toxic sludge at the opponent."},
    "Poison Jab": {"name": "Poison Jab", "type": "Poison", "power": 30, "accuracy": 100, "desc": "Stabs with venomous spikes."},
    "Acid Spray": {"name": "Acid Spray", "type": "Poison", "power": 24, "accuracy": 100, "desc": "Sprays caustic acid that lowers defense."},
    "Toxic": {"name": "Toxic", "type": "Poison", "power": 22, "accuracy": 100, "desc": "A potent poison that inflicts continuous damage."},

    # Ground Moves
    "Earthquake": {"name": "Earthquake", "type": "Ground", "power": 46, "accuracy": 90, "desc": "Sets off a devastating seismic quake."},
    "Earth Power": {"name": "Earth Power", "type": "Ground", "power": 36, "accuracy": 95, "desc": "Erupts geysers of dirt and magma."},
    "Dig": {"name": "Dig", "type": "Ground", "power": 28, "accuracy": 100, "desc": "Burrows underground and strikes from below."},
    "Rock Tomb": {"name": "Rock Tomb", "type": "Ground", "power": 26, "accuracy": 95, "desc": "Traps and damages the target with falling rocks."},

    # Flying Moves
    "Brave Bird": {"name": "Brave Bird", "type": "Flying", "power": 48, "accuracy": 85, "desc": "Tucks wings and dives with terrifying velocity."},
    "Drill Peck": {"name": "Drill Peck", "type": "Flying", "power": 32, "accuracy": 100, "desc": "Corkscrewing beak attack."},
    "Air Slash": {"name": "Air Slash", "type": "Flying", "power": 30, "accuracy": 95, "desc": "Slices through the air with blade-like gusts."},
    "Wing Attack": {"name": "Wing Attack", "type": "Flying", "power": 26, "accuracy": 100, "desc": "Strikes hard with broad wings."},

    # Bug Moves
    "Megahorn": {"name": "Megahorn", "type": "Bug", "power": 48, "accuracy": 80, "desc": "Rams with a gigantic, tough horn."},
    "Bug Buzz": {"name": "Bug Buzz", "type": "Bug", "power": 35, "accuracy": 95, "desc": "Vibrates wings to generate damaging sound waves."},
    "X-Scissor": {"name": "X-Scissor", "type": "Bug", "power": 30, "accuracy": 100, "desc": "Crosses scythes/claws in an X-shaped slash."},
    "Leech Life": {"name": "Leech Life", "type": "Bug", "power": 25, "accuracy": 100, "desc": "Drains opponent HP to restore health."},

    # Rock Moves
    "Rock Slide": {"name": "Rock Slide", "type": "Rock", "power": 35, "accuracy": 90, "desc": "Hurls large boulders at the opponent."},
    "Stone Edge": {"name": "Stone Edge", "type": "Rock", "power": 46, "accuracy": 80, "desc": "Stabs from below with sharp pointed stones."},
    "Ancient Power": {"name": "Ancient Power", "type": "Rock", "power": 26, "accuracy": 100, "desc": "Unearths prehistoric energy."},
    "Rock Throw": {"name": "Rock Throw", "type": "Rock", "power": 24, "accuracy": 100, "desc": "Throws a small rock to strike the foe."},

    # Ghost Moves
    "Shadow Ball": {"name": "Shadow Ball", "type": "Ghost", "power": 36, "accuracy": 95, "desc": "Hurls a shadowy black mass of spectral energy."},
    "Shadow Claw": {"name": "Shadow Claw", "type": "Ghost", "power": 28, "accuracy": 100, "desc": "Slashes with claws formed from shadows."},
    "Night Shade": {"name": "Night Shade", "type": "Ghost", "power": 25, "accuracy": 100, "desc": "Projects a horrifying spectral illusion."},
    "Confuse Ray": {"name": "Confuse Ray", "type": "Ghost", "power": 20, "accuracy": 100, "desc": "A sinister ray that disorients the target."},

    # Dragon Moves
    "Outrage": {"name": "Outrage", "type": "Dragon", "power": 50, "accuracy": 80, "desc": "Rampages with draconic fury."},
    "Dragon Claw": {"name": "Dragon Claw", "type": "Dragon", "power": 34, "accuracy": 100, "desc": "Slashes with sharp, ancient dragon claws."},
    "Dragon Breath": {"name": "Dragon Breath", "type": "Dragon", "power": 28, "accuracy": 100, "desc": "Exhales an intense burst of dragon flame."},
    "Dragon Rage": {"name": "Dragon Rage", "type": "Dragon", "power": 30, "accuracy": 100, "desc": "Strikes the target with shock waves of pure rage."},

    # Normal Moves
    "Hyper Beam": {"name": "Hyper Beam", "type": "Normal", "power": 52, "accuracy": 80, "desc": "Fires an overwhelming kinetic beam of destructive energy."},
    "Body Slam": {"name": "Body Slam", "type": "Normal", "power": 34, "accuracy": 95, "desc": "Drops full body weight onto the opponent."},
    "Quick Attack": {"name": "Quick Attack", "type": "Normal", "power": 20, "accuracy": 100, "desc": "Strikes at blinding speed with priority."},
    "Extreme Speed": {"name": "Extreme Speed", "type": "Normal", "power": 32, "accuracy": 100, "desc": "Blinding sprint strike that never misses."},
    "Slash": {"name": "Slash", "type": "Normal", "power": 28, "accuracy": 100, "desc": "High critical hit slash attack."},
    "Rest": {"name": "Rest", "type": "Normal", "power": 20, "accuracy": 100, "desc": "Restores energy and strikes back with renewed vigor."},

    # Dark / Fairy / Steel
    "Dark Pulse": {"name": "Dark Pulse", "type": "Dark", "power": 36, "accuracy": 95, "desc": "Releases a horrible aura imbued with dark thoughts."},
    "Night Slash": {"name": "Night Slash", "type": "Dark", "power": 30, "accuracy": 100, "desc": "Slashes as soon as an opportunity arises."},
    "Crunch": {"name": "Crunch", "type": "Dark", "power": 34, "accuracy": 100, "desc": "Crunches with sharp vicious fangs."},
    "Bite": {"name": "Bite", "type": "Dark", "power": 24, "accuracy": 100, "desc": "Bites down with sharp teeth."},
    "Dazzling Gleam": {"name": "Dazzling Gleam", "type": "Fairy", "power": 36, "accuracy": 95, "desc": "Dazes the target with a powerful flash of light."},
    "Moonblast": {"name": "Moonblast", "type": "Fairy", "power": 42, "accuracy": 95, "desc": "Attacks by borrowing the power of the moon."},
    "Draining Kiss": {"name": "Draining Kiss", "type": "Fairy", "power": 25, "accuracy": 100, "desc": "Drains the target's HP to restore own health."},
    "Play Rough": {"name": "Play Rough", "type": "Fairy", "power": 34, "accuracy": 90, "desc": "Plays rough with the target to inflict heavy damage."},
    "Flash Cannon": {"name": "Flash Cannon", "type": "Steel", "power": 36, "accuracy": 95, "desc": "Gathers all light energy and unleashes a cannon blast."},
    "Iron Head": {"name": "Iron Head", "type": "Steel", "power": 32, "accuracy": 100, "desc": "Slams the target with a steel-hard head."},
    "Steel Wing": {"name": "Steel Wing", "type": "Steel", "power": 28, "accuracy": 95, "desc": "Strikes hard with wings of steel."},
    "Metal Claw": {"name": "Metal Claw", "type": "Steel", "power": 24, "accuracy": 100, "desc": "Slashes with steel-hard sharp claws."}
}

# Base custom starters (with standard moves)
BASE_MONSTERS = {
    "pyrozard": {
        "id": "pyrozard",
        "name": "Pyrozard",
        "title": "The Crimson Apex",
        "type": "Fire",
        "hp": 110,
        "max_hp": 110,
        "attack": 38,
        "defense": 22,
        "speed": 32,
        "moves": ["Flamethrower", "Fire Blast", "Flame Wheel", "Air Slash"],
        "sprite": [
            r"     /\_/\       ",
            r"    ( o.o ) <炎> ",
            r"   /(  v  )\_//  ",
            r"  / /|   |\ /    ",
            r" (___/---\___)   "
        ],
        "sprite_front": [
            r"       .---.          ",
            r"      /     \   /|    ",
            r"     ( > o < ) / /    ",
            r"    / \  =  / / /     ",
            r"   /   '---' / /  ⚡  ",
            r"  /  /|     | /       ",
            r" (___/ \___/ )        "
        ]
    },
    "aquablast": {
        "id": "aquablast",
        "name": "Aquablast",
        "title": "The Tidal Fortress",
        "type": "Water",
        "hp": 130,
        "max_hp": 130,
        "attack": 28,
        "defense": 38,
        "speed": 18,
        "moves": ["Hydro Cannon", "Aqua Jet", "Water Pulse", "Surf"],
        "sprite": [
            r"     [═══]       ",
            r"    ( o.o ) [水] ",
            r"   /(  ▼  )\=    ",
            r"  / [====] \     ",
            r" (___/---\___)   "
        ],
        "sprite_front": [
            r"      /═════\         ",
            r"    o(  o.o  )o  [水] ",
            r"   / |  ===  | \      ",
            r"  |  \_______/  |     ",
            r"   \  [SHELL]  /      ",
            r"    (_________)       "
        ]
    },
    "voltmouse": {
        "id": "voltmouse",
        "name": "Voltmouse",
        "title": "The Thunder Runner",
        "type": "Electric",
        "hp": 90,
        "max_hp": 90,
        "attack": 34,
        "defense": 18,
        "speed": 45,
        "moves": ["Thunderbolt", "Volt Charge", "Spark Dash", "Quick Attack"],
        "sprite": [
            r"    (\__/)  ⚡   ",
            r"    ( •.•)       ",
            r"   / >⚡ <\      ",
            r"  (   ..   )     ",
            r"   \"\"\"\"\"\"       "
        ],
        "sprite_front": [
            r"    (\__/)    _⚡     ",
            r"    ( •.• )  / /      ",
            r"   /  ==  \ / /       ",
            r"  (  [⚡]  ) /        ",
            r"   \"\"--\"\"            "
        ]
    },
    "florasaur": {
        "id": "florasaur",
        "name": "Florasaur",
        "title": "The Ancient Sprout",
        "type": "Grass",
        "hp": 120,
        "max_hp": 120,
        "attack": 30,
        "defense": 30,
        "speed": 22,
        "moves": ["Solar Beam", "Vine Whip", "Giga Drain", "Razor Leaf"],
        "sprite": [
            r"     (✿ ✿)       ",
            r"    ( ◕‿◕ ) [草] ",
            r"   /(  ♣  )\     ",
            r"  / [====] \     ",
            r" (___/---\___)   "
        ],
        "sprite_front": [
            r"      (\___/)         ",
            r"     (  ✿.✿  )   [草] ",
            r"    /|  ===  |\       ",
            r"   ( | [LEAF]| )      ",
            r"    \ \_____/ /       ",
            r"     (_______)        "
        ]
    },
    "psycrab": {
        "id": "psycrab",
        "name": "Psycrab",
        "title": "The Astral Weaver",
        "type": "Psychic",
        "hp": 95,
        "max_hp": 95,
        "attack": 40,
        "defense": 24,
        "speed": 28,
        "moves": ["Mind Blast", "Psybeam", "Teleport Strike", "Psychic"],
        "sprite": [
            r"   (V) (o.o) (V) ",
            r"     \  =  /  🔮 ",
            r"    (  ✦✦✦  )    ",
            r"     /---\       ",
            r"    \"\"\" \"\"\"     "
        ],
        "sprite_front": [
            r"   (V)  (•.•)  (V)    ",
            r"     \   ▲   /    🔮  ",
            r"    ( [PSY-CORE] )    ",
            r"     /  ===  \        ",
            r"    / /     \ \       "
        ]
    }
}

def load_pokedex_151() -> Dict[str, Dict[str, Any]]:
    """Loads all 151 Pokémon from pokedex_151.json if available."""
    json_path = os.path.join(os.path.dirname(__file__), "pokedex_151.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

POKEDEX_151 = load_pokedex_151()

# Full monsters dictionary merging Base Monsters and Pokédex 151
MONSTERS: Dict[str, Dict[str, Any]] = {**BASE_MONSTERS, **POKEDEX_151}

# Curated lists of popular Gen 1 favorites for quick selection
FEATURED_STARTERS = [
    "poke_25",   # Pikachu
    "poke_6",    # Charizard
    "poke_9",    # Blastoise
    "poke_3",    # Venusaur
    "poke_94",   # Gengar
    "poke_150",  # Mewtwo
    "poke_149",  # Dragonite
    "poke_65",   # Alakazam
    "poke_130",  # Gyarados
    "poke_143",  # Snorlax
    "poke_133",  # Eevee
    "poke_135",  # Jolteon
    "poke_134",  # Vaporeon
    "poke_136",  # Flareon
    "poke_144",  # Articuno
    "poke_145",  # Zapdos
    "poke_146",  # Moltres
    "poke_151",  # Mew
]

def find_pokemon(query: str) -> Optional[Dict[str, Any]]:
    """Searches for a Pokémon by ID, Pokédex number (#1-151), or Name."""
    query = query.strip().lower()
    if query in MONSTERS:
        return MONSTERS[query]
    
    # Try numeric dex number
    if query.isdigit() or (query.startswith("#") and query[1:].isdigit()):
        num = int(query.lstrip("#"))
        key = f"poke_{num}"
        if key in MONSTERS:
            return MONSTERS[key]
    
    # Search by exact name match
    for m_id, m in MONSTERS.items():
        if m["name"].lower() == query:
            return m
        
    # Search by partial name match
    for m_id, m in MONSTERS.items():
        if query in m["name"].lower():
            return m
            
    return None
