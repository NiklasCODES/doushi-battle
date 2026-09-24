#!/usr/bin/env python3
"""
Retro Terminal Pokémon Battle Simulator
Featuring all 151 Original Pokémon, ANSI Half-Block Color Sprites,
Turn-Based Combat, Dynamic Win Probability Analytics, and 8-Bit Audio.

Run directly:
    python3 main.py
"""

import sys
import random
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from rich.align import Align
from rich import box

from monsters import MONSTERS, FEATURED_STARTERS, find_pokemon
from game import BattleSession
from renderer import clear_terminal, print_banner, get_terminal_width, TYPE_COLORS, format_sprite_text

console = Console()


def display_pokedex_gallery():
    """Interactive Pokédex browser: allows browsing pages or searching any of the 151 Pokémon."""
    page = 0
    per_page = 4
    all_keys = [k for k in MONSTERS.keys() if k.startswith("poke_")]
    
    while True:
        clear_terminal()
        print_banner()
        w = get_terminal_width()
        total_pages = (len(all_keys) + per_page - 1) // per_page
        
        console.print(Align.center(f"[bold bright_yellow]📖 151 POKÉDEX ARCHIVE — Page {page + 1}/{total_pages}[/]\n", width=w))

        start_idx = page * per_page
        end_idx = min(start_idx + per_page, len(all_keys))
        current_batch = all_keys[start_idx:end_idx]

        for m_id in current_batch:
            m = MONSTERS[m_id]
            t_col = TYPE_COLORS.get(m["type"], "white")
            sprite_lines = m.get("sprite_front", m.get("sprite", []))
            sprite_widget = format_sprite_text(sprite_lines, fallback_style=f"bold {t_col}")
            
            info = Table.grid(padding=(0, 2), expand=True)
            info.add_column(ratio=1)
            info.add_column(ratio=2)
            
            types_str = " / ".join(m.get("types", [m["type"]]))
            stats_table = Table.grid()
            stats_table.add_row(Text("Type: ", style="bold white"), Text(types_str, style=f"bold {t_col}"))
            stats_table.add_row(Text("HP: ", style="bold white"), Text(str(m["hp"]), style="green"))
            stats_table.add_row(Text("ATK: ", style="bold white"), Text(str(m["attack"]), style="red"))
            stats_table.add_row(Text("DEF: ", style="bold white"), Text(str(m["defense"]), style="blue"))
            stats_table.add_row(Text("SPD: ", style="bold white"), Text(str(m["speed"]), style="yellow"))
            stats_table.add_row(Text("Moves: ", style="bold white"), Text(", ".join(m["moves"]), style="italic dim white"))

            info.add_row(sprite_widget, stats_table)

            panel = Panel(
                info,
                title=f"[bold {t_col}]#{m.get('dex_num', 0):03d} {m['name'].upper()}[/] [italic dim white]({m.get('title', '')})[/]",
                border_style=t_col,
                box=box.ROUNDED,
                width=w
            )
            console.print(Align.center(panel, width=w))

        nav = Table.grid(expand=True)
        nav.add_column(ratio=1, justify="left")
        nav.add_column(ratio=1, justify="right")
        nav.add_row(
            Text("[N] Next  [P] Prev  [S] Search by Name/ID", style="bold cyan"),
            Text("[Q] Back to Menu", style="bold yellow")
        )
        console.print(Align.center(nav, width=w))

        cmd = Prompt.ask("\n[bold cyan]Action[/]", default="N").strip().upper()
        if cmd == "N":
            if page < total_pages - 1:
                page += 1
            else:
                page = 0
        elif cmd == "P":
            if page > 0:
                page -= 1
            else:
                page = total_pages - 1
        elif cmd == "S":
            query = Prompt.ask("[bold yellow]Enter Pokémon Name or Dex Number (e.g. 25, Gengar, Mewtwo)[/]").strip()
            found = find_pokemon(query)
            if found:
                inspect_single_pokemon(found)
            else:
                Prompt.ask("[bold red]Pokémon not found. Press Enter to continue...[/]")
        elif cmd == "Q" or cmd == "B":
            break


