"""
Retro Terminal Battle Renderer for Pokémon Battle Simulator.
Faithfully recreates classic Pokémon battle layouts in your terminal:
- Top-Left: Opponent Status Bracket (Name, Level, HP meter)
- Top-Right: Opponent Front Sprite (ANSI Color Pixel Art / Retro ASCII)
- Bottom-Left: Player Back Sprite (ANSI Color Pixel Art / Retro ASCII)
- Bottom-Right: Player Status Bracket (Name, Level, HP meter, HP count)
- Bottom: UNIFIED Dialogue Frame with typewritten text,
  Live Win Probability HUD, and classic 'Press Any Key ▼' progression.
"""

import os
import sys
import time
import shutil
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box

from monsters import MOVES, MONSTERS
from sound import play_sound

console = Console()

TARGET_WIDTH = 70

TYPE_COLORS = {
    "Fire": "bright_red",
    "Water": "bright_blue",
    "Grass": "bright_green",
    "Electric": "bright_yellow",
    "Psychic": "bright_magenta",
    "Ice": "bright_cyan",
    "Fighting": "red",
    "Poison": "magenta",
    "Ground": "yellow",
    "Flying": "bright_cyan",
    "Bug": "green",
    "Rock": "dim yellow",
    "Ghost": "bright_magenta",
    "Dragon": "bold magenta",
    "Steel": "bright_white",
    "Dark": "dim white",
    "Fairy": "bright_magenta",
    "Normal": "white",
    "Cyber": "bright_cyan"
}


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def get_terminal_width() -> int:
    try:
        w = shutil.get_terminal_size((70, 24)).columns
        return min(TARGET_WIDTH, max(56, w - 2))
    except Exception:
        return 70


def wait_for_key() -> str:
    """Reads a single keypress instantly and plays a retro blip."""
    ch = ""
    try:
        if os.name == "nt":
            import msvcrt
            ch = msvcrt.getch().decode("utf-8", errors="ignore")
        else:
            import tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        try:
            ch = input()
        except Exception:
            ch = ""

    play_sound("blip")
    return ch


def print_banner():
    """Main menu title banner."""
    w = get_terminal_width()
    banner = r"""
[bold bright_magenta]  ___  ___  _   _ ___ _   _ ___   ____    _  _____ _____ _     _____ [/]
[bold bright_magenta] |   \/ _ \| | | / __| | | |_ _| | __ )  / \|_   _|_   _| |   | ____|[/]
[bold bright_cyan] | |) | | | | | | \__ \ |_| || |  |  _ \ / _ \ | |   | | | |   |  _|  [/]
[bold bright_cyan] |___/\___/ \___/|___/\___/|___| |____//_/ \_\|_|   |_| |___|_|____| [/]
[bold white on dark_blue] ⚡ RETRO TERMINAL POKÉMON BATTLE SIMULATOR (151 POKÉMON) ⚡ [/]
"""
    console.print(Align.center(banner, width=w))


def get_hp_meter(current: int, max_val: int, width: int = 12) -> Text:
    ratio = max(0.0, min(1.0, current / max(1, max_val)))
    filled = int(ratio * width)
    empty = width - filled

    if ratio > 0.5:
        bar_color = "bright_green"
    elif ratio > 0.2:
        bar_color = "bright_yellow"
    else:
        bar_color = "bold bright_red"

    txt = Text()
    txt.append("HP: ", style="bold white")
    txt.append("█" * filled, style=bar_color)
    txt.append("░" * empty, style="dim white")
    return txt


def get_odds_bar(win_prob: float, width: int = 10) -> Text:
    pct = int(win_prob * 100)
    filled = int(win_prob * width)
    empty = width - filled
    color = "bold bright_green" if win_prob >= 0.60 else ("bold bright_yellow" if win_prob >= 0.40 else "bold bright_red")

    txt = Text()
    txt.append("█" * filled, style=color)
    txt.append("░" * empty, style="dim white")
    txt.append(f" {pct}%", style=color)
    return txt


def format_sprite_text(sprite_lines: List[str], hit: bool = False, fallback_style: str = "white") -> Text:
    """Formats either ANSI TrueColor pixel art or ASCII line art into a Rich Text block."""
    txt = Text()
    for i, line in enumerate(sprite_lines):
        if "\033[" in line:
            line_txt = Text.from_ansi(line)
            if hit:
                line_txt.stylize("on red")
            txt.append_text(line_txt)
        else:
            style = "bold white on red" if hit else fallback_style
            txt.append(line, style=style)
        if i < len(sprite_lines) - 1:
            txt.append("\n")
    return txt


