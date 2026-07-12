"""
leaderboard.py
==============
Leaderboard management for FormulaGuess.
Demonstrates CSV file handling — reads and writes leaderboard.csv,
sorting data by wins and best streak.
"""

import csv
import os
from utilities import (
    display_header, display_divider, Fore, Style,
    safe_int, safe_float, format_number
)


# ── Default paths ───────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.csv")

# CSV column headers
LEADERBOARD_HEADERS = [
    'Player Name', 'Games Played', 'Wins',
    'Best Streak', 'Average Guesses', 'Total Score'
]


class LeaderboardManager:
    """
    Manages the game leaderboard using CSV file I/O.

    The leaderboard is sorted by Wins (descending),
    then by Best Streak (descending).

    Demonstrates CSV reading, writing, and sorting
    for the CBSE project requirements.
    """

    def __init__(self, leaderboard_path=None):
        """
        Initialize LeaderboardManager.

        Parameters
        ----------
        leaderboard_path : str, optional
            Path to the leaderboard CSV. Defaults to data/leaderboard.csv.
        """
        self.leaderboard_path = leaderboard_path or LEADERBOARD_FILE
        os.makedirs(os.path.dirname(self.leaderboard_path), exist_ok=True)
        self.entries = []
        self.load_leaderboard()

    def load_leaderboard(self):
        """
        Load leaderboard data from CSV file.

        Each row is stored as a dictionary matching LEADERBOARD_HEADERS.
        """
        self.entries = []
        if not os.path.exists(self.leaderboard_path):
            return

        try:
            with open(self.leaderboard_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    entry = {
                        'Player Name': row.get('Player Name', 'Unknown').strip(),
                        'Games Played': safe_int(row.get('Games Played', 0)),
                        'Wins': safe_int(row.get('Wins', 0)),
                        'Best Streak': safe_int(row.get('Best Streak', 0)),
                        'Average Guesses': safe_float(row.get('Average Guesses', 0.0)),
                        'Total Score': safe_int(row.get('Total Score', 0)),
                    }
                    self.entries.append(entry)
        except (IOError, csv.Error) as e:
            print(f"Warning: Could not load leaderboard: {e}")
            self.entries = []

    def save_leaderboard(self):
        """
        Save leaderboard data to CSV file.

        Sorts entries before saving.
        """
        self._sort_entries()
        try:
            with open(self.leaderboard_path, 'w', newline='',
                       encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=LEADERBOARD_HEADERS)
                writer.writeheader()
                for entry in self.entries:
                    writer.writerow(entry)
            return True
        except (IOError, csv.Error) as e:
            print(f"Error saving leaderboard: {e}")
            return False

    def update_leaderboard(self, player_name, won, guesses_used,
                           best_streak, score=0):
        """
        Update or create a leaderboard entry for a player.

        Parameters
        ----------
        player_name : str
            The player's name.
        won : bool
            Whether the game was won.
        guesses_used : int
            Number of guesses used.
        best_streak : int
            Player's current best streak.
        score : int
            Points scored this game.
        """
        # Search for existing entry (case-insensitive)
        existing = None
        for entry in self.entries:
            if entry['Player Name'].lower() == player_name.lower():
                existing = entry
                break

        if existing:
            # Update existing entry
            existing['Games Played'] += 1
            if won:
                existing['Wins'] += 1
            if best_streak > existing['Best Streak']:
                existing['Best Streak'] = best_streak
            existing['Total Score'] += score

            # Recalculate average guesses
            total_guesses = existing['Average Guesses'] * (existing['Games Played'] - 1) + guesses_used
            existing['Average Guesses'] = round(total_guesses / existing['Games Played'], 1)
        else:
            # Create new entry
            new_entry = {
                'Player Name': player_name,
                'Games Played': 1,
                'Wins': 1 if won else 0,
                'Best Streak': best_streak,
                'Average Guesses': round(float(guesses_used), 1),
                'Total Score': score,
            }
            self.entries.append(new_entry)

        self.save_leaderboard()

    def _sort_entries(self):
        """
        Sort leaderboard entries.

        Primary sort: Wins (descending)
        Secondary sort: Best Streak (descending)
        Tertiary sort: Total Score (descending)
        """
        self.entries.sort(
            key=lambda e: (
                -e.get('Wins', 0),
                -e.get('Best Streak', 0),
                -e.get('Total Score', 0)
            )
        )

    def display_leaderboard(self, top_n=15):
        """
        Display the leaderboard in a formatted table.

        Parameters
        ----------
        top_n : int
            Number of top entries to display.
        """
        display_header("LEADERBOARD")

        if not self.entries:
            print(f"  {Fore.YELLOW}No entries yet. Play a game to get on the board!{Style.RESET_ALL}\n")
            return

        self._sort_entries()
        shown = self.entries[:top_n]

        # Table header
        print(f"  {Fore.WHITE}{Style.BRIGHT}"
              f"{'Rank':<6}{'Player':<18}{'Played':<9}{'Wins':<7}"
              f"{'Streak':<9}{'Avg Guess':<11}{'Score':<8}"
              f"{Style.RESET_ALL}")
        print(f"  {Fore.RED}{'─' * 66}{Style.RESET_ALL}")

        for i, entry in enumerate(shown, 1):
            # Medal for top 3
            if i == 1:
                rank = f"{Fore.YELLOW}🥇 1  {Style.RESET_ALL}"
            elif i == 2:
                rank = f"{Fore.WHITE}🥈 2  {Style.RESET_ALL}"
            elif i == 3:
                rank = f"{Fore.RED}🥉 3  {Style.RESET_ALL}"
            else:
                rank = f"   {i:<3}"

            name = entry['Player Name'][:16]
            played = entry['Games Played']
            wins = entry['Wins']
            streak = entry['Best Streak']
            avg = entry['Average Guesses']
            score = entry['Total Score']

            print(f"  {rank}{Fore.WHITE}{name:<18}{played:<9}{Fore.GREEN}{wins:<7}"
                  f"{Fore.YELLOW}{streak:<9}{Fore.CYAN}{avg:<11.1f}"
                  f"{Fore.MAGENTA}{score:<8}{Style.RESET_ALL}")

        if len(self.entries) > top_n:
            remaining = len(self.entries) - top_n
            print(f"\n  {Fore.WHITE}... and {remaining} more players{Style.RESET_ALL}")

        print()

    def get_player_rank(self, player_name):
        """
        Get a player's rank on the leaderboard.

        Parameters
        ----------
        player_name : str
            The player's name.

        Returns
        -------
        int or None
            The player's rank (1-indexed), or None if not found.
        """
        self._sort_entries()
        for i, entry in enumerate(self.entries, 1):
            if entry['Player Name'].lower() == player_name.lower():
                return i
        return None

    def search_player(self, query):
        """
        Search for a player on the leaderboard.

        Parameters
        ----------
        query : str
            Search query (partial match supported).

        Returns
        -------
        list of dict
            Matching entries.
        """
        query_lower = query.strip().lower()
        return [
            entry for entry in self.entries
            if query_lower in entry['Player Name'].lower()
        ]