def inspect_single_pokemon(m: dict):
    """Detailed view for a single Pokémon with front and back sprites."""
    clear_terminal()
    print_banner()
    w = get_terminal_width()
    t_col = TYPE_COLORS.get(m["type"], "white")

    front_lines = m.get("sprite_front", [])
    back_lines = m.get("sprite", [])

    grid = Table.grid(padding=(0, 2), expand=True)
    grid.add_column(ratio=1, justify="center")
    grid.add_column(ratio=1, justify="center")
    grid.add_column(ratio=2)

    stats_table = Table.grid()
    stats_table.add_row(Text("Dex #: ", style="bold white"), Text(f"#{m.get('dex_num', 0):03d}", style="bold yellow"))
    stats_table.add_row(Text("Type: ", style="bold white"), Text(" / ".join(m.get("types", [m["type"]])), style=f"bold {t_col}"))
    stats_table.add_row(Text("Base HP: ", style="bold white"), Text(str(m["hp"]), style="green"))
    stats_table.add_row(Text("Attack: ", style="bold white"), Text(str(m["attack"]), style="red"))
    stats_table.add_row(Text("Defense: ", style="bold white"), Text(str(m["defense"]), style="blue"))
    stats_table.add_row(Text("Speed: ", style="bold white"), Text(str(m["speed"]), style="yellow"))
    stats_table.add_row(Text("Movepool: ", style="bold white"), Text(", ".join(m["moves"]), style="italic cyan"))

    grid.add_row(
        Panel(format_sprite_text(front_lines, fallback_style=f"bold {t_col}"), title="[dim]Front Sprite[/]", box=box.HORIZONTALS),
        Panel(format_sprite_text(back_lines, fallback_style=f"bold {t_col}"), title="[dim]Back Sprite[/]", box=box.HORIZONTALS),
        stats_table
    )

    panel = Panel(
        grid,
        title=f"[bold {t_col}]POKÉDEX ENTRY: #{m.get('dex_num', 0):03d} {m['name'].upper()}[/]",
        border_style=t_col,
        box=box.DOUBLE,
        width=w
    )
    console.print(Align.center(panel, width=w))
    Prompt.ask("\n[bold cyan]Press Enter to return...[/]")


def select_monster(prompt_text: str = "Select your fighter") -> str:
    """Provides fighter selection (Featured Starters, Search 151, Random, Retro)."""
    clear_terminal()
    print_banner()
    w = get_terminal_width()
    console.print(Align.center(f"[bold bright_cyan]🎯 {prompt_text}:[/]\n", width=w))

    table = Table(box=box.ROUNDED, expand=True, width=w)
    table.add_column("#", justify="center", style="bold yellow", width=4)
    table.add_column("Pokémon / Fighter", style="bold white", width=18)
    table.add_column("Type", justify="center", width=12)
    table.add_column("HP", justify="center", style="green", width=6)
    table.add_column("ATK", justify="center", style="red", width=6)
    table.add_column("DEF", justify="center", style="blue", width=6)
    table.add_column("SPD", justify="center", style="yellow", width=6)

    for i, m_id in enumerate(FEATURED_STARTERS, 1):
        if m_id in MONSTERS:
            m = MONSTERS[m_id]
            t_col = TYPE_COLORS.get(m["type"], "white")
            table.add_row(
                str(i),
                f"#{m.get('dex_num', 0):03d} {m['name']}",
                f"[{t_col}]{m['type']}[/{t_col}]",
                str(m["hp"]),
                str(m["attack"]),
                str(m["defense"]),
                str(m["speed"])
            )

    console.print(Align.center(table, width=w))
    console.print(Align.center(Text("\n[S] Search Any 151 Pokémon by Name/ID   [R] Random Pokémon   [C] Custom Retro Monsters", style="bold yellow"), width=w))

    while True:
        raw_choice = Prompt.ask("\n[bold cyan]Choose number (1-18) or [S/R/C][/]", default="1").strip().upper()
        
        if raw_choice.isdigit():
            idx = int(raw_choice)
            if 1 <= idx <= len(FEATURED_STARTERS):
                return FEATURED_STARTERS[idx - 1]
        
        elif raw_choice == "R":
            all_poke = [k for k in MONSTERS.keys() if k.startswith("poke_")]
            chosen = random.choice(all_poke)
            console.print(f"[bold green]Selected Random: {MONSTERS[chosen]['name']}![/]")
            return chosen
        
        elif raw_choice == "S":
            q = Prompt.ask("[bold yellow]Enter Pokémon Name or Dex Number (e.g. 6 for Charizard, Mewtwo, Gengar)[/]").strip()
            found = find_pokemon(q)
            if found:
                return found["id"]
            else:
                console.print("[bold red]Pokémon not found! Try again.[/]")
        
        elif raw_choice == "C":
            custom_keys = ["pyrozard", "aquablast", "voltmouse", "florasaur", "psycrab"]
            for i, k in enumerate(custom_keys, 1):
                console.print(f"[{i}] {MONSTERS[k]['name']} ({MONSTERS[k]['type']})")
            c_idx = Prompt.ask("[bold cyan]Pick (1-5)[/]", choices=["1", "2", "3", "4", "5"], default="1")
            return custom_keys[int(c_idx) - 1]
        
        console.print("[bold red]Invalid option. Please choose a number or S/R/C.[/]")