def render_battle_screen(
    player: Dict[str, Any],
    opponent: Dict[str, Any],
    win_prob: float,
    dialog_text: str = "",
    waiting_for_input: bool = False,
    hit_target: Optional[str] = None,
    custom_player_hp: Optional[int] = None,
    custom_opp_hp: Optional[int] = None,
    move_menu_active: bool = False,
    latency_ms: Optional[float] = None
):
    clear_terminal()
    w = get_terminal_width()

    p_hp = player["hp"] if custom_player_hp is None else custom_player_hp
    o_hp = opponent["hp"] if custom_opp_hp is None else custom_opp_hp

    opp_type_col = TYPE_COLORS.get(opponent["type"], "white")
    p_type_col = TYPE_COLORS.get(player["type"], "white")

    # ==================== TOP ROW: Opponent Status & Sprite ====================
    top_grid = Table.grid(expand=True, padding=(0, 1))
    top_grid.add_column(ratio=1)
    top_grid.add_column(ratio=1, justify="right")

    o_hit = " 💥" if hit_target == "opponent" else ""
    opp_box_content = Table.grid()
    opp_box_content.add_row(Text.assemble(
        (f"{opponent['name'].upper()}", "bold white"),
        (f" :L50", "bold yellow"),
        (f" [{opponent['type']}]", f"bold {opp_type_col}"),
        (o_hit, "bold red")
    ))
    opp_box_content.add_row(get_hp_meter(o_hp, opponent["max_hp"], 12))

    opp_status_panel = Panel(
        opp_box_content,
        border_style="bold red" if hit_target == "opponent" else "dim white",
        box=box.HORIZONTALS,
        padding=(0, 1)
    )

    opp_sprite_lines = opponent.get("sprite_front", opponent["sprite"])
    opp_sprite_text = format_sprite_text(opp_sprite_lines, hit=(hit_target == "opponent"), fallback_style=f"bold {opp_type_col}")

    top_grid.add_row(opp_status_panel, opp_sprite_text)

    # ==================== BOTTOM ROW: Player Sprite & Status ====================
    bot_grid = Table.grid(expand=True, padding=(0, 1))
    bot_grid.add_column(ratio=1)
    bot_grid.add_column(ratio=1, justify="right")

    p_sprite_lines = player.get("sprite", player.get("sprite_front", []))
    p_sprite_text = format_sprite_text(p_sprite_lines, hit=(hit_target == "player"), fallback_style=f"bold {p_type_col}")

    p_hit = " 💥" if hit_target == "player" else ""
    p_box_content = Table.grid()
    p_box_content.add_row(Text.assemble(
        (f"{player['name'].upper()}", "bold white"),
        (f" :L50", "bold yellow"),
        (f" [{player['type']}]", f"bold {p_type_col}"),
        (p_hit, "bold red")
    ))
    p_box_content.add_row(get_hp_meter(p_hp, player["max_hp"], 12))
    p_box_content.add_row(Text(f"{max(0, p_hp):>12}/{player['max_hp']}", style="bold white"))

    p_status_panel = Panel(
        p_box_content,
        border_style="bold red" if hit_target == "player" else "dim white",
        box=box.HORIZONTALS,
        padding=(0, 1)
    )

    bot_grid.add_row(p_sprite_text, p_status_panel)

    # Combine Arena Frame
    arena_layout = Table.grid(expand=True)
    arena_layout.add_column(ratio=1)
    arena_layout.add_row(top_grid)
    arena_layout.add_row(Text(""))
    arena_layout.add_row(bot_grid)

    arena_panel = Panel(
        arena_layout,
        border_style="dim cyan",
        box=box.DOUBLE,
        width=w
    )
    console.print(Align.center(arena_panel, width=w))

    # ==================== UNIFIED DIALOGUE & COMBAT PREDICTOR BOX ====================
    box_table = Table.grid(expand=True)
    box_table.add_column(ratio=1)

    # 1. Combat Odds Header
    telemetry_header = Text.assemble(
        ("📊 WIN PREDICTION: ", "bold cyan"),
        get_odds_bar(win_prob, 10),
        (" ODDS ", "bold cyan"),
        ("│ ⚡ Tactical Analysis", "dim white")
    )
    box_table.add_row(telemetry_header)
    box_table.add_row(Text("─" * (w - 6), style="dim magenta"))

    # 2. Dialogue or Move Grid
    if move_menu_active:
        grid = Table.grid(padding=(0, 2), expand=True)
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)

        move_buttons = []
        for i, move_name in enumerate(player["moves"], 1):
            move = MOVES.get(move_name, {"name": move_name, "type": "Normal", "power": 20})
            t_col = TYPE_COLORS.get(move["type"], "white")
            btn = Text.assemble(
                (f"▶ [{i}] ", "bold yellow"),
                (f"{move['name']:<13}", "bold white"),
                (f"[{move['type']}]", f"{t_col}")
            )
            move_buttons.append(btn)

        if len(move_buttons) >= 4:
            grid.add_row(move_buttons[0], move_buttons[1])
            grid.add_row(move_buttons[2], move_buttons[3])
        elif len(move_buttons) == 2:
            grid.add_row(move_buttons[0], move_buttons[1])

        prompt_line = Table.grid(expand=True)
        prompt_line.add_column(ratio=2)
        prompt_line.add_column(ratio=1, justify="right")
        prompt_line.add_row(
            Text(f"What will {player['name'].upper()} do?", style="bold white"),
            Text("[1-4 / Q to run]", style="bold yellow")
        )
        box_table.add_row(prompt_line)
        box_table.add_row(grid)

    else:
        # Standard dialogue mode
        dialogue_lines = Table.grid(expand=True)
        dialogue_lines.add_column(ratio=1)
        dialogue_lines.add_row(Text(f" {dialog_text}", style="bold white"))

        if waiting_for_input:
            prompt_line = Table.grid(expand=True)
            prompt_line.add_column(ratio=1, justify="right")
            prompt_line.add_row(Text("▼ [Press any key] ", style="bold yellow blink"))
            dialogue_lines.add_row(prompt_line)
        else:
            dialogue_lines.add_row(Text(" "))

        box_table.add_row(dialogue_lines)

    dialogue_panel = Panel(
        box_table,
        border_style="bold bright_cyan",
        box=box.ROUNDED,
        width=w,
        padding=(0, 1)
    )
    console.print(Align.center(dialogue_panel, width=w))


