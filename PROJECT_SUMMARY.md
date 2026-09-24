# ⚡ Doushi Battle (doushi-mon) — Project & Strategy Summary ⚡

## 🎯 Origin & Strategy
- **Goal:** Create a fun, viral, developer-friendly open-source showcase to promote [Doushi.ai](https://doushi.ai) on Reddit and developer communities without coming across as spammy or corporate.
- **Why Pokémon/Monsters:** Everyone understands the rules instantly; it showcases Doushi's core prompt-to-model speed, real-time ML inference (14ms latency), and explainable AI insights in a memorable way.
- **Target Communities:** `r/Python`, `r/commandline`, `r/pokemon`, `r/SideProject`, `r/unixporn`, `r/gamedev`.

---

## 🏗️ Architecture & Modules (`doushi-battle/`)

| File | Purpose |
| :--- | :--- |
| **`pokedex_151.json`** | Complete dataset containing all 151 original Pokémon with High-Def TrueColor ANSI half-block pixel sprites (Front & Back), official base stats, dual typing, and classic movepools. |
| **`monsters.py`** | 151 Pokémon + 6 custom monster archetypes, 18-type combat effectiveness matrix (with Cyber type expansion), and comprehensive move library. |
| **`doushi_ai.py`** | Autonomous ML combat scoring engine (predicts real-time win odds, multi-feature importance, and AI opponent tactics with ~14ms latency). |
| **`renderer.py`** | Authentic Pokémon Red/Blue/Gold GameBoy battle layout, ANSI TrueColor sprite rendering, responsive 70/80-column terminal clamping, and unified typewriter dialogue box with `▼ [Press any key]` progression. |
| **`sound.py`** | Zero-dependency 8-bit chiptune audio engine: synthesizes classic GameBoy sound effects (`blip`, `hit`, `crit`, `scan`, `victory`, `faint`) and a 140 BPM background battle theme. |
| **`game.py`** | Full turn-based battle loop with turn priority, animated HP drains, typewriter combat logs, and victory/defeat telemetry. |
| **`main.py`** | CLI entrypoint featuring Quick Battle (with Random Encounter & Custom Pick), The Doushi Gauntlet (4-stage boss challenge), Interactive 151 Pokédex Archive Browser & Search, and About Doushi.ai. |
| **`scripts/build_pokedex.py`** | Multi-threaded generation script to fetch official sprites from PokéAPI and compile ANSI half-block characters and stats. |

---

## 🕹️ How to Run

```bash
cd doushi-battle
python3 main.py
```

---

## 🎬 Reddit Post & Launch Playbook

### 1. The Video Demo (20-30 seconds)
Record a crisp terminal screencast (using macOS screen recording or `vhs`) showing:
1. Launching `python3 main.py` and picking Pikachu, Charizard, Gengar, or searching any of the 151 Pokémon.
2. The opening typewriter intro: *"Wild CHARIZARD appeared!"* with background 8-bit music.
3. The **Doushi AI Win Odds HUD** recalculating live at ~14ms.
4. Landing a critical hit with the HP drain animation and sound effects.

### 2. Suggested Reddit Post Title:
> *"I built an authentic retro GameBoy-style Pokémon battle simulator with all 151 Pokémon in Python that runs in your terminal—powered by real-time ML odds [Open Source]"*

### 3. Suggested First Comment (The Value/Recipe Hook):
> *"Hey everyone! Built this in Python with `rich` and pure waveform synthesis for the 8-bit sounds, with high-def ANSI half-block pixel art for all original 151 Pokémon. Behind the scenes, the combat odds and AI moves are powered by an ML model I trained on match data using **[Doushi.ai](https://doushi.ai)** (a tabular AutoML builder I've been developing). The code is 100% open source here: [GitHub Link]. Would love feedback on the terminal animations!"*
