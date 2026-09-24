"""
Build script to fetch and generate full 151 Pokémon dataset with:
- High-Def ANSI Half-Block Color Sprites (Front & Back)
- Official Gen 1 Stats (HP, Attack, Defense, Speed)
- Official Types
- Classic Movepools
"""

import os
import io
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

# Thematic moves by type for all 151 Pokemon
TYPE_MOVE_POOLS = {
    "Fire": ["Flamethrower", "Fire Blast", "Flame Wheel", "Fire Spin"],
    "Water": ["Hydro Cannon", "Aqua Jet", "Water Pulse", "Surf"],
    "Grass": ["Solar Beam", "Vine Whip", "Giga Drain", "Razor Leaf"],
    "Electric": ["Thunderbolt", "Volt Charge", "Spark Dash", "Thunder Wave"],
    "Psychic": ["Mind Blast", "Psybeam", "Teleport Strike", "Psychic"],
    "Ice": ["Blizzard", "Ice Beam", "Aurora Beam", "Ice Punch"],
    "Fighting": ["Close Combat", "Dynamic Punch", "Brick Break", "Cross Chop"],
    "Poison": ["Sludge Bomb", "Poison Jab", "Acid Spray", "Toxic"],
    "Ground": ["Earthquake", "Earth Power", "Dig", "Rock Tomb"],
    "Flying": ["Brave Bird", "Drill Peck", "Air Slash", "Wing Attack"],
    "Bug": ["Megahorn", "Bug Buzz", "X-Scissor", "Leech Life"],
    "Rock": ["Rock Slide", "Stone Edge", "Ancient Power", "Rock Throw"],
    "Ghost": ["Shadow Ball", "Shadow Claw", "Night Shade", "Confuse Ray"],
    "Dragon": ["Outrage", "Dragon Claw", "Dragon Breath", "Dragon Rage"],
    "Steel": ["Flash Cannon", "Iron Head", "Steel Wing", "Metal Claw"],
    "Normal": ["Hyper Beam", "Body Slam", "Quick Attack", "Slash"],
    "Fairy": ["Dazzling Gleam", "Moonblast", "Draining Kiss", "Play Rough"],
    "Dark": ["Dark Pulse", "Night Slash", "Crunch", "Bite"]
}

SPECIAL_SIGNATURE_MOVES = {
    "pikachu": ["Thunderbolt", "Volt Charge", "Spark Dash", "Quick Attack"],
    "raichu": ["Thunderbolt", "Volt Charge", "Hyper Beam", "Quick Attack"],
    "charizard": ["Fire Blast", "Flamethrower", "Dragon Claw", "Air Slash"],
    "blastoise": ["Hydro Cannon", "Hydro Pump", "Ice Beam", "Aqua Jet"],
    "venusaur": ["Solar Beam", "Giga Drain", "Sludge Bomb", "Razor Leaf"],
    "mewtwo": ["Mind Blast", "Psybeam", "Shadow Ball", "Hyper Beam"],
    "mew": ["Mind Blast", "Solar Beam", "Flamethrower", "Psychic"],
    "gengar": ["Shadow Ball", "Night Shade", "Sludge Bomb", "Shadow Claw"],
    "dragonite": ["Outrage", "Dragon Claw", "Hyper Beam", "Thunderbolt"],
    "alakazam": ["Mind Blast", "Psybeam", "Teleport Strike", "Shadow Ball"],
    "gyarados": ["Hydro Cannon", "Outrage", "Hyper Beam", "Aqua Jet"],
    "snorlax": ["Body Slam", "Hyper Beam", "Earthquake", "Rest"],
    "lapras": ["Ice Beam", "Hydro Cannon", "Blizzard", "Body Slam"],
    "articuno": ["Blizzard", "Ice Beam", "Brave Bird", "Air Slash"],
    "zapdos": ["Thunderbolt", "Volt Charge", "Drill Peck", "Brave Bird"],
    "moltres": ["Fire Blast", "Flamethrower", "Air Slash", "Brave Bird"],
    "machamp": ["Close Combat", "Dynamic Punch", "Brick Break", "Cross Chop"],
    "arcanine": ["Flamethrower", "Fire Blast", "Extreme Speed", "Bite"],
    "eevee": ["Quick Attack", "Body Slam", "Bite", "Slash"],
    "vaporeon": ["Hydro Cannon", "Water Pulse", "Ice Beam", "Surf"],
    "jolteon": ["Thunderbolt", "Volt Charge", "Spark Dash", "Quick Attack"],
    "flareon": ["Flamethrower", "Fire Blast", "Flame Wheel", "Quick Attack"]
}


