"""
achievements.py
===============
Achievement tracking system for FormulaGuess.
Checks and awards achievements based on player stats.
"""

from utilities import display_header, display_divider, Fore, Style


# ── Achievement Definitions ─────────────────────────────────────────────────

ACHIEVEMENTS = {
    'ach_first_win': {
        'name': 'First Victory',
        'icon': '🏆',
        'description': 'Win your first game',
        'condition': lambda s: s.get('games_won', 0) >= 1
    },
    'ach_10_wins': {
        'name': 'Race Winner',
        'icon': '🏁',
        'description': 'Win 10 games',
        'condition': lambda s: s.get('games_won', 0) >= 10
    },
    'ach_50_wins': {
        'name': 'Champion',
        'icon': '👑',
        'description': 'Win 50 games',
        'condition': lambda s: s.get('games_won', 0) >= 50
    },
    'ach_perfect_accuracy': {
        'name': 'Perfect Accuracy',
        'icon': '🎯',
        'description': 'Maintain 100% win rate after 5+ games',
        'condition': lambda s: (
            s.get('games_played', 0) >= 5 and
            s.get('games_won', 0) == s.get('games_played', 0)
        )
    },
    'ach_hall_of_fame': {
        'name': 'Hall of Fame',
        'icon': '⭐',
        'description': 'Achieve a 10-game win streak',
        'condition': lambda s: s.get('best_streak', 0) >= 10
    },
    'ach_perfect_game': {
        'name': 'Perfect Game',
        'icon': '💎',
        'description': 'Guess correctly on the first attempt',
        'condition': lambda s: s.get('perfect_games', 0) >= 1
    },
}


class AchievementManager:
    """
    Manages player achievements.

    Achievements are stored as flags in the stats dictionary
    and checked after each game.
    """

    def __init__(self, stats_manager):
        """
        Initialize AchievementManager.

        Parameters
        ----------
        stats_manager : StatsManager
            The stats manager to read/write achievement flags.
        """
        self.stats_mgr = stats_manager

    def check_achievements(self):
        """
        Check all achievements and return newly unlocked ones.

        Returns
        -------
        list of dict
            List of newly unlocked achievements.
        """
        newly_unlocked = []
        stats = self.stats_mgr.stats

        for key, ach in ACHIEVEMENTS.items():
            # Skip already unlocked achievements
            if stats.get(key, 0) == 1:
                continue

            # Check condition
            if ach['condition'](stats):
                stats[key] = 1
                newly_unlocked.append(ach)

        # Save if any new achievements unlocked
        if newly_unlocked:
            self.stats_mgr.save_stats()

        return newly_unlocked

    def display_new_achievements(self, achievements):
        """
        Display newly unlocked achievements with fanfare.

        Parameters
        ----------
        achievements : list of dict
            The achievements to display.
        """
        if not achievements:
            return

        print(f"\n{Fore.YELLOW}{Style.BRIGHT}")
        print("  ╔═══════════════════════════════════════════╗")
        print("  ║          ACHIEVEMENT UNLOCKED!            ║")
        print("  ╚═══════════════════════════════════════════╝")
        print(f"{Style.RESET_ALL}")

        for ach in achievements:
            print(f"  {ach['icon']}  {Fore.GREEN}{Style.BRIGHT}{ach['name']}{Style.RESET_ALL}")
            print(f"     {Fore.WHITE}{ach['description']}{Style.RESET_ALL}")
            print()

    def display_all_achievements(self):
        """Display all achievements with their unlock status."""
        display_header("ACHIEVEMENTS")

        stats = self.stats_mgr.stats
        unlocked_count = 0
        total = len(ACHIEVEMENTS)

        for key, ach in ACHIEVEMENTS.items():
            is_unlocked = stats.get(key, 0) == 1
            if is_unlocked:
                unlocked_count += 1
                status = f"{Fore.GREEN}✅ UNLOCKED{Style.RESET_ALL}"
                icon = ach['icon']
                name_color = Fore.GREEN
            else:
                status = f"{Fore.RED}🔒 Locked{Style.RESET_ALL}"
                icon = "❓"
                name_color = Fore.WHITE

            print(f"  {icon}  {name_color}{Style.BRIGHT}{ach['name']:<25}{Style.RESET_ALL} {status}")
            print(f"     {Fore.WHITE}{ach['description']}{Style.RESET_ALL}")
            print()

        display_divider()
        print(f"  {Fore.CYAN}Progress: {unlocked_count}/{total} achievements unlocked{Style.RESET_ALL}\n")

    def get_completion_percentage(self):
        """
        Get the percentage of achievements unlocked.

        Returns
        -------
        float
            Percentage of achievements unlocked.
        """
        stats = self.stats_mgr.stats
        unlocked = sum(1 for key in ACHIEVEMENTS if stats.get(key, 0) == 1)
        total = len(ACHIEVEMENTS)
        return (unlocked / total * 100) if total > 0 else 0.0
