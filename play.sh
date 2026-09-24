#!/usr/bin/env bash
# ==============================================================================
#  ⚡ Retro Terminal Pokémon Battle Simulator — Quick Launcher ⚡
#  Play instantly: curl -sSL https://doushi.ai/battle | bash
# ==============================================================================

set -e

TMP_DIR="/tmp/doushi-battle-game"
VENV_DIR="/tmp/doushi-battle-venv"
REPO_URL="https://github.com/niklascodes/doushi-battle.git"

printf "\033[1;35m⚡ Launching Retro Terminal Pokémon Battle Simulator...\033[0m\n"

# 1. Detect Python 3 interpreter
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null && python -c 'import sys; sys.exit(0 if sys.version_info.major >= 3 else 1)' 2>/dev/null; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    printf "\033[1;31m❌ Python 3 was not detected on your system.\033[0m\n"
    printf "Install Python 3 to play:\n"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        printf "  • macOS: brew install python3\n"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        printf "  • Debian/Ubuntu: sudo apt install python3 python3-venv python3-pip\n"
        printf "  • Fedora:        sudo dnf install python3\n"
        printf "  • Arch Linux:    sudo pacman -S python\n"
    fi
    exit 1
fi

# 2. Clone or update repository in /tmp
if [ -d "$TMP_DIR/.git" ]; then
    cd "$TMP_DIR"
    git fetch --depth=1 origin main 2>/dev/null && git reset --hard origin/main 2>/dev/null || true
else
    rm -rf "$TMP_DIR"
    git clone --quiet --depth=1 "$REPO_URL" "$TMP_DIR"
    cd "$TMP_DIR"
fi

# 3. Create / activate isolated virtual environment (handles missing pip & PEP 668)
if [ ! -d "$VENV_DIR" ]; then
    "$PYTHON_CMD" -m venv "$VENV_DIR" 2>/dev/null || true
fi

if [ -f "$VENV_DIR/bin/python" ]; then
    VENV_PY="$VENV_DIR/bin/python"
    VENV_PIP="$VENV_DIR/bin/pip"
else
    VENV_PY="$PYTHON_CMD"
    VENV_PIP="pip3"
fi

# 4. Check & install minimal dependencies in venv
"$VENV_PY" -c "import rich, PIL" 2>/dev/null || {
    printf "\033[1;36m📦 Setting up terminal dependencies (rich, pillow)...\033[0m\n"
    "$VENV_PIP" install --quiet --upgrade rich Pillow 2>/dev/null || "$PYTHON_CMD" -m pip install --quiet rich Pillow 2>/dev/null || true
}

# 5. Launch Game connected to user terminal tty
if [ -e /dev/tty ]; then
    "$VENV_PY" main.py < /dev/tty
else
    "$VENV_PY" main.py
fi
