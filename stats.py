"""
stats.py
========
Statistics tracking for FormulaGuess.
Demonstrates text file handling — reads and writes stats.txt
using plain text key=value format.
"""

import os
from datetime import datetime
from utilities import (
    display_header, display_divider, Fore, Style,
    safe_int, safe_float, format_number
)


# ── Default paths ───────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
STATS_FILE = os.path.join(DATA_DIR, "stats.txt")


class StatsManager:
    """
    Manages game statistics using text file I/O.

    Stats are stored in data/stats.txt in a simple key=value format.
    This demonstrates text file reading and writing for the
    CBSE project requirements.

    Attributes
    ----------
    stats : dict
        Dictionary of all tracked statistics.
    stats_path : str
        Path to the stats file.
    """

    # Default statistics template
    DEFAULT_STATS = {
        'games_played': 0,
        'games_won': 0,
        'games_lost': 0,
        'current_streak': 0,
        'best_streak': 0,
        'total_guesses': 0,
        'total_score': 0,
        'driver_wins': 0,
        'constructor_wins': 0,
        'circuit_wins': 0,
        'driver_played': 0,
        'constructor_played': 0,
        'circuit_played': 0,
        'hints_used': 0,
        'perfect_games': 0,
        'last_played': '',
        'player_name': 'Player',
        # Achievement flags
        'ach_first_win': 0,
        'ach_10_wins': 0,
        'ach_50_wins': 0,
        'ach_perfect_accuracy': 0,
        'ach_hall_of_fame': 0,
        'ach_perfect_game': 0,
    }

    def __init__(self, stats_path=None):
        """
        Initialize StatsManager and load existing stats.

        Parameters
        ----------
        stats_path : str, optional
            Path to the stats file. Defaults to data/stats.txt.
        """
        self.stats_path = stats_path or STATS_FILE
        os.makedirs(os.path.dirname(self.stats_path), exist_ok=True)
        self.stats = dict(self.DEFAULT_STATS)
        self.load_stats()

    def load_stats(self):
        """
        Load statistics from the text file.

        File format: key=value (one per line).
        Lines starting with # are treated as comments.
        """
        if not os.path.exists(self.stats_path):
            return

        try:
            with open(self.stats_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, _, value = line.partition('=')
                        key = key.strip()
                        value = value.strip()
                        if key in self.stats:
                            # Convert to appropriate type
                            if isinstance(self.DEFAULT_STATS.get(key), int):
                                self.stats[key] = safe_int(value)
                            elif isinstance(self.DEFAULT_STATS.get(key), float):
                                self.stats[key] = safe_float(value)
                            else:
                                self.stats[key] = value
        except (IOError, OSError) as e:
            print(f"Warning: Could not load stats: {e}")

    def save_stats(self):
        """
        Save statistics to the text file.

        Writes stats in key=value format with a header comment.
        """
        try:
            with open(self.stats_path, 'w', encoding='utf-8') as f:
                f.write(f"# FormulaGuess Statistics\n")
                f.write(f"# Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Do not edit manually\n\n")
                for key, value in sorted(self.stats.items()):
                    f.write(f"{key}={value}\n")
            return True
        except (IOError, OSError) as e:
            print(f"Error saving stats: {e}")
            return False

    def update_stats(self, mode, won, guesses_used, score=0, hints=0):
        """
        Update statistics after a game.

        Parameters
        ----------
        mode : str
            Game mode ('driver', 'constructor', 'circuit').
        won : bool
            Whether the player won.
        guesses_used : int
            Number of guesses used.
        score : int
            Points scored.
        hints : int
            Number of hints used.
        """
        self.stats['games_played'] += 1
        self.stats['total_guesses'] += guesses_used
        self.stats['total_score'] += score
        self.stats['hints_used'] += hints
        self.stats['last_played'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Track per-mode games played
        mode_key = f"{mode}_played"
        if mode_key in self.stats:
            self.stats[mode_key] += 1

        if won:
            self.stats['games_won'] += 1
            self.stats['current_streak'] += 1
            if self.stats['current_streak'] > self.stats['best_streak']:
                self.stats['best_streak'] = self.stats['current_streak']

            # Track per-mode wins
            win_key = f"{mode}_wins"
            if win_key in self.stats:
                self.stats[win_key] += 1

            # Perfect game (guess 1)
            if guesses_used == 1:
                self.stats['perfect_games'] += 1
        else:
            self.stats['games_lost'] += 1
            self.stats['current_streak'] = 0

        self.save_stats()

    def get_win_percentage(self):
        """Calculate win percentage."""
        if self.stats['games_played'] == 0:
            return 0.0
        return (self.stats['games_won'] / self.stats['games_played']) * 100

    def get_average_guesses(self):
        """Calculate average guesses per game."""
        if self.stats['games_played'] == 0:
            return 0.0
        return self.stats['total_guesses'] / self.stats['games_played']

    def display_stats(self):
        """Display formatted statistics in the terminal."""
        display_header("STATISTICS")

        s = self.stats
        win_pct = self.get_win_percentage()
        avg_guesses = self.get_average_guesses()

        # Overall stats
        print(f"  {Fore.WHITE}Player:              {Fore.CYAN}{s['player_name']}{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}Games Played:        {Fore.YELLOW}{format_number(s['games_played'])}{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}Games Won:           {Fore.GREEN}{format_number(s['games_won'])}{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}Games Lost:          {Fore.RED}{format_number(s['games_lost'])}{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}Win Percentage:      {Fore.YELLOW}{win_pct:.1f}%{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}Total Score:         {Fore.YELLOW}{format_number(s['total_score'])}{Style.RESET_ALL}")

        display_divider()

        # Streaks
        print(f"  {Fore.WHITE}Current Streak:      {Fore.GREEN}{s['current_streak']}{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}Best Streak:         {Fore.YELLOW}{s['best_streak']}{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}Average Guesses:     {Fore.CYAN}{avg_guesses:.1f}{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}Perfect Games:       {Fore.MAGENTA}{s['perfect_games']}{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}Hints Used:          {Fore.WHITE}{s['hints_used']}{Style.RESET_ALL}")

        display_divider()

        # Per-mode breakdown
        print(f"  {Fore.WHITE}{Style.BRIGHT}Mode Breakdown:{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}  Driver Wins:       {Fore.GREEN}{s['driver_wins']}{Fore.WHITE}/{s['driver_played']}{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}  Constructor Wins:  {Fore.GREEN}{s['constructor_wins']}{Fore.WHITE}/{s['constructor_played']}{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}  Circuit Wins:      {Fore.GREEN}{s['circuit_wins']}{Fore.WHITE}/{s['circuit_played']}{Style.RESET_ALL}")

        if s['last_played']:
            print(f"\n  {Fore.WHITE}Last Played:         {Fore.CYAN}{s['last_played']}{Style.RESET_ALL}")

        print()

    def export_stats(self, export_path=None):
        """
        Export statistics to a formatted TXT file.

        Parameters
        ----------
        export_path : str, optional
            Path for the export file. Defaults to data/stats_export.txt.

        Returns
        -------
        str
            Path to the exported file.
        """
        if export_path is None:
            export_path = os.path.join(
                os.path.dirname(self.stats_path),
                "stats_export.txt"
            )

        try:
            s = self.stats
            win_pct = self.get_win_percentage()
            avg_guesses = self.get_average_guesses()

            with open(export_path, 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write("    FormulaGuess — Statistics Export\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Player:              {s['player_name']}\n")
                f.write(f"Exported:            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("-" * 50 + "\n")
                f.write("OVERALL\n")
                f.write("-" * 50 + "\n")
                f.write(f"Games Played:        {s['games_played']}\n")
                f.write(f"Games Won:           {s['games_won']}\n")
                f.write(f"Games Lost:          {s['games_lost']}\n")
                f.write(f"Win Percentage:      {win_pct:.1f}%\n")
                f.write(f"Total Score:         {s['total_score']}\n\n")
                f.write("-" * 50 + "\n")
                f.write("STREAKS\n")
                f.write("-" * 50 + "\n")
                f.write(f"Current Streak:      {s['current_streak']}\n")
                f.write(f"Best Streak:         {s['best_streak']}\n")
                f.write(f"Average Guesses:     {avg_guesses:.1f}\n")
                f.write(f"Perfect Games:       {s['perfect_games']}\n\n")
                f.write("-" * 50 + "\n")
                f.write("MODE BREAKDOWN\n")
                f.write("-" * 50 + "\n")
                f.write(f"Driver Wins:         {s['driver_wins']}/{s['driver_played']}\n")
                f.write(f"Constructor Wins:    {s['constructor_wins']}/{s['constructor_played']}\n")
                f.write(f"Circuit Wins:        {s['circuit_wins']}/{s['circuit_played']}\n\n")
                f.write("=" * 50 + "\n")

            return export_path
        except (IOError, OSError) as e:
            print(f"Error exporting stats: {e}")
            return None

    def reset_stats(self):
        """Reset all statistics to defaults."""
        player_name = self.stats.get('player_name', 'Player')
        self.stats = dict(self.DEFAULT_STATS)
        self.stats['player_name'] = player_name
        self.save_stats()
