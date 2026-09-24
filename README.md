# ⚡ Retro Terminal Pokémon Battle Simulator ⚡

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Terminal UI](https://img.shields.io/badge/Terminal_UI-Rich-magenta.svg)](https://github.com/Textualize/rich)
[![AutoML Ready](https://img.shields.io/badge/ML_Modeling-Doushi.ai-cyan.svg)](https://doushi.ai)

An authentic retro turn-based Pokémon battle simulator running directly in your terminal. Features **all 151 original Generation 1 Pokémon** rendered in high-definition 24-bit TrueColor ANSI half-block pixel art, procedural 8-bit audio sound synthesis and dynamic combat analytics.

<p align="center">
  <img src="assets/demo.gif" alt="Terminal Pokémon Battle Demo" width="750">
</p>

---

## 🎮 Highlights

- 🎨 **All 151 Original Pokémon Sprites:** High-definition ANSI half-block pixel art (`▀`/`▄`) for both **Front** and **Back** sprites.
- 🎵 **Pure Waveform 8-Bit Audio:** Synthesizes retro 8-bit sound effects (`blip`, `hit`, `crit`, `scan`, `victory`, `faint`) and a 140 BPM battle theme using pure mathematical audio synthesis.
- 📊 **Real-Time Win Probability HUD:** Dynamically computes turn-by-turn win odds based on HP ratios, speed initiative differentials, and full 18-type effectiveness charts.
- 📖 **Interactive 151 Pokédex Archive:** Search any Pokémon by name or Pokédex number (`#1`–`#151`) to inspect full base stats, types, movepools, and sprites.
- ⚔️ **Game Modes:**
  - **Quick Battle:** Battle random wild encounters or choose specific matchups.
  - **Champion Gauntlet:** 4-stage boss challenge scaling against iconic masters and the final Legendary Boss Mewtwo.
- 🤖 **AutoML & Telemetry Ready:** Includes a dataset generator to simulate matches and train real Machine Learning models using **[Doushi.ai](https://doushi.ai)**.

---

## 🚀 Quick Start

### ⚡ Play Instantly in 1 Command (`curl`):

```bash
curl -sSL https://doushi.ai/battle | bash
```

*Or directly from GitHub:*
```bash
curl -sSL https://raw.githubusercontent.com/niklascodes/doushi-battle/main/play.sh | bash
```

---

### 📦 Or Clone & Run Locally:

```bash
git clone https://github.com/niklascodes/doushi-battle.git
cd doushi-battle

# Install dependencies (only rich & pillow)
pip install -r requirements.txt

# Launch the game
python3 main.py
```

### 2. Or Install as a CLI Package

```bash
pip install .
pokemon-battle
```

---

## 🕹️ Controls & Combat System

| Key | Action |
| :---: | :--- |
| `1` – `4` | Select move from your active movepool |
| `Q` | Attempt to run / flee battle |
| `Any Key` / `Enter` | Progress typewriter dialogue box |

### Tactical Mechanics:
- **Elemental Advantage:** Exploiting type weaknesses deals **1.5× – 2.0×** damage.
- **Speed Initiative:** Higher speed guarantees first-strike advantage; priority moves (e.g., *Aqua Jet*, *Quick Attack*) bypass standard speed brackets.
- **Tactical Scan:** Analyzes opponent stats to boost Attack and Critical Strike rate for 3 turns.
- **Drain Moves:** *Giga Drain*, *Draining Kiss*, and *Byte Drain* restore 40% of damage dealt back to your HP.

---

## 🤖 How to Train Your Own ML Combat Predictor with Doushi.ai

You can use the included dataset generator and **[Doushi.ai](https://doushi.ai)** to train a real tabular Machine Learning model that predicts match outcomes:

### Step 1: Generate Match Dataset
Simulate 10,000 matches across the 151 Pokémon roster to generate `pokemon_battles.csv`:

```bash
python scripts/generate_training_data.py --samples 10000
```

### Step 2: Install Doushi CLI & Login

```bash
pip install doushi-cli
dsh login
```

### Step 3: Train an AutoML Model in 1 Line
Upload the dataset and tell Doushi what to predict in plain English:

```bash
dsh projects create \
  --name "Pokemon Win Predictor" \
  --file "pokemon_battles.csv" \
  --target winner \
  --prompt "Predict the winning pokemon based on stats, elemental types, and HP ratios"
```

Doushi will automatically clean the data, select the best model (LightGBM, XGBoost, CatBoost), evaluate feature importance, and deploy a live REST API endpoint.

---

## 🏗️ Repository Architecture

```text
doushi-battle/
├── main.py                     # CLI entrypoint & interactive menu system
├── renderer.py                 # Terminal layout, ANSI sprite parsing & dialogue frames
├── game.py                     # Turn-based battle loop, HP drain animations & telemetry
├── monsters.py                 # Full 18-type matrix, movepool library & monster database
├── doushi_ai.py                # Combat probability engine & AI opponent tactics
├── sound.py                    # 8-bit chiptune audio & waveform synthesizer
├── pokedex_151.json            # 151 Pokémon sprites, base stats & dual typing
├── scripts/
│   ├── build_pokedex.py        # PokéAPI sprite downloader & ANSI half-block converter
│   └── generate_training_data.py # 10k match simulation dataset generator
├── requirements.txt            # Minimal dependencies (rich, Pillow)
├── pyproject.toml              # Package configuration
└── README.md
```

---

## 📜 Credits & Acknowledgments

This project is built upon open-source tooling and datasets:

- **[PokeAPI](https://pokeapi.co/) & [PokeAPI/sprites](https://github.com/PokeAPI/sprites)** — For the original Pokémon Gen 1 pixel art sprites and base stats data.
- **[Rich](https://github.com/Textualize/rich)** by Will McGugan — For the terminal UI engine, tables, panels, and ANSI TrueColor parsing.
- **[Pillow (PIL)](https://github.com/python-pillow/Pillow)** — For image loading and pixel color sampling during ANSI half-block conversion.
- **[Pokemon ASCII Art Dataset](https://gist.github.com/numbpill3d/2622233)** / **[vsoch/pokemon](https://github.com/vsoch/pokemon)** — For ASCII art inspiration.
- **[Doushi.ai](https://doushi.ai)** — Tabular AutoML builder for training predictive ML models from plain text prompts.

---

## ⚖️ Disclaimer & License

Pokémon and Pokémon character names are trademarks of Nintendo, Creatures Inc., and Game Freak. This is an unofficial, non-commercial open-source educational and fan project.

Code is licensed under the [MIT License](LICENSE).