def image_to_half_block_ansi(img_bytes: bytes, max_w: int = 16, max_h: int = 14) -> list:
    """Converts image PNG bytes to high-definition ANSI half-block characters."""
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        
        w, h = img.size
        scale = min(max_w / w, max_h / h)
        new_w = max(1, int(w * scale))
        new_h = max(2, int(h * scale))
        if new_h % 2 != 0:
            new_h += 1
        
        img = img.resize((new_w, new_h), Image.Resampling.NEAREST)
        
        lines = []
        for y in range(0, new_h, 2):
            line_parts = []
            for x in range(new_w):
                r1, g1, b1, a1 = img.getpixel((x, y))
                r2, g2, b2, a2 = img.getpixel((x, y + 1)) if y + 1 < new_h else (0, 0, 0, 0)
                
                top_vis = a1 > 80
                bot_vis = a2 > 80
                
                if top_vis and bot_vis:
                    line_parts.append(f"\033[38;2;{r1};{g1};{b1}m\033[48;2;{r2};{g2};{b2}m▀\033[0m")
                elif top_vis and not bot_vis:
                    line_parts.append(f"\033[38;2;{r1};{g1};{b1}m▀\033[0m")
                elif not top_vis and bot_vis:
                    line_parts.append(f"\033[38;2;{r2};{g2};{b2}m▄\033[0m")
                else:
                    line_parts.append(" ")
            lines.append("".join(line_parts))
        return lines
    except Exception as e:
        return [f"[Sprite Error: {e}]"]


def fetch_pokemon_data(p_id: int) -> dict:
    """Fetches details and sprites for a single Pokemon."""
    api_url = f"https://pokeapi.co/api/v2/pokemon/{p_id}"
    req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    name = data["name"].capitalize()
    types = [t["type"]["name"].capitalize() for t in data["types"]]
    primary_type = types[0]
    
    stats_dict = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
    hp = stats_dict.get("hp", 80)
    attack = stats_dict.get("attack", 70)
    defense = stats_dict.get("defense", 65)
    speed = stats_dict.get("speed", 60)
    
    # Scale stats to match balanced game range
    game_hp = max(60, min(180, int(hp * 1.1)))
    game_atk = max(15, min(55, int(attack * 0.38)))
    game_def = max(12, min(50, int(defense * 0.35)))
    game_spd = max(10, min(60, int(speed * 0.42)))
    
    # Fetch Front Sprite
    front_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{p_id}.png"
    req_f = urllib.request.Request(front_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req_f, timeout=10) as resp_f:
        front_bytes = resp_f.read()
    sprite_front = image_to_half_block_ansi(front_bytes, max_w=18, max_h=14)
    
    # Fetch Back Sprite
    back_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/{p_id}.png"
    sprite_back = sprite_front
    try:
        req_b = urllib.request.Request(back_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req_b, timeout=10) as resp_b:
            back_bytes = resp_b.read()
        sprite_back = image_to_half_block_ansi(back_bytes, max_w=16, max_h=12)
    except Exception:
        pass
    
    # Select moves
    slug = data["name"].lower()
    if slug in SPECIAL_SIGNATURE_MOVES:
        moves = SPECIAL_SIGNATURE_MOVES[slug]
    else:
        moves = TYPE_MOVE_POOLS.get(primary_type, TYPE_MOVE_POOLS["Normal"])
    
    return {
        "id": f"poke_{p_id}",
        "dex_num": p_id,
        "name": name,
        "title": f"The #{p_id:03d} Pokémon",
        "type": primary_type,
        "types": types,
        "hp": game_hp,
        "max_hp": game_hp,
        "attack": game_atk,
        "defense": game_def,
        "speed": game_spd,
        "moves": moves,
        "sprite": sprite_back,
        "sprite_front": sprite_front
    }


def main():
    print("🚀 Fetching all 151 Pokémon from PokéAPI and generating ANSI Half-Block Color Sprites...")
    results = {}
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(fetch_pokemon_data, i): i for i in range(1, 152)}
        for future in as_completed(futures):
            p_id = futures[future]
            try:
                p_data = future.result()
                results[p_data["id"]] = p_data
                print(f"  [✓] #{p_id:03d} {p_data['name']} ({p_data['type']})")
            except Exception as e:
                print(f"  [✗] Failed #{p_id}: {e}")
    
    # Sort by dex_num
    sorted_pokemon = dict(sorted(results.items(), key=lambda item: item[1]["dex_num"]))
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "pokedex_151.json")
    out_path = os.path.abspath(out_path)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sorted_pokemon, f, indent=2, ensure_ascii=False)
    
    print(f"\n✨ Successfully compiled {len(sorted_pokemon)} Pokémon into {out_path}!")


if __name__ == "__main__":
    main()
