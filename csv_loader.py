"""
csv_loader.py
=============
Loads all CSV game data files into memory.
Demonstrates CSV file handling with the csv module,
data validation, and error handling.
"""

import csv
import os
from utilities import safe_int, safe_float


# ── Data directory path ─────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


class CSVLoader:
    """
    Loads and validates CSV data files for FormulaGuess.

    All data is loaded once at startup and stored in memory
    for fast access during gameplay. CSV files are never modified.

    Attributes
    ----------
    drivers : list of dict
        All F1 drivers from the dataset.
    teams : list of dict
        All F1 constructors/teams.
    circuits : list of dict
        All F1 circuits.
    constructors : list of dict
        Extended constructor data.
    season_champions : list of dict
        Season champion records.
    race_winners : list of dict
        Race winner records.
    """

    def __init__(self, data_dir=None):
        """
        Initialize CSVLoader and load all data files.

        Parameters
        ----------
        data_dir : str, optional
            Path to the data directory. Defaults to ./data/.
        """
        self.data_dir = data_dir or DATA_DIR
        self.drivers = []
        self.teams = []
        self.circuits = []
        self.constructors = []
        self.season_champions = []
        self.race_winners = []

    def load_all(self):
        """
        Load all CSV data files.

        Returns
        -------
        bool
            True if all critical files loaded successfully.
        """
        success = True

        # Load each CSV file
        self.drivers = self._load_csv("drivers.csv")
        if not self.drivers:
            print("ERROR: Could not load drivers.csv — this file is required!")
            success = False

        self.teams = self._load_csv("teams.csv")
        if not self.teams:
            print("WARNING: Could not load teams.csv")

        self.circuits = self._load_csv("circuits.csv")
        if not self.circuits:
            print("WARNING: Could not load circuits.csv")

        self.constructors = self._load_csv("constructors.csv")
        if not self.constructors:
            # Fall back to teams data
            self.constructors = self.teams

        self.season_champions = self._load_csv("season_champions.csv")
        self.race_winners = self._load_csv("race_winners.csv")

        # Convert numeric fields
        if self.drivers:
            self._convert_driver_numerics()

        if self.teams:
            self._convert_team_numerics()

        if self.circuits:
            self._convert_circuit_numerics()

        return success

    def _load_csv(self, filename):
        """
        Load a single CSV file and return a list of dictionaries.

        Parameters
        ----------
        filename : str
            Name of the CSV file (relative to data directory).

        Returns
        -------
        list of dict
            Each row as a dictionary, or empty list on failure.
        """
        filepath = os.path.join(self.data_dir, filename)
        try:
            if not os.path.exists(filepath):
                return []

            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                data = []
                for row_num, row in enumerate(reader, start=2):
                    # Strip whitespace from keys and values
                    cleaned = {}
                    for key, value in row.items():
                        if key is not None:
                            cleaned[key.strip()] = value.strip() if value else ''
                    data.append(cleaned)
                return data

        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return []
        except csv.Error as e:
            print(f"CSV error in {filename}: {e}")
            return []
        except UnicodeDecodeError:
            # Try with latin-1 encoding as fallback
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    reader = csv.DictReader(f)
                    return [
                        {k.strip(): (v.strip() if v else '')
                         for k, v in row.items() if k is not None}
                        for row in reader
                    ]
            except Exception as e:
                print(f"Encoding error in {filename}: {e}")
                return []
        except Exception as e:
            print(f"Unexpected error loading {filename}: {e}")
            return []

    def _convert_driver_numerics(self):
        """Convert numeric string fields to integers for drivers."""
        numeric_fields = [
            'Birth Year', 'Age', 'Driver Number', 'Debut Season',
            'Championships', 'Race Starts', 'Wins', 'Podiums',
            'Pole Positions', 'Fastest Laps', 'Highest Championship Finish'
        ]
        float_fields = ['Points']

        for driver in self.drivers:
            for field in numeric_fields:
                if field in driver:
                    driver[field] = safe_int(driver[field])
            for field in float_fields:
                if field in driver:
                    driver[field] = safe_float(driver[field])

    def _convert_team_numerics(self):
        """Convert numeric string fields to integers for teams."""
        numeric_fields = ['Founded', 'Championships', 'Race Wins']
        for team in self.teams:
            for field in numeric_fields:
                if field in team:
                    team[field] = safe_int(team[field])

    def _convert_circuit_numerics(self):
        """Convert numeric string fields for circuits."""
        for circuit in self.circuits:
            if 'Corners' in circuit:
                circuit['Corners'] = safe_int(circuit['Corners'])
            if 'First GP' in circuit:
                circuit['First GP'] = safe_int(circuit['First GP'])
            if 'Length' in circuit:
                # Keep as string with units, but also store numeric
                length_str = circuit['Length']
                try:
                    # Extract numeric part (e.g., "5.412 km" -> 5.412)
                    numeric_part = ''.join(
                        c for c in length_str.split()[0]
                        if c.isdigit() or c == '.'
                    )
                    circuit['Length_km'] = safe_float(numeric_part)
                except (IndexError, ValueError):
                    circuit['Length_km'] = 0.0

    # ── Filtering Methods ───────────────────────────────────────────────────

    def get_current_drivers(self):
        """Get only drivers currently active in F1."""
        return [d for d in self.drivers
                if d.get('Current Status', '').lower() == 'active']

    def get_drivers_from_year(self, year):
        """Get drivers who debuted in or after a given year."""
        return [d for d in self.drivers
                if safe_int(d.get('Debut Season', 0)) >= year]

    def get_active_circuits(self):
        """Get only circuits currently on the F1 calendar."""
        return [c for c in self.circuits
                if c.get('Current Status', '').lower() == 'active']

    def get_active_teams(self):
        """Get only teams currently competing in F1."""
        return [t for t in self.constructors
                if t.get('Current Status', '').lower() in ('active', '')]

    # ── Search Methods ──────────────────────────────────────────────────────

    def find_driver(self, name):
        """
        Find a driver by exact name match.

        Parameters
        ----------
        name : str
            The driver's full name.

        Returns
        -------
        dict or None
            The driver's data dictionary, or None if not found.
        """
        name_lower = name.strip().lower()
        for driver in self.drivers:
            if driver.get('Full Name', '').lower() == name_lower:
                return driver
        return None

    def find_team(self, name):
        """Find a team by exact name match."""
        name_lower = name.strip().lower()
        for team in self.constructors:
            if team.get('Team Name', '').lower() == name_lower:
                return team
        return None

    def find_circuit(self, name):
        """Find a circuit by exact name match."""
        name_lower = name.strip().lower()
        for circuit in self.circuits:
            if circuit.get('Circuit Name', '').lower() == name_lower:
                return circuit
        return None

    # ── Statistics ──────────────────────────────────────────────────────────

    def get_data_summary(self):
        """
        Get a summary of loaded data.

        Returns
        -------
        dict
            Counts of each data type loaded.
        """
        return {
            'drivers': len(self.drivers),
            'teams': len(self.teams),
            'circuits': len(self.circuits),
            'constructors': len(self.constructors),
            'season_champions': len(self.season_champions),
            'race_winners': len(self.race_winners)
        }
