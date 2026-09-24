"""
Game Loop and Battle Engine for Pokémon Battle Simulator.
Handles turn mechanics, typewriter dialogue with 'Press Any Key ▼' progression,
stat buffs, and animated HP drains.
"""

import time
import copy
import random
from typing import Dict, Any, List
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

from monsters import MONSTERS, MOVES
from doushi_ai import CombatEngine
from sound import play_sound, start_battle_music, stop_battle_music
from renderer import (
    render_battle_screen,
    play_typewriter_message,
    animate_hp_drain,
    wait_for_key,
    clear_terminal,
    print_banner,
    get_terminal_width
)

console = Console()


class BattleSession:
    def __init__(self, player_monster_id: str, opponent_monster_id: str):
        self.engine = CombatEngine()
        self.player = copy.deepcopy(MONSTERS[player_monster_id])
        self.opponent = copy.deepcopy(MONSTERS[opponent_monster_id])
        self.turn = 1
        self.player_buff = 0
        self.opponent_buff = 0
        self.current_win_prob = 0.50
        self.current_insight = "Analyzing combat matchup..."

    def run(self) -> bool:
        """
        Executes the battle loop. Returns True if player won, False if lost.
        """
        # Start the 8-bit battle theme loop
        start_battle_music()

        # Initial combat calculation
        self.current_win_prob, self.current_insight = self.engine.predict_win_probability(
            self.player, self.opponent
        )

        # 1. Opening Typewriter Intro Messages
        play_typewriter_message(
            self.player, self.opponent,
            self.current_win_prob,
            f"Wild {self.opponent['name'].upper()} appeared!"
        )
        play_typewriter_message(
            self.player, self.opponent,
            self.current_win_prob,
            f"Go! {self.player['name'].upper()}!"
        )

        while self.player["hp"] > 0 and self.opponent["hp"] > 0:
            # 2. Update Live Win Probability
            self.current_win_prob, self.current_insight = self.engine.predict_win_probability(
                self.player, self.opponent
            )
            
            # 3. Render Move Selector Screen inside the unified bottom box
            render_battle_screen(
                self.player,
                self.opponent,
                self.current_win_prob,
                move_menu_active=True
            )

            # 4. Player Input
            choice = Prompt.ask(
                "",
                choices=["1", "2", "3", "4", "q", "Q"],
                default="1",
                show_choices=False
            )

            if choice.lower() == "q":
                stop_battle_music()
                play_typewriter_message(
                    self.player, self.opponent,
                    self.current_win_prob,
                    "Got away safely!"
                )
                return False

            move_idx = int(choice) - 1
            if move_idx >= len(self.player["moves"]):
                move_idx = 0
            player_move_name = self.player["moves"][move_idx]
            ai_move_name = self.engine.select_ai_move(self.opponent, self.player)

            # 5. Determine Turn Priority
            p_speed = self.player["speed"] + (50 if any(k in player_move_name for k in ["Jet", "Dash", "Quick", "Speed"]) else 0)
            o_speed = self.opponent["speed"] + (50 if any(k in ai_move_name for k in ["Jet", "Dash", "Quick", "Speed"]) else 0)

            first_attacker, second_attacker = (
                ("player", player_move_name),
                ("opponent", ai_move_name)
            ) if p_speed >= o_speed else (
                ("opponent", ai_move_name),
                ("player", player_move_name)
            )

            # 6. Execute Moves with Typewriter & Keypress Advancement
            for side, move_name in [first_attacker, second_attacker]:
                if side == "player" and self.player["hp"] > 0 and self.opponent["hp"] > 0:
                    self._execute_player_move(move_name)
                elif side == "opponent" and self.opponent["hp"] > 0 and self.player["hp"] > 0:
                    self._execute_opponent_move(move_name)

            self.turn += 1

        # End of match screen
        return self._handle_match_end()

    def _execute_player_move(self, move_name: str):
        play_typewriter_message(
            self.player, self.opponent,
            self.current_win_prob,
            f"{self.player['name'].upper()} used {move_name}!"
        )

        if move_name in ["Tactical Scan", "AI Analysis"]:
            play_sound("scan")
            self.player_buff = 3
            self.player["attack"] += 8
            play_typewriter_message(
                self.player, self.opponent,
                self.current_win_prob,
                "Tactical scan complete! Attack and Critical rate boosted!"
            )
            return

        dmg, is_crit, mult, desc = self.engine.calculate_damage(self.player, self.opponent, move_name)
        if dmg == 0:
            play_typewriter_message(
                self.player, self.opponent,
                self.current_win_prob,
                f"{self.player['name'].upper()}'s attack missed!"
            )
        else:
            old_opp_hp = self.opponent["hp"]
            new_opp_hp = max(0, old_opp_hp - dmg)
            self.opponent["hp"] = new_opp_hp

            if is_crit:
                play_sound("crit")
            else:
                play_sound("hit")

            # Animate HP Drain
            animate_hp_drain(
                self.player, self.opponent,
                self.current_win_prob,
                f"Dealt {dmg} damage to {self.opponent['name'].upper()}!",
                target="opponent", old_hp=old_opp_hp, new_hp=new_opp_hp
            )

            if desc:
                play_typewriter_message(
                    self.player, self.opponent,
                    self.current_win_prob,
                    desc
                )

            # Drain heals
            if move_name in ["Giga Drain", "Byte Drain", "Draining Kiss"] and new_opp_hp > 0:
                heal = max(5, int(dmg * 0.4))
                old_p_hp = self.player["hp"]
                self.player["hp"] = min(self.player["max_hp"], old_p_hp + heal)
                play_typewriter_message(
                    self.player, self.opponent,
                    self.current_win_prob,
                    f"Absorbed {heal} HP!"
                )

    def _execute_opponent_move(self, move_name: str):
        play_typewriter_message(
            self.player, self.opponent,
            self.current_win_prob,
            f"Enemy {self.opponent['name'].upper()} used {move_name}!"
        )

        if move_name in ["Tactical Scan", "AI Analysis"]:
            play_sound("scan")
            self.opponent_buff = 3
            self.opponent["attack"] += 8
            play_typewriter_message(
                self.player, self.opponent,
                self.current_win_prob,
                f"Enemy {self.opponent['name'].upper()} ran Tactical Scan! Attack boosted!"
            )
            return

        dmg, is_crit, mult, desc = self.engine.calculate_damage(self.opponent, self.player, move_name)
        if dmg == 0:
            play_typewriter_message(
                self.player, self.opponent,
                self.current_win_prob,
                f"Enemy {self.opponent['name'].upper()}'s attack missed!"
            )
        else:
            old_p_hp = self.player["hp"]
            new_p_hp = max(0, old_p_hp - dmg)
            self.player["hp"] = new_p_hp

            if is_crit:
                play_sound("crit")
            else:
                play_sound("hit")

            # Animate HP Drain
            animate_hp_drain(
                self.player, self.opponent,
                self.current_win_prob,
                f"{self.player['name'].upper()} took {dmg} damage!",
                target="player", old_hp=old_p_hp, new_hp=new_p_hp
            )

            if desc:
                play_typewriter_message(
                    self.player, self.opponent,
                    self.current_win_prob,
                    desc
                )

            if move_name in ["Giga Drain", "Byte Drain", "Draining Kiss"] and new_p_hp > 0:
                heal = max(5, int(dmg * 0.4))
                self.opponent["hp"] = min(self.opponent["max_hp"], self.opponent["hp"] + heal)
                play_typewriter_message(
                    self.player, self.opponent,
                    self.current_win_prob,
                    f"Enemy absorbed {heal} HP!"
                )

    def _handle_match_end(self) -> bool:
        stop_battle_music()
        w = get_terminal_width()
        player_won = self.player["hp"] > 0

        if player_won:
            play_sound("victory")
            play_typewriter_message(
                self.player, self.opponent,
                1.0,
                f"Enemy {self.opponent['name'].upper()} fainted!"
            )
            play_typewriter_message(
                self.player, self.opponent,
                1.0,
                f"{self.player['name'].upper()} won the battle in {self.turn} turns! 🏆"
            )
        else:
            play_sound("faint")
            play_typewriter_message(
                self.player, self.opponent,
                0.0,
                f"{self.player['name'].upper()} fainted..."
            )
            play_typewriter_message(
                self.player, self.opponent,
                0.0,
                "You whited out! 💀"
            )

        clear_terminal()
        print_banner()

        title = "[bold bright_green]🏆 VICTORY! 🏆[/]" if player_won else "[bold bright_red]💀 DEFEAT! 💀[/]"
        border = "bright_green" if player_won else "bright_red"

        summary = Text.assemble(
            (f"Match concluded in {self.turn} turns.\n\n", "bold white"),
            ("📊 Combat Telemetry Summary:\n", "bold cyan"),
            (f" • Match Result: {'Player Victory' if player_won else 'Opponent Victory'}\n", "white"),
            (f" • Key Factor: Speed ({self.player['speed']} vs {self.opponent['speed']}) & Type Matchup\n\n", "white"),
            ("⚡ Train custom tabular ML models on your match data using Doushi.ai (https://doushi.ai)\n", "italic dim cyan")
        )

        console.print(Align.center(Panel(summary, title=title, border_style=border, box=box.HEAVY, width=w), width=w))
        Prompt.ask("\n[bold yellow]Press Enter to continue...[/]")
        return player_won