def run_quick_battle():
    player_id = select_monster("Select your Pokémon fighter")
    
    # Choose opponent mode
    clear_terminal()
    print_banner()
    w = get_terminal_width()
    console.print(Align.center("[bold cyan]⚔️ CHOOSE OPPONENT ⚔️[/]\n", width=w))
    
    opp_table = Table(box=box.ROUNDED, expand=True, width=w)
    opp_table.add_column("#", justify="center", style="bold yellow", width=4)
    opp_table.add_column("Mode", style="bold white", width=22)
    opp_table.add_column("Details", style="dim white")
    opp_table.add_row("1", "Random Wild Pokémon", "Battle a random encounter from the 151 Pokédex.")
    opp_table.add_row("2", "Specific Pokémon", "Pick exactly who you want to challenge.")
    opp_table.add_row("3", "Legendary Mewtwo", "Challenge the ultimate psychic boss #150 Mewtwo.")

    console.print(Align.center(opp_table, width=w))
    opp_mode = Prompt.ask("\n[bold cyan]Select Opponent (1-3)[/]", choices=["1", "2", "3"], default="1")

    if opp_mode == "1":
        all_opps = [k for k in MONSTERS.keys() if k != player_id]
        opp_id = random.choice(all_opps)
    elif opp_mode == "2":
        opp_id = select_monster("Select your opponent Pokémon")
    else:
        opp_id = "poke_150"

    session = BattleSession(player_id, opp_id)
    session.run()


def run_gauntlet():
    clear_terminal()
    print_banner()
    w = get_terminal_width()
    console.print(Align.center("[bold bright_magenta]⚔️ THE CHAMPION GAUNTLET ⚔️[/]", width=w))
    console.print(Align.center("[italic white]Battle through iconic Pokémon masters and defeat the final Legendary Mewtwo![/]\n", width=w))
    
    player_id = select_monster("Select your Champion for the Gauntlet")
    
    # Classic gauntlet bosses: Charizard -> Gengar -> Dragonite -> Legendary Mewtwo (#150)
    challengers = ["poke_6", "poke_94", "poke_149", "poke_150"]

    for stage, opp_id in enumerate(challengers, 1):
        clear_terminal()
        print_banner()
        boss_label = "FINAL BOSS" if opp_id == "poke_150" else f"STAGE {stage}/4"
        console.print(Align.center(f"[bold yellow]=== {boss_label}: FIGHTING {MONSTERS[opp_id]['name'].upper()} ===[/]\n", width=w))
        Prompt.ask("[bold cyan]Press Enter to step into the arena...[/]")

        session = BattleSession(player_id, opp_id)
        won = session.run()
        if not won:
            console.print(Align.center("[bold red]💀 Gauntlet Failed! Train harder and try again.[/]", width=w))
            Prompt.ask("\n[bold yellow]Press Enter...[/]")
            return

    clear_terminal()
    print_banner()
    victory_text = Text.assemble(
        ("🎉 CONGRATULATIONS! YOU CONQUERED THE GAUNTLET! 🎉\n\n", "bold bright_green"),
        ("You defeated all challengers and conquered the combat arena!\n\n", "white"),
        ("⚡ Interested in building Machine Learning models on combat or tabular data?\n", "bold cyan"),
        ("Check out https://doushi.ai - Build, train, and deploy AutoML models with plain text.", "white")
    )
    console.print(Align.center(Panel(victory_text, border_style="bright_green", box=box.DOUBLE, width=w), width=w))
    Prompt.ask("\n[bold yellow]Press Enter to return to main menu...[/]")


