# FormulaGuess 🏎️

A **terminal-based Formula 1 Wordle-inspired guessing game** built entirely in Python. Test your Formula 1 knowledge by identifying **drivers, constructors, and circuits** using attribute-based comparisons, progressive hints, multiple difficulty levels, achievements, leaderboards, and more.

---

## Features

* 🏁 **Driver Guess Mode**

  * Guess the mystery Formula 1 driver.
  * Compare attributes such as:

    * Nationality
    * Team
    * Championships
    * Wins
    * Podiums
    * Pole Positions
    * Driver Number
    * Age
    * Debut Season
  * Progressive hint system.

* 🏎️ **Constructor Guess Mode**

  * Guess Formula 1 constructors using historical and team information.

* 🛣️ **Circuit Guess Mode**

  * Identify famous Formula 1 circuits from their characteristics.

* 🎯 **Daily Challenge**

  * Everyone gets the same challenge each day.

* 🎲 **Random Challenge**

  * Unlimited randomly generated games.

* 📊 Multiple Difficulty Levels

  * Easy
  * Medium
  * Hard

* 💾 Save & Resume Games

* 📈 Player Statistics

  * Games played
  * Win percentage
  * Guess distribution
  * Streak tracking
  * Best streak
  * Average guesses

* 🏆 Leaderboards

* 🎖️ Achievement System

* 🌈 Colored Terminal Interface (Colorama)

* 🔍 Smart/Fuzzy Search for driver names

---

## Project Structure

```text
FormulaGuess/
│
├── main.py                 # Entry point
├── menu.py                 # Main menu
├── driver_game.py          # Driver mode
├── constructor_game.py     # Constructor mode
├── circuit_game.py         # Circuit mode
├── csv_loader.py           # Loads CSV data
├── leaderboard.py          # Leaderboards
├── stats.py                # Player statistics
├── achievements.py         # Achievement system
├── savegame.py             # Save/load functionality
├── utilities.py            # UI and helper functions
│
├── data/
│   ├── drivers.csv
│   ├── constructors.csv
│   ├── circuits.csv
│   ├── teams.csv
│   ├── race_winners.csv
│   └── season_champions.csv
│
└── README.md
```

---

## Requirements

* Python **3.10+**
* Colorama

Install dependencies:

```bash
pip install colorama
```

---

## Running the Game

Clone the repository:

```bash
git clone https://github.com/yourusername/FormulaGuess.git
```

Navigate to the project:

```bash
cd FormulaGuess
```

Run:

```bash
python main.py
```

---

## Gameplay

You have **6 attempts** to guess the correct answer.

Each guess compares several attributes with the hidden target.

Examples include:

* Team
* Nationality
* Championships
* Wins
* Age
* Debut Season

As you play:

* Correct attributes help narrow the search.
* Progressive hints unlock after several incorrect guesses.
* Your score depends on accuracy and number of guesses used.

---

## Game Modes

### Driver Guess

Identify a Formula 1 driver from attribute comparisons.

### Constructor Guess

Guess the Formula 1 constructor using team statistics and history.

### Circuit Guess

Guess famous Formula 1 circuits using location and circuit characteristics.

---

## Data

The game uses locally stored CSV files containing Formula 1 data, including:

* Modern Formula 1 drivers
* Constructors
* Teams
* Circuits
* Race winners
* Season champions

Everything runs **offline** once the data files are present.

---

## Statistics & Progress

Your progress is automatically tracked, including:

* Games Played
* Wins
* Win Rate
* Current Streak
* Best Streak
* Guess Distribution
* Average Guesses

Games can also be saved and resumed later.

---

## Technologies Used

* Python
* CSV
* Object-Oriented Programming (OOP)
* File Handling
* Colorama
* Random
* Datetime
* Pickle
* Terminal UI

---

## Educational Concepts Demonstrated

This project showcases:

* Object-Oriented Programming
* Classes and Inheritance
* Modular Programming
* File Handling
* CSV Processing
* Data Validation
* Search Algorithms
* User Input Handling
* Terminal Interface Design
* Game Logic
* State Management

---

## Screenshots

Add screenshots of:

* Main Menu
* Driver Guess Mode
* Constructor Mode
* Circuit Mode
* Statistics
* Leaderboard

---

## Future Improvements

* More Formula 1 seasons
* Historical driver mode
* Multiplayer mode
* Time attack mode
* Custom challenges
* Online leaderboards
* Achievement expansions
* Additional statistics

---

## Contributing

Contributions, feature requests, and bug reports are welcome.

1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Open a Pull Request.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

* Formula 1 for the inspiration.
* The Formula 1 community for historical data and statistics.
* Python's open-source ecosystem for making projects like this possible.

---

**FormulaGuess** combines the strategy of Wordle with the excitement of Formula 1, challenging players to use racing knowledge, logic, and deduction to identify drivers, constructors, and circuits in as few guesses as possible.
