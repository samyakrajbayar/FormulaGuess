"""
savegame.py
===========
Save and load game state using pickle (binary file handling).
Demonstrates Python's pickle module for serialization/deserialization
of complex objects to/from binary files.
"""

import pickle
import os
from datetime import datetime


# ── Default save file path ──────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SAVE_FILE = os.path.join(DATA_DIR, "savegame.dat")


class GameState:
    """
    Represents a complete game state that can be saved/loaded.

    Attributes
    ----------
    player_name : str
        Name of the current player.
    game_mode : str
        Current game mode ('driver', 'constructor', 'circuit').
    target : dict
        The target item to guess (driver/constructor/circuit data).
    remaining_guesses : int
        Number of guesses remaining.
    guess_history : list
        List of previous guesses (each is a dict).
    current_streak : int
        Current win streak.
    best_streak : int
        Best win streak achieved.
    hints_used : int
        Number of hints revealed so far.
    difficulty : str
        Difficulty level ('easy', 'medium', 'hard').
    timestamp : str
        When the game was saved.
    score : int
        Current accumulated score.
    """

    def __init__(self, player_name="Player", game_mode="driver",
                 target=None, remaining_guesses=6, guess_history=None,
                 current_streak=0, best_streak=0, hints_used=0,
                 difficulty="medium", score=0):
        self.player_name = player_name
        self.game_mode = game_mode
        self.target = target or {}
        self.remaining_guesses = remaining_guesses
        self.guess_history = guess_history or []
        self.current_streak = current_streak
        self.best_streak = best_streak
        self.hints_used = hints_used
        self.difficulty = difficulty
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.score = score

    def __str__(self):
        return (f"GameState(player={self.player_name}, mode={self.game_mode}, "
                f"guesses_left={self.remaining_guesses}, streak={self.current_streak})")


class SaveManager:
    """
    Manages saving and loading game state using pickle.

    Uses binary file I/O to serialize GameState objects
    to a .dat file, demonstrating Python's pickle module.
    """

    def __init__(self, save_path=None):
        """
        Initialize SaveManager with a save file path.

        Parameters
        ----------
        save_path : str, optional
            Path to the save file. Defaults to data/savegame.dat.
        """
        self.save_path = save_path or SAVE_FILE
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

    def save_game(self, game_state):
        """
        Save a GameState object to binary file using pickle.

        Parameters
        ----------
        game_state : GameState
            The game state to save.

        Returns
        -------
        bool
            True if saved successfully, False otherwise.
        """
        try:
            game_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.save_path, 'wb') as f:
                pickle.dump(game_state, f)
            return True
        except (IOError, pickle.PicklingError) as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self):
        """
        Load a GameState object from binary file using pickle.

        Returns
        -------
        GameState or None
            The loaded game state, or None if no save exists or load fails.
        """
        if not self.has_save():
            return None
        try:
            with open(self.save_path, 'rb') as f:
                game_state = pickle.load(f)
            # Validate the loaded object
            if isinstance(game_state, GameState):
                return game_state
            else:
                print("Warning: Save file contains invalid data.")
                return None
        except (IOError, pickle.UnpicklingError, EOFError,
                AttributeError, ImportError) as e:
            print(f"Error loading save: {e}")
            return None

    def delete_save(self):
        """
        Delete the save file.

        Returns
        -------
        bool
            True if deleted successfully, False otherwise.
        """
        try:
            if os.path.exists(self.save_path):
                os.remove(self.save_path)
                return True
            return False
        except IOError as e:
            print(f"Error deleting save: {e}")
            return False

    def has_save(self):
        """
        Check if a save file exists.

        Returns
        -------
        bool
            True if save file exists, False otherwise.
        """
        return os.path.exists(self.save_path)

    def get_save_info(self):
        """
        Get summary info about the current save file without fully loading.

        Returns
        -------
        dict or None
            Dictionary with save info, or None if no save exists.
        """
        state = self.load_game()
        if state is None:
            return None
        return {
            'player_name': state.player_name,
            'game_mode': state.game_mode,
            'remaining_guesses': state.remaining_guesses,
            'guesses_made': len(state.guess_history),
            'streak': state.current_streak,
            'difficulty': state.difficulty,
            'timestamp': state.timestamp,
            'score': state.score
        }