def show_about():
    clear_terminal()
    print_banner()
    w = get_terminal_width()
    about_text = Text.assemble(
        ("⚡ ABOUT THIS SIMULATOR & DOUSHI.AI\n\n", "bold bright_magenta"),
        ("This is an open-source retro terminal Pokémon battle simulator featuring all 151 original ", "white"),
        ("Pokémon rendered in high-definition ANSI TrueColor pixel art with 8-bit chiptunes.\n\n", "white"),
        ("📊 Combat Win Probability Modeling:\n", "bold bright_cyan"),
        ("Every turn, the simulator evaluates HP ratios, speed initiative, and type multipliers ", "white"),
        ("to calculate dynamic win probabilities and optimal AI decisions.\n\n", "white"),
        ("🤖 Train Your Own ML Models with Doushi.ai:\n", "bold bright_yellow"),
        ("Doushi.ai is a tabular AutoML platform. You can export match telemetry into CSV and use ", "white"),
        ("Doushi to train real machine learning models with natural language.\n\n", "white"),
        ("🔗 Doushi.ai Platform: ", "bold yellow"),
        ("https://doushi.ai\n", "underline cyan"),
        ("📦 CLI Tool:            ", "bold yellow"),
        ("pip install doushi-cli\n", "bold green"),
        ("💻 GitHub Repository:   ", "bold yellow"),
        ("https://github.com/niklascodes/doushi-battle\n", "underline cyan")
    )
    console.print(Align.center(Panel(about_text, border_style="bright_magenta", box=box.ROUNDED, width=w), width=w))
    Prompt.ask("\n[bold cyan]Press Enter to return to main menu...[/]")


def main():
    while True:
        clear_terminal()
        print_banner()
        w = get_terminal_width()

        menu = Table(box=box.SIMPLE, expand=True, width=w)
        menu.add_column("[#]", justify="center", style="bold yellow", width=6)
        menu.add_column("Mode", style="bold white", width=24)
        menu.add_column("Description", style="dim white")

        menu.add_row("[1]", "Quick Battle", "Pick any Pokémon and battle against wild AI or custom opponents.")
        menu.add_row("[2]", "Champion Gauntlet", "Battle 4 legendary stages culminating in the Sovereign Boss.")
        menu.add_row("[3]", "151 Pokédex Archive", "Browse full 151 Pokémon sprites, stats, and search by name/ID.")
        menu.add_row("[4]", "About & ML Training", "Learn how combat modeling and Doushi.ai work.")
        menu.add_row("[5]", "Exit", "Quit to terminal.")

        console.print(Align.center(Panel(menu, title="[bold white]🎮 MAIN MENU[/]", border_style="cyan", box=box.ROUNDED, width=w), width=w))

        choice = Prompt.ask("\n[bold cyan]Select an option (1-5)[/]", choices=["1", "2", "3", "4", "5"], default="1")

        if choice == "1":
            run_quick_battle()
        elif choice == "2":
            run_gauntlet()
        elif choice == "3":
            display_pokedex_gallery()
        elif choice == "4":
            show_about()
        elif choice == "5":
            clear_terminal()
            console.print(Align.center("[bold green]Thanks for playing! Check out https://doushi.ai ⚡[/]", width=w))
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_terminal()
        print("\nSession ended. Visit https://doushi.ai")
        sys.exit(0)