def typewriter_dialogue(
    player: Dict[str, Any],
    opponent: Dict[str, Any],
    win_prob: float,
    text: str,
    latency_ms: Optional[float] = None,
    sfx: Optional[str] = "blip",
    speed: float = 0.015,
    press_to_continue: bool = True
):
    """Renders retro typewriter dialogue letter by letter, then waits for a keypress."""
    if sfx:
        play_sound(sfx)

    for i in range(1, len(text) + 1):
        partial = text[:i]
        render_battle_screen(
            player=player,
            opponent=opponent,
            win_prob=win_prob,
            dialog_text=partial,
            waiting_for_input=False
        )
        time.sleep(speed)

    if press_to_continue:
        render_battle_screen(
            player=player,
            opponent=opponent,
            win_prob=win_prob,
            dialog_text=text,
            waiting_for_input=True
        )
        wait_for_key()


play_typewriter_message = typewriter_dialogue


def animate_hp_drain(
    player: Dict[str, Any],
    opponent: Dict[str, Any],
    win_prob: float,
    damage_text: str = "",
    target: str = "opponent",
    old_hp: Optional[int] = None,
    new_hp: Optional[int] = None,
    start_hp: Optional[int] = None,
    end_hp: Optional[int] = None,
    latency_ms: Optional[float] = None
):
    """Gradually drains the target's HP bar with flashing hit indicators."""
    s_hp = old_hp if old_hp is not None else (start_hp or 100)
    e_hp = new_hp if new_hp is not None else (end_hp or 0)
    steps = 8
    diff = s_hp - e_hp
    play_sound("hit")

    for step in range(steps + 1):
        curr_hp = int(s_hp - (diff * (step / steps)))
        hit_target = target if (step % 2 == 1 and step < steps) else None

        if target == "opponent":
            render_battle_screen(
                player=player,
                opponent=opponent,
                win_prob=win_prob,
                dialog_text=damage_text,
                hit_target=hit_target,
                custom_opp_hp=curr_hp
            )
        else:
            render_battle_screen(
                player=player,
                opponent=opponent,
                win_prob=win_prob,
                dialog_text=damage_text,
                hit_target=hit_target,
                custom_player_hp=curr_hp
            )
        time.sleep(0.04)


def display_match_result(
    player: Dict[str, Any],
    opponent: Dict[str, Any],
    victory: bool,
    turns: int,
    start_time: float,
    mvp_move: str
):
    """Displays victory or defeat fanfare with match summary."""
    clear_terminal()
    print_banner()
    w = get_terminal_width()

    elapsed = round(time.time() - start_time, 1)

    if victory:
        play_sound("victory")
        title = "[bold bright_green]🏆 VICTORY ACHIEVED! 🏆[/]"
        border_col = "bright_green"
        msg = f"You and {player['name'].upper()} defeated {opponent['name'].upper()}!"
    else:
        play_sound("faint")
        title = "[bold bright_red]💀 MATCH DEFEAT 💀[/]"
        border_col = "bright_red"
        msg = f"{player['name'].upper()} fainted... {opponent['name'].upper()} prevailed."

    telemetry_table = Table(box=box.SIMPLE, expand=True)
    telemetry_table.add_column("Combat Metric", style="bold white")
    telemetry_table.add_column("Value", style="bold cyan", justify="right")

    telemetry_table.add_row("Total Combat Turns", str(turns))
    telemetry_table.add_row("Battle Duration", f"{elapsed}s")
    telemetry_table.add_row("Decisive Move", mvp_move)
    telemetry_table.add_row("Combat Predictor", "Type Effectiveness & Stat Delta Matrix")

    p = Panel(
        Align.center(
            Text.assemble(
                (f"\n{msg}\n\n", "bold white"),
            )
        ),
        title=title,
        border_style=border_col,
        box=box.ROUNDED,
        width=w
    )

    console.print(Align.center(p, width=w))
    console.print(Align.center(Panel(telemetry_table, title="[bold cyan]📊 COMBAT ANALYTICS[/]", border_style="cyan", width=w), width=w))
    console.print(Align.center(Text("\n▼ [Press any key to return to Main Menu]", style="bold yellow blink"), width=w))
    wait_for_key()
