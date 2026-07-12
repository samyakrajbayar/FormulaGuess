"""
menu.py
=======
Main menu system for FormulaGuess.
Handles navigation, sub-menus, help page,
and game mode selection with difficulty levels.
"""

from utilities import (
    display_banner, display_header, display_subheader, display_divider,
    get_valid_input, get_player_name, clear_screen, pause,
    print_success, print_error, print_warning, print_info,
    Fore, Style
)
from driver_game import DriverGame
from constructor_game import ConstructorGame
from circuit_game import CircuitGame
from savegame import SaveManager, GameState


class Menu:
    """
    Main menu system for FormulaGuess.

    Handles all user navigation, game mode selection,
    difficulty settings, and sub-menu displays.

    Parameters
    ----------
    csv_loader : CSVLoader
        The loaded CSV data.
    stats_manager : StatsManager
        Statistics tracker.
    leaderboard_manager : LeaderboardManager
        Leaderboard tracker.
    achievement_manager : AchievementManager
        Achievement tracker.
    """

    def __init__(self, csv_loader, stats_manager,
                 leaderboard_manager, achievement_manager):
        self.data = csv_loader
        self.stats = stats_manager
        self.leaderboard = leaderboard_manager
        self.achievements = achievement_manager
        self.save_manager = SaveManager()
        self.player_name = self.stats.stats.get('player_name', 'Player')

    def show_main_menu(self):
        """
        Display the main menu and handle user selection.

        This is the primary game loop that returns only when
        the user chooses to exit.
        """
        while True:
            clear_screen()
            display_banner()

            # Check for saved game
            save_info = self.save_manager.get_save_info()

            print(f"  {Fore.CYAN}Welcome, {Fore.WHITE}{Style.BRIGHT}"
                  f"{self.player_name}!{Style.RESET_ALL}\n")

            options = [
                ("1", "🏎  Driver Guess"),
                ("2", "🏗  Constructor Guess"),
                ("3", "🏁  Circuit Guess"),
                ("4", "📊  Statistics"),
                ("5", "🏆  Leaderboard"),
                ("6", "🎖  Achievements"),
                ("7", "❓  Help"),
                ("8", "👤  Change Player"),
                ("9", "🚪  Exit"),
            ]

            for key, label in options:
                print(f"  {Fore.YELLOW}{key}.{Style.RESET_ALL} {label}")

            if save_info:
                print(f"\n  {Fore.GREEN}💾 Saved game found: "
                      f"{save_info['game_mode'].title()} mode, "
                      f"{save_info['remaining_guesses']} guesses left "
                      f"({save_info['timestamp']}){Style.RESET_ALL}")
                print(f"  {Fore.YELLOW}0.{Style.RESET_ALL} Resume Saved Game")

            print()
            choice = get_valid_input(
                "  Choose option: ",
                ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            )

            if choice is None or choice == '9':
                self._exit_game()
                return

            elif choice == '1':
                self._play_driver_game()
            elif choice == '2':
                self._play_constructor_game()
            elif choice == '3':
                self._play_circuit_game()
            elif choice == '4':
                clear_screen()
                self.stats.display_stats()
                # Export option
                exp = get_valid_input(
                    "  Export stats to file? (y/n): ",
                    ['y', 'n', 'yes', 'no']
                )
                if exp and exp.lower() in ('y', 'yes'):
                    path = self.stats.export_stats()
                    if path:
                        print_success(f"Stats exported to {path}")
                pause()
            elif choice == '5':
                clear_screen()
                self.leaderboard.display_leaderboard()
                pause()
            elif choice == '6':
                clear_screen()
                self.achievements.display_all_achievements()
                pause()
            elif choice == '7':
                self._show_help()
            elif choice == '8':
                self._change_player()
            elif choice == '0' and save_info:
                self._resume_saved_game()

    def _select_difficulty(self):
        """
        Show difficulty selection sub-menu.

        Returns
        -------
        str
            Selected difficulty ('easy', 'medium', 'hard').
        """
        display_subheader("SELECT DIFFICULTY")
        print(f"  {Fore.GREEN}1. Easy{Style.RESET_ALL}    — Current drivers only (~20 drivers)")
        print(f"  {Fore.YELLOW}2. Medium{Style.RESET_ALL}  — Drivers from 2010 onwards (~100 drivers)")
        print(f"  {Fore.RED}3. Hard{Style.RESET_ALL}    — All drivers from 2005 onwards (~150+ drivers)")
        print()

        choice = get_valid_input("  Select difficulty: ", ['1', '2', '3'])
        if choice == '1':
            return 'easy'
        elif choice == '3':
            return 'hard'
        return 'medium'

    def _select_challenge(self):
        """
        Show challenge type selection.

        Returns
        -------
        str
            'daily' or 'random'.
        """
        display_subheader("CHALLENGE TYPE")
        print(f"  {Fore.CYAN}1. Daily Challenge{Style.RESET_ALL}  — Same for everyone today")
        print(f"  {Fore.MAGENTA}2. Random Challenge{Style.RESET_ALL} — Random selection")
        print()

        choice = get_valid_input("  Select challenge: ", ['1', '2'])
        return 'daily' if choice == '1' else 'random'

    def _get_drivers_for_difficulty(self, difficulty):
        """
        Get the driver pool based on difficulty level.

        Parameters
        ----------
        difficulty : str
            'easy', 'medium', or 'hard'.

        Returns
        -------
        list of dict
            Filtered driver list.
        """
        if difficulty == 'easy':
            drivers = self.data.get_current_drivers()
            if not drivers:
                print_warning("No current drivers found. Using all drivers.")
                drivers = self.data.drivers
            return drivers
        elif difficulty == 'medium':
            drivers = self.data.get_drivers_from_year(2010)
            if not drivers:
                print_warning("No 2010+ drivers found. Using all drivers.")
                drivers = self.data.drivers
            return drivers
        else:
            return self.data.drivers

    def _play_driver_game(self):
        """Launch a Driver Guess game."""
        clear_screen()
        display_header("DRIVER GUESS")

        difficulty = self._select_difficulty()
        challenge = self._select_challenge()

        drivers = self._get_drivers_for_difficulty(difficulty)
        print_info(f"Pool: {len(drivers)} drivers ({difficulty} difficulty)")
        print()

        game = DriverGame(
            drivers=drivers,
            all_drivers=self.data.drivers,
            difficulty=difficulty,
            challenge_type=challenge,
            player_name=self.player_name,
            current_streak=self.stats.stats.get('current_streak', 0),
            best_streak=self.stats.stats.get('best_streak', 0)
        )

        result = game.play()
        if result:
            self._handle_game_result('driver', result)
        pause()

    def _play_constructor_game(self):
        """Launch a Constructor Guess game."""
        clear_screen()
        display_header("CONSTRUCTOR GUESS")

        challenge = self._select_challenge()

        constructors = self.data.constructors
        if not constructors:
            print_error("No constructor data available!")
            pause()
            return

        print_info(f"Pool: {len(constructors)} constructors")
        print()

        game = ConstructorGame(
            constructors=constructors,
            challenge_type=challenge,
            player_name=self.player_name,
            current_streak=self.stats.stats.get('current_streak', 0),
            best_streak=self.stats.stats.get('best_streak', 0)
        )

        result = game.play()
        if result:
            self._handle_game_result('constructor', result)
        pause()

    def _play_circuit_game(self):
        """Launch a Circuit Guess game."""
        clear_screen()
        display_header("CIRCUIT GUESS")

        challenge = self._select_challenge()

        circuits = self.data.circuits
        if not circuits:
            print_error("No circuit data available!")
            pause()
            return

        print_info(f"Pool: {len(circuits)} circuits")
        print()

        game = CircuitGame(
            circuits=circuits,
            challenge_type=challenge,
            player_name=self.player_name,
            current_streak=self.stats.stats.get('current_streak', 0),
            best_streak=self.stats.stats.get('best_streak', 0)
        )

        result = game.play()
        if result:
            self._handle_game_result('circuit', result)
        pause()

    def _handle_game_result(self, mode, result):
        """
        Process game results — update stats, leaderboard, achievements.

        Parameters
        ----------
        mode : str
            Game mode ('driver', 'constructor', 'circuit').
        result : dict
            Game result dictionary.
        """
        # If game was saved, do not treat as finished or update stats/leaderboard
        if result.get('saved'):
            return

        won = result['won']
        guesses = result['guesses']
        score = result['score']
        hints = result['hints']

        # Update statistics
        self.stats.update_stats(mode, won, guesses, score, hints)

        # Update leaderboard
        self.leaderboard.update_leaderboard(
            player_name=self.player_name,
            won=won,
            guesses_used=guesses,
            best_streak=self.stats.stats['best_streak'],
            score=score
        )

        # Check achievements
        new_achievements = self.achievements.check_achievements()
        if new_achievements:
            self.achievements.display_new_achievements(new_achievements)

        # Show rank
        rank = self.leaderboard.get_player_rank(self.player_name)
        if rank:
            print(f"\n  {Fore.CYAN}Your leaderboard rank: "
                  f"{Fore.YELLOW}#{rank}{Style.RESET_ALL}")

        # Show streak info
        streak = self.stats.stats['current_streak']
        if streak > 1:
            print(f"  {Fore.GREEN}🔥 Win streak: {streak}!{Style.RESET_ALL}")

        # Delete save file after completing a game
        self.save_manager.delete_save()

    def _resume_saved_game(self):
        """Resume a previously saved game."""
        state = self.save_manager.load_game()
        if state is None:
            print_error("Could not load saved game.")
            pause()
            return

        clear_screen()
        display_header(f"RESUMING {state.game_mode.upper()} GAME")
        print_info(f"Welcome back, {state.player_name}. Restoring your progress...")

        # Update current player name to the one in the save file
        self.player_name = state.player_name
        self.stats.stats['player_name'] = state.player_name

        mode = state.game_mode
        challenge_type = getattr(state, 'challenge_type', 'random')

        if mode == 'driver':
            drivers = self._get_drivers_for_difficulty(state.difficulty)
            game = DriverGame(
                drivers=drivers,
                all_drivers=self.data.drivers,
                difficulty=state.difficulty,
                challenge_type=challenge_type,
                player_name=state.player_name,
                current_streak=state.current_streak,
                best_streak=state.best_streak
            )
            game.load_state(state)
            result = game.play()
            if result:
                self._handle_game_result('driver', result)

        elif mode == 'constructor':
            game = ConstructorGame(
                constructors=self.data.constructors,
                challenge_type=challenge_type,
                player_name=state.player_name,
                current_streak=state.current_streak,
                best_streak=state.best_streak
            )
            game.load_state(state)
            result = game.play()
            if result:
                self._handle_game_result('constructor', result)

        elif mode == 'circuit':
            game = CircuitGame(
                circuits=self.data.circuits,
                challenge_type=challenge_type,
                player_name=state.player_name,
                current_streak=state.current_streak,
                best_streak=state.best_streak
            )
            game.load_state(state)
            result = game.play()
            if result:
                self._handle_game_result('circuit', result)

        else:
            print_error(f"Unknown game mode '{mode}' in save file.")
        
        pause()

    def _change_player(self):
        """Change the current player name."""
        clear_screen()
        display_header("CHANGE PLAYER")
        print(f"  {Fore.WHITE}Current player: "
              f"{Fore.CYAN}{self.player_name}{Style.RESET_ALL}\n")

        new_name = get_player_name()
        if new_name:
            self.player_name = new_name
            self.stats.stats['player_name'] = new_name
            self.stats.save_stats()
            print_success(f"Player changed to {new_name}!")
        pause()

    def _show_help(self):
        """Display the help page with rules and explanations."""
        clear_screen()
        display_header("HELP & RULES")

        help_text = f"""
  {Fore.WHITE}{Style.BRIGHT}HOW TO PLAY{Style.RESET_ALL}
  {Fore.WHITE}FormulaGuess is a Wordle-style guessing game themed around
  Formula One. Try to identify the secret F1 driver, constructor,
  or circuit in 6 guesses or fewer!{Style.RESET_ALL}

  {Fore.RED}{'─' * 55}{Style.RESET_ALL}

  {Fore.WHITE}{Style.BRIGHT}GAME MODES{Style.RESET_ALL}
  {Fore.GREEN}🏎  Driver Guess{Style.RESET_ALL}     — Guess an F1 driver
  {Fore.GREEN}🏗  Constructor Guess{Style.RESET_ALL} — Guess an F1 team
  {Fore.GREEN}🏁  Circuit Guess{Style.RESET_ALL}     — Guess an F1 circuit

  {Fore.RED}{'─' * 55}{Style.RESET_ALL}

  {Fore.WHITE}{Style.BRIGHT}SYMBOLS{Style.RESET_ALL}
  {Fore.GREEN}✅ Match{Style.RESET_ALL}     — Attribute matches exactly
  {Fore.RED}❌ Wrong{Style.RESET_ALL}     — Attribute does not match
  {Fore.YELLOW}⬆ Higher{Style.RESET_ALL}    — Target value is HIGHER than your guess
  {Fore.YELLOW}⬇ Lower{Style.RESET_ALL}     — Target value is LOWER than your guess

  {Fore.RED}{'─' * 55}{Style.RESET_ALL}

  {Fore.WHITE}{Style.BRIGHT}HINTS{Style.RESET_ALL}
  {Fore.WHITE}Hints are revealed progressively as you use guesses:
  • Guess 3: Small hint (e.g., nationality first letter)
  • Guess 4: Medium hint (e.g., current team)
  • Guess 5: Large hint (e.g., win count range){Style.RESET_ALL}

  {Fore.RED}{'─' * 55}{Style.RESET_ALL}

  {Fore.WHITE}{Style.BRIGHT}SCORING{Style.RESET_ALL}
  {Fore.WHITE}Guess 1: {Fore.GREEN}100 pts{Style.RESET_ALL}  |  {Fore.WHITE}Guess 2: {Fore.GREEN}80 pts{Style.RESET_ALL}
  {Fore.WHITE}Guess 3: {Fore.YELLOW}60 pts{Style.RESET_ALL}   |  {Fore.WHITE}Guess 4: {Fore.YELLOW}40 pts{Style.RESET_ALL}
  {Fore.WHITE}Guess 5: {Fore.RED}20 pts{Style.RESET_ALL}   |  {Fore.WHITE}Guess 6: {Fore.RED}10 pts{Style.RESET_ALL}
  {Fore.WHITE}Failed:  {Fore.RED}0 pts{Style.RESET_ALL}

  {Fore.RED}{'─' * 55}{Style.RESET_ALL}

  {Fore.WHITE}{Style.BRIGHT}DIFFICULTY LEVELS{Style.RESET_ALL}
  {Fore.GREEN}Easy{Style.RESET_ALL}   — Current F1 drivers only (~20)
  {Fore.YELLOW}Medium{Style.RESET_ALL} — Drivers from 2010 onwards (~100)
  {Fore.RED}Hard{Style.RESET_ALL}   — All drivers from 2005 onwards (~150+)

  {Fore.RED}{'─' * 55}{Style.RESET_ALL}

  {Fore.WHITE}{Style.BRIGHT}SEARCH TIPS{Style.RESET_ALL}
  {Fore.WHITE}• Type partial names: "ham" → Hamilton
  • Case insensitive: "MAX" = "max" = "Max"
  • First or last name works: "lewis" or "hamilton"
  • Type 'quit' to abandon a game{Style.RESET_ALL}
"""
        print(help_text)
        pause()

    def _exit_game(self):
        """Handle game exit with confirmation."""
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}")
        print("  ╔═══════════════════════════════════════╗")
        print("  ║     Thanks for playing FormulaGuess!  ║")
        print("  ║          See you on track!            ║")
        print("  ╚═══════════════════════════════════════╝")
        print(f"{Style.RESET_ALL}")
