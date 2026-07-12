"""
main.py
=======
Entry point for FormulaGuess — a terminal-based Formula 1 Wordle game.

This is the main script that initializes all components and
launches the game. Run this file to start playing.

Modules Used:
    csv, random, pickle, os, datetime, colorama,
    textwrap, collections, statistics, time, sys

Usage:
    python main.py
"""

import sys
import os
import time

# ── Ensure project directory is on path ─────────────────────────────────────
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# ── Check for colorama ─────────────────────────────────────────────────────
try:
    from colorama import init
    init(autoreset=True)
except ImportError:
    print("=" * 55)
    print("  WARNING: colorama is not installed.")
    print("  The game will work, but without colored output.")
    print("  Install it with: pip install colorama")
    print("=" * 55)
    print()

# ── Import game modules ────────────────────────────────────────────────────
from utilities import (
    display_banner, print_success, print_error, print_info,
    print_warning, get_player_name, clear_screen, pause,
    Fore, Style
)
from csv_loader import CSVLoader
from stats import StatsManager
from leaderboard import LeaderboardManager
from achievements import AchievementManager
from menu import Menu


def check_data_directory():
    """
    Verify that the data directory and required CSV files exist.

    Returns
    -------
    bool
        True if the data directory exists with required files.
    """
    data_dir = os.path.join(PROJECT_DIR, "data")

    if not os.path.exists(data_dir):
        print_error(f"Data directory not found: {data_dir}")
        print_info("Please ensure the 'data' folder with CSV files is present.")
        return False

    required_files = ['drivers.csv']
    optional_files = ['teams.csv', 'circuits.csv', 'constructors.csv',
                      'season_champions.csv', 'race_winners.csv']

    missing_required = []
    missing_optional = []

    for f in required_files:
        if not os.path.exists(os.path.join(data_dir, f)):
            missing_required.append(f)

    for f in optional_files:
        if not os.path.exists(os.path.join(data_dir, f)):
            missing_optional.append(f)

    if missing_required:
        print_error(f"Missing required files: {', '.join(missing_required)}")
        return False

    if missing_optional:
        print_warning(f"Missing optional files: {', '.join(missing_optional)}")
        print_info("Some game modes may be unavailable.")

    return True


def load_game_data():
    """
    Load all CSV game data.

    Returns
    -------
    CSVLoader or None
        Loaded data, or None if critical files missing.
    """
    print_info("Loading game data...")
    loader = CSVLoader()
    success = loader.load_all()

    if not success:
        print_error("Failed to load critical game data!")
        return None

    # Display data summary
    summary = loader.get_data_summary()
    print_success(f"Loaded: {summary['drivers']} drivers, "
                  f"{summary['teams']} teams, "
                  f"{summary['circuits']} circuits, "
                  f"{summary['constructors']} constructors")
    return loader


def initialize_player(stats_manager):
    """
    Initialize or load the player's identity.

    Parameters
    ----------
    stats_manager : StatsManager
        The stats manager to check for existing player.

    Returns
    -------
    str
        The player's name.
    """
    existing_name = stats_manager.stats.get('player_name', '')

    if existing_name and existing_name != 'Player':
        print(f"\n  {Fore.CYAN}Welcome back, "
              f"{Fore.WHITE}{Style.BRIGHT}{existing_name}!{Style.RESET_ALL}")
        choice = input(f"  {Fore.CYAN}Continue as {existing_name}? (Y/n): "
                       f"{Style.RESET_ALL}").strip().lower()
        if choice not in ('n', 'no'):
            return existing_name

    print(f"\n  {Fore.CYAN}{'─' * 40}{Style.RESET_ALL}")
    name = get_player_name()
    stats_manager.stats['player_name'] = name
    stats_manager.save_stats()
    return name


def main():
    """
    Main entry point for FormulaGuess.

    Initializes all components, loads data, and launches
    the interactive menu system.
    """
    try:
        # Clear screen and show banner
        clear_screen()
        display_banner()

        # Check data directory
        if not check_data_directory():
            print_error("Cannot start without game data.")
            print_info("Ensure the 'data' directory contains drivers.csv")
            sys.exit(1)

        # Load CSV data
        loader = load_game_data()
        if loader is None:
            print_error("Failed to initialize game data.")
            sys.exit(1)

        # Initialize statistics (text file I/O)
        stats_mgr = StatsManager()

        # Initialize leaderboard (CSV file I/O)
        lb_mgr = LeaderboardManager()

        # Initialize achievements
        ach_mgr = AchievementManager(stats_mgr)

        # Get player name
        player_name = initialize_player(stats_mgr)

        time.sleep(0.5)

        # Create and show main menu
        menu = Menu(
            csv_loader=loader,
            stats_manager=stats_mgr,
            leaderboard_manager=lb_mgr,
            achievement_manager=ach_mgr
        )
        menu.player_name = player_name

        # Launch the game!
        menu.show_main_menu()

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Game interrupted. Goodbye! 🏁{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
