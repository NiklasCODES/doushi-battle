#!/usr/bin/env bash
# ==============================================================================
#  ⚡ Retro Terminal Pokémon Battle Simulator — Quick Launcher ⚡
#  Play instantly: curl -sSL https://doushi.ai/battle | bash
# ==============================================================================

set -e

TMP_DIR="/tmp/doushi-battle-game"
REPO_URL="https://github.com/niklascodes/doushi-battle.git"

echo "⚡ Launching Retro Terminal Pokémon Battle Simulator..."

# Ensure Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required to run this game. Please install Python 3 and try again."
    exit 1
fi

# Clone or pull latest in /tmp
if [ -d "$TMP_DIR/.git" ]; then
    cd "$TMP_DIR"
    git pull -q origin main 2>/dev/null || true
else
    rm -rf "$TMP_DIR"
    git clone -q --depth=1 "$REPO_URL" "$TMP_DIR"
    cd "$TMP_DIR"
fi

# Ensure required libraries are installed
python3 -c "import rich, PIL" 2>/dev/null || {
    echo "📦 Installing minimal dependencies (rich, pillow)..."
    pip3 install -q rich Pillow 2>/dev/null || pip install -q rich Pillow
}

# Reconnect stdin to the interactive terminal (fixes EOFError when piped via curl | bash)
if [ ! -t 0 ] && [ -e /dev/tty ]; then
    exec < /dev/tty
fi

# Run the game
python3 main.py
