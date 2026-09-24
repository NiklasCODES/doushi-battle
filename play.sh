#!/usr/bin/env bash
# ==============================================================================
#  ⚡ Retro Terminal Pokémon Battle Simulator — Quick Launcher ⚡
#  Play instantly: curl -sSL https://doushi.ai/battle | bash
# ==============================================================================

set -e

TMP_DIR="/tmp/doushi-battle-game"
REPO_URL="https://github.com/niklascodes/doushi-battle.git"

# Reconnect standard input to the interactive user terminal immediately
if [ ! -t 0 ] && [ -e /dev/tty ]; then
    exec < /dev/tty
fi

printf "\033[1;35m⚡ Launching Retro Terminal Pokémon Battle Simulator...\033[0m\n"

# 1. Check Python 3
if ! command -v python3 &> /dev/null; then
    printf "\033[1;31m❌ Python 3 is required. Please install Python 3 and try again.\033[0m\n"
    exit 1
fi

# 2. Clone or update repository
if [ -d "$TMP_DIR/.git" ]; then
    cd "$TMP_DIR"
    git pull --quiet --ff-only 2>/dev/null || true
else
    rm -rf "$TMP_DIR"
    git clone --quiet --depth=1 "$REPO_URL" "$TMP_DIR"
    cd "$TMP_DIR"
fi

# 3. Check / Install dependencies
python3 -c "import rich, PIL" 2>/dev/null || {
    printf "\033[1;36m📦 Installing terminal dependencies (rich, pillow)...\033[0m\n"
    pip3 install --quiet --upgrade rich Pillow 2>/dev/null || pip install --quiet rich Pillow
}

# 4. Launch Game
python3 main.py
