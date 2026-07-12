"""
circuit_game.py
===============
Circuit Guess game mode for FormulaGuess.
Player guesses an F1 circuit by comparing attributes.
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


# ── Comparison attributes for Circuit mode ──────────────────────────────────
CIRCUIT_ATTRIBUTES = [
    ("Country",           "Country",                False),
    ("Length",             "Length",                  False),
    ("Corners",           "Corners",                 True),
    ("First GP",          "First GP",                True),
    ("Current Status",    "Current Status",          False),
]


class CircuitGame:
    """
    Circuit Guess game mode.

    The computer randomly selects an F1 circuit. The player
    has 6 guesses to identify it by comparing attributes.

    Parameters
    ----------
    circuits : list of dict
        All available circuits.
    challenge_type : str
        'daily' or 'random'.
    """

    MAX_GUESSES = 6

    def __init__(self, circuits, challenge_type="random", player_name="Player",
                 current_streak=0, best_streak=0):
        self.circuits = circuits
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
        """Select the target circuit."""
        if self.target:
            return True

        if not self.circuits:
            print_error("No circuits available!")
            return False

        if self.challenge_type == "daily":
            seed = date.today().toordinal() + 2000
            rng = random.Random(seed)
            self.target = rng.choice(self.circuits)
        else:
            self.target = random.choice(self.circuits)

        return True

    def play(self):
        """
        Main game loop for Circuit Guess mode.

        Returns
        -------
        dict
            Game result with keys: won, guesses, score, hints, target, saved.
        """
        if not self.select_target():
            return None

        display_header("CIRCUIT GUESS")
        print(f"  {Fore.CYAN}Guess the F1 circuit in "
              f"{self.MAX_GUESSES} attempts!{Style.RESET_ALL}")
        display_divider()

        # If resuming a saved game, replay history of comparisons first
        if self.guess_count > 0:
            print_info(f"Replaying your previous {self.guess_count} guesses:")
            for i, g in enumerate(self.guesses, 1):
                display_guess_result(i, self.MAX_GUESSES, g['Circuit Name'])
                display_comparison_table(g, self.target, CIRCUIT_ATTRIBUTES)
            display_divider()

        while self.guess_count < self.MAX_GUESSES and not self.won:
            self._show_hint()
            guessed = self._get_guess()

            if guessed is None:
                print_warning("Game abandoned.")
                return {
                    'won': False, 'guesses': self.guess_count,
                    'score': 0, 'hints': self.hints_given,
                    'target': self.target.get('Circuit Name', 'Unknown')
                }

            if guessed == 'save':
                # Save game
                from savegame import GameState, SaveManager
                state = GameState(
                    player_name=self.player_name,
                    game_mode='circuit',
                    target=self.target,
                    remaining_guesses=self.MAX_GUESSES - self.guess_count,
                    guess_history=self.guesses,
                    current_streak=self.current_streak,
                    best_streak=self.best_streak,
                    hints_used=self.hints_given,
                    difficulty='medium',
                    score=self.score
                )
                state.challenge_type = self.challenge_type
                
                sm = SaveManager()
                if sm.save_game(state):
                    print_success("Game saved successfully! You can resume it from the main menu.")
                else:
                    print_error("Failed to save game.")
                return {'saved': True}

            self.guess_count += 1
            self.guesses.append(guessed)

            # Check if correct
            if guessed.get('Circuit Name', '').lower() == \
               self.target.get('Circuit Name', '').lower():
                self.won = True
                self.score = calculate_score(self.guess_count)
                display_guess_result(self.guess_count, self.MAX_GUESSES,
                                     guessed['Circuit Name'], won=True)
                display_score(self.guess_count, self.score)
                break

            # Show comparison
            display_guess_result(self.guess_count, self.MAX_GUESSES,
                                 guessed['Circuit Name'])
            display_comparison_table(guessed, self.target,
                                     CIRCUIT_ATTRIBUTES)

        if not self.won:
            print(f"\n  {Fore.RED}{Style.BRIGHT}Game Over!{Style.RESET_ALL}")
            print(f"  {Fore.WHITE}The correct circuit was: "
                  f"{Fore.GREEN}{Style.BRIGHT}"
                  f"{self.target.get('Circuit Name', 'Unknown')}"
                  f"{Style.RESET_ALL}")
            country = self.target.get('Country', 'N/A')
            corners = self.target.get('Corners', 'N/A')
            print(f"  {Fore.CYAN}Country: {country} | "
                  f"Corners: {corners}{Style.RESET_ALL}")

        return {
            'won': self.won, 'guesses': self.guess_count,
            'score': self.score, 'hints': self.hints_given,
            'target': self.target.get('Circuit Name', 'Unknown')
        }

    def _get_guess(self):
        """Get and validate the player's circuit guess."""
        remaining = self.MAX_GUESSES - self.guess_count

        while True:
            try:
                print(f"\n  {Fore.CYAN}Attempts remaining: "
                      f"{Fore.WHITE}{remaining}{Style.RESET_ALL}")
                query = input(f"  {Fore.YELLOW}Enter circuit name "
                              f"(or 'save', 'quit'): {Style.RESET_ALL}").strip()

                if not query:
                    print_error("Please enter a circuit name.")
                    continue
                if query.lower() in ('quit', 'exit', 'q'):
                    return None
                if query.lower() == 'save':
                    return 'save'

                matches = fuzzy_search(
                    query, self.circuits,
                    key_fields=['Circuit Name', 'Country']
                )

                if not matches:
                    print_error(f"No circuit found matching '{query}'.")
                    continue

                selected = select_from_matches(matches,
                                               display_field='Circuit Name')
                if selected is None:
                    continue

                # Check already guessed
                already = any(
                    g.get('Circuit Name', '').lower() == selected.get('Circuit Name', '').lower()
                    for g in self.guesses
                )
                if already:
                    print_warning(f"You already guessed {selected['Circuit Name']}.")
                    continue

                return selected

            except (EOFError, KeyboardInterrupt):
                print()
                return None

    def _show_hint(self):
        """Show progressive hints for circuit mode."""
        if self.guess_count == 2:
            country = self.target.get('Country', 'Unknown')
            if country and country != 'Unknown':
                print_hint(f"Country begins with '{country[0]}'")
                self.hints_given += 1

        elif self.guess_count == 3:
            corners = safe_int(self.target.get('Corners', 0))
            if corners > 0:
                if corners < 12:
                    print_hint("Has fewer than 12 corners")
                elif corners < 18:
                    print_hint("Has between 12 and 18 corners")
                else:
                    print_hint("Has more than 18 corners")
            self.hints_given += 1

        elif self.guess_count == 4:
            status = self.target.get('Current Status', 'Unknown')
            if status:
                print_hint(f"Circuit status: {status}")
            self.hints_given += 1

    def get_state(self):
        """Get state for saving."""
        return {
            'game_mode': 'circuit',
            'target': self.target,
            'guesses': self.guesses,
            'guess_count': self.guess_count,
            'won': self.won,
            'hints_given': self.hints_given,
            'difficulty': 'medium',
            'challenge_type': self.challenge_type,
        }

    def load_state(self, state):
        """Load saved state."""
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
