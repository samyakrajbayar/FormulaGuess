"""
driver_game.py
==============
Driver Guess game mode for FormulaGuess.
Player guesses an F1 driver by comparing attributes.
Supports difficulty levels, daily/random challenges,
and progressive hints.
"""

import random
from datetime import date
from utilities import (
    display_header, display_subheader, display_divider,
    display_comparison_table, display_guess_result, display_score,
    fuzzy_search, select_from_matches, calculate_score,
    print_success, print_error, print_warning, print_info, print_hint,
    pause, Fore, Style, safe_int
)


# ── Comparison attributes for Driver mode ───────────────────────────────────
# Each tuple: (Display Name, CSV Key, Is Numeric)
DRIVER_ATTRIBUTES = [
    ("Nationality",       "Nationality",           False),
    ("Current Team",      "Current Team",           False),
    ("Championships",     "Championships",          True),
    ("Wins",              "Wins",                   True),
    ("Podiums",           "Podiums",                True),
    ("Pole Positions",    "Pole Positions",         True),
    ("Driver Number",     "Driver Number",          True),
    ("Age",               "Age",                    True),
    ("Debut Season",      "Debut Season",           True),
]


class DriverGame:
    """
    Driver Guess game mode.

    The computer randomly selects an F1 driver. The player has
    6 guesses to identify the driver by comparing attributes.
    Progressive hints are revealed at guesses 3, 4, and 5.

    Parameters
    ----------
    drivers : list of dict
        All available drivers for this difficulty.
    all_drivers : list of dict
        Complete driver list (for search validation).
    difficulty : str
        Difficulty level ('easy', 'medium', 'hard').
    challenge_type : str
        'daily' for date-seeded or 'random'.
    """

    MAX_GUESSES = 6

    def __init__(self, drivers, all_drivers=None, difficulty="medium",
                 challenge_type="random", player_name="Player",
                 current_streak=0, best_streak=0):
        self.drivers = drivers
        self.all_drivers = all_drivers or drivers
        self.difficulty = difficulty
        self.challenge_type = challenge_type
        self.player_name = player_name
        self.current_streak = current_streak
        self.best_streak = best_streak
        self.target = None
        self.guesses = []
        self.guess_count = 0
        self.won = False
        self.hints_given = 0
        self.score = 0

    def select_target(self):
        """
        Select the target driver based on challenge type.

        For 'daily' challenge, uses today's date as seed
        so everyone gets the same driver on the same day.
        For 'random', picks a random driver.
        """
        if self.target:
            return True

        if not self.drivers:
            print_error("No drivers available for this difficulty level!")
            return False

        if self.challenge_type == "daily":
            # Use today's date as seed for consistent daily challenge
            seed = date.today().toordinal()
            rng = random.Random(seed)
            self.target = rng.choice(self.drivers)
        else:
            self.target = random.choice(self.drivers)

        return True

    def play(self):
        """
        Main game loop for Driver Guess mode.

        Returns
        -------
        dict
            Game result with keys: won, guesses, score, hints, target, saved.
        """
        if not self.select_target():
            return None

        # Display game header
        display_header("DRIVER GUESS")
        diff_display = self.difficulty.upper()
        challenge_display = self.challenge_type.upper()
        print(f"  {Fore.CYAN}Difficulty: {Fore.WHITE}{diff_display}  "
              f"{Fore.CYAN}Challenge: {Fore.WHITE}{challenge_display}{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}Guess the F1 driver in {self.MAX_GUESSES} attempts!{Style.RESET_ALL}")
        display_divider()

        # If resuming a saved game, replay history of comparisons first
        if self.guess_count > 0:
            print_info(f"Replaying your previous {self.guess_count} guesses:")
            for i, g in enumerate(self.guesses, 1):
                display_guess_result(i, self.MAX_GUESSES, g['Full Name'])
                display_comparison_table(g, self.target, DRIVER_ATTRIBUTES)
            display_divider()

        while self.guess_count < self.MAX_GUESSES and not self.won:
            # Show hint if applicable (from guess 3 onwards)
            self._show_hint()

            # Get player's guess
            guessed_driver = self._get_guess()
            if guessed_driver is None:
                # Player quit
                print_warning("Game abandoned.")
                return {
                    'won': False,
                    'guesses': self.guess_count,
                    'score': 0,
                    'hints': self.hints_given,
                    'target': self.target.get('Full Name', 'Unknown')
                }

            if guessed_driver == 'save':
                # Save game
                from savegame import GameState, SaveManager
                state = GameState(
                    player_name=self.player_name,
                    game_mode='driver',
                    target=self.target,
                    remaining_guesses=self.MAX_GUESSES - self.guess_count,
                    guess_history=self.guesses,
                    current_streak=self.current_streak,
                    best_streak=self.best_streak,
                    hints_used=self.hints_given,
                    difficulty=self.difficulty,
                    score=self.score
                )
                # Store extra challenge info in state for consistency
                state.challenge_type = self.challenge_type
                
                sm = SaveManager()
                if sm.save_game(state):
                    print_success("Game saved successfully! You can resume it from the main menu.")
                else:
                    print_error("Failed to save game.")
                return {'saved': True}

            self.guess_count += 1
            self.guesses.append(guessed_driver)

            # Check if correct
            if guessed_driver.get('Full Name', '').lower() == \
               self.target.get('Full Name', '').lower():
                self.won = True
                self.score = calculate_score(self.guess_count)
                display_guess_result(self.guess_count, self.MAX_GUESSES,
                                     guessed_driver['Full Name'], won=True)
                display_score(self.guess_count, self.score)
                break

            # Show comparison table
            display_guess_result(self.guess_count, self.MAX_GUESSES,
                                 guessed_driver['Full Name'])
            display_comparison_table(guessed_driver, self.target,
                                     DRIVER_ATTRIBUTES)

        # Game over — reveal answer if lost
        if not self.won:
            print(f"\n  {Fore.RED}{Style.BRIGHT}Game Over!{Style.RESET_ALL}")
            print(f"  {Fore.WHITE}The correct driver was: "
                  f"{Fore.GREEN}{Style.BRIGHT}"
                  f"{self.target.get('Full Name', 'Unknown')}"
                  f"{Style.RESET_ALL}")

            # Show some target info
            team = self.target.get('Current Team', 'N/A')
            nat = self.target.get('Nationality', 'N/A')
            wins = self.target.get('Wins', 0)
            print(f"  {Fore.CYAN}Team: {team} | Nationality: {nat} | "
                  f"Wins: {wins}{Style.RESET_ALL}")

        return {
            'won': self.won,
            'guesses': self.guess_count,
            'score': self.score,
            'hints': self.hints_given,
            'target': self.target.get('Full Name', 'Unknown')
        }

    def _get_guess(self):
        """
        Get and validate the player's driver guess.

        Uses fuzzy search to find matching drivers.

        Returns
        -------
        dict or None
            The guessed driver's data, or None if player quits.
        """
        remaining = self.MAX_GUESSES - self.guess_count

        while True:
            try:
                print(f"\n  {Fore.CYAN}Attempts remaining: "
                      f"{Fore.WHITE}{remaining}{Style.RESET_ALL}")
                query = input(f"  {Fore.YELLOW}Enter driver name "
                              f"(or 'save', 'quit'): {Style.RESET_ALL}").strip()

                if not query:
                    print_error("Please enter a driver name.")
                    continue

                if query.lower() in ('quit', 'exit', 'q'):
                    return None

                if query.lower() == 'save':
                    return 'save'

                # Fuzzy search across all drivers
                matches = fuzzy_search(
                    query, self.all_drivers,
                    key_fields=['Full Name', 'Surname', 'Name']
                )

                if not matches:
                    print_error(f"No driver found matching '{query}'. Try again.")
                    continue

                # Let player select if multiple matches
                selected = select_from_matches(matches, display_field='Full Name')
                if selected is None:
                    continue

                # Check if already guessed
                already_guessed = any(
                    g.get('Full Name', '').lower() == selected.get('Full Name', '').lower()
                    for g in self.guesses
                )
                if already_guessed:
                    print_warning(f"You already guessed {selected['Full Name']}. Try someone else.")
                    continue

                return selected

            except (EOFError, KeyboardInterrupt):
                print()
                return None

    def _show_hint(self):
        """
        Show progressive hints based on current guess number.

        Guess 3: Nationality first letter
        Guess 4: Current team
        Guess 5: Win count range
        """
        if self.guess_count == 2:
            # Hint 1: Nationality first letter
            nat = self.target.get('Nationality', 'Unknown')
            if nat and nat != 'Unknown':
                print_hint(f"Nationality begins with '{nat[0]}'")
                self.hints_given += 1

        elif self.guess_count == 3:
            # Hint 2: Current team
            team = self.target.get('Current Team', 'Unknown')
            if team and team != 'Unknown':
                print_hint(f"Current constructor is {team}")
            else:
                # Fallback: debut decade
                debut = safe_int(self.target.get('Debut Season', 0))
                if debut > 0:
                    decade = (debut // 10) * 10
                    print_hint(f"Debuted in the {decade}s")
            self.hints_given += 1

        elif self.guess_count == 4:
            # Hint 3: Win count range
            wins = safe_int(self.target.get('Wins', 0))
            if wins == 0:
                print_hint("Has never won a Grand Prix")
            elif wins < 5:
                print_hint(f"Has won fewer than 5 races")
            elif wins < 20:
                print_hint(f"Has won between 5 and 20 races")
            elif wins < 50:
                print_hint(f"Has won between 20 and 50 races")
            else:
                print_hint(f"Has won more than 50 races")
            self.hints_given += 1

    def get_state(self):
        """
        Get the current game state for saving.

        Returns
        -------
        dict
            State dictionary suitable for SaveManager.
        """
        return {
            'game_mode': 'driver',
            'target': self.target,
            'guesses': self.guesses,
            'guess_count': self.guess_count,
            'won': self.won,
            'hints_given': self.hints_given,
            'difficulty': self.difficulty,
            'challenge_type': self.challenge_type,
        }

    def load_state(self, state):
        """
        Load a saved game state.

        Parameters
        ----------
        state : GameState or dict
            Previously saved game state.
        """
        if hasattr(state, 'target'):
            self.target = state.target
            self.guesses = state.guess_history
            self.guess_count = len(state.guess_history)
            self.won = False
            self.hints_given = state.hints_used
            self.difficulty = state.difficulty
            self.challenge_type = getattr(state, 'challenge_type', 'random')
            self.score = state.score
        else:
            self.target = state.get('target')
            self.guesses = state.get('guesses', [])
            self.guess_count = state.get('guess_count', 0)
            self.won = state.get('won', False)
            self.hints_given = state.get('hints_given', 0)
            self.difficulty = state.get('difficulty', 'medium')
            self.challenge_type = state.get('challenge_type', 'random')
