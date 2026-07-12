"""
utilities.py
============
Shared utility functions for FormulaGuess.
Provides colored output, fuzzy searching, display helpers,
input validation, and comparison table rendering.
"""

import os
import sys
import time
import textwrap

# Reconfigure stdout/stderr to UTF-8 on Windows to prevent encoding crash with emojis
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# ── Colorama Setup ──────────────────────────────────────────────────────────
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback: define empty color constants so the game still runs
    class _FallbackFore:
        GREEN = RED = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ""
        LIGHTGREEN_EX = LIGHTRED_EX = LIGHTYELLOW_EX = LIGHTBLUE_EX = ""
        LIGHTCYAN_EX = LIGHTMAGENTA_EX = LIGHTWHITE_EX = ""
    class _FallbackBack:
        GREEN = RED = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ""
    class _FallbackStyle:
        BRIGHT = DIM = RESET_ALL = ""
    Fore = _FallbackFore()
    Back = _FallbackBack()
    Style = _FallbackStyle()


# ── Symbols ─────────────────────────────────────────────────────────────────
MATCH       = Fore.GREEN  + "✅ Match"      + Style.RESET_ALL
WRONG       = Fore.RED    + "❌ Wrong"      + Style.RESET_ALL
HIGHER      = Fore.YELLOW + "⬆ Higher"     + Style.RESET_ALL
LOWER       = Fore.YELLOW + "⬇ Lower"      + Style.RESET_ALL

MATCH_SHORT  = Fore.GREEN  + "✅" + Style.RESET_ALL
WRONG_SHORT  = Fore.RED    + "❌" + Style.RESET_ALL
HIGHER_SHORT = Fore.YELLOW + "⬆"  + Style.RESET_ALL
LOWER_SHORT  = Fore.YELLOW + "⬇"  + Style.RESET_ALL


# ── Screen Utilities ────────────────────────────────────────────────────────

def clear_screen():
    """Clear the terminal screen (cross-platform)."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pause(message="Press Enter to continue..."):
    """Pause and wait for user to press Enter."""
    input(f"\n{Fore.CYAN}{message}{Style.RESET_ALL}")


def slow_print(text, delay=0.02):
    """Print text character by character for dramatic effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


# ── Banner & Headers ────────────────────────────────────────────────────────

def display_banner():
    """Display the FormulaGuess ASCII art banner."""
    banner = f"""
{Fore.RED}{Style.BRIGHT}╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   {Fore.WHITE}███████╗ ██████╗ ██████╗ ███╗   ███╗██╗   ██╗██╗      █████╗ {Fore.RED}    ║
║   {Fore.WHITE}██╔════╝██╔═══██╗██╔══██╗████╗ ████║██║   ██║██║     ██╔══██╗{Fore.RED}    ║
║   {Fore.WHITE}█████╗  ██║   ██║██████╔╝██╔████╔██║██║   ██║██║     ███████║{Fore.RED}    ║
║   {Fore.WHITE}██╔══╝  ██║   ██║██╔══██╗██║╚██╔╝██║██║   ██║██║     ██╔══██║{Fore.RED}    ║
║   {Fore.WHITE}██║     ╚██████╔╝██║  ██║██║ ╚═╝ ██║╚██████╔╝███████╗██║  ██║{Fore.RED}    ║
║   {Fore.WHITE}╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝{Fore.RED}    ║
║                                                                    ║
║           {Fore.YELLOW}██████╗ ██╗   ██╗███████╗███████╗███████╗{Fore.RED}                ║
║           {Fore.YELLOW}██╔════╝ ██║   ██║██╔════╝██╔════╝██╔════╝{Fore.RED}               ║
║           {Fore.YELLOW}██║  ███╗██║   ██║█████╗  ███████╗███████╗{Fore.RED}               ║
║           {Fore.YELLOW}██║   ██║██║   ██║██╔══╝  ╚════██║╚════██║{Fore.RED}               ║
║           {Fore.YELLOW}╚██████╔╝╚██████╔╝███████╗███████║███████║{Fore.RED}               ║
║           {Fore.YELLOW} ╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚══════╝{Fore.RED}               ║
║                                                                    ║
║                 {Fore.CYAN}🏎  The Formula 1 Wordle Experience  🏁{Fore.RED}             ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def display_header(title):
    """Display a styled section header."""
    width = 60
    border = "═" * width
    padding = (width - len(title) - 2) // 2
    print(f"\n{Fore.RED}{Style.BRIGHT}╔{border}╗")
    print(f"║{' ' * padding} {Fore.WHITE}{title} {Fore.RED}{' ' * (width - padding - len(title) - 2)}║")
    print(f"╚{border}╝{Style.RESET_ALL}\n")


def display_subheader(title):
    """Display a smaller styled sub-header."""
    width = 50
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}┌{'─' * width}┐")
    padding = (width - len(title)) // 2
    print(f"│{' ' * padding}{title}{' ' * (width - padding - len(title))}│")
    print(f"└{'─' * width}┘{Style.RESET_ALL}\n")


def display_divider(char="─", width=60):
    """Display a horizontal divider line."""
    print(f"{Fore.RED}{char * width}{Style.RESET_ALL}")


# ── Color Printing ──────────────────────────────────────────────────────────

def print_success(message):
    """Print a success message in green."""
    print(f"{Fore.GREEN}{Style.BRIGHT}✅ {message}{Style.RESET_ALL}")


def print_error(message):
    """Print an error message in red."""
    print(f"{Fore.RED}{Style.BRIGHT}❌ {message}{Style.RESET_ALL}")


def print_warning(message):
    """Print a warning message in yellow."""
    print(f"{Fore.YELLOW}{Style.BRIGHT}⚠  {message}{Style.RESET_ALL}")


def print_info(message):
    """Print an informational message in cyan."""
    print(f"{Fore.CYAN}ℹ  {message}{Style.RESET_ALL}")


def print_hint(message):
    """Print a hint message in magenta."""
    print(f"{Fore.MAGENTA}{Style.BRIGHT}💡 HINT: {message}{Style.RESET_ALL}")


# ── Input Validation ────────────────────────────────────────────────────────

def get_valid_input(prompt, valid_options, allow_empty=False):
    """
    Get validated input from the user.

    Parameters
    ----------
    prompt : str
        The prompt message to display.
    valid_options : list
        List of acceptable inputs (as strings).
    allow_empty : bool
        Whether to accept empty input.

    Returns
    -------
    str
        The user's validated choice.
    """
    while True:
        try:
            choice = input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}").strip()
            if not choice and not allow_empty:
                print_error("Input cannot be empty. Please try again.")
                continue
            if choice.lower() in [opt.lower() for opt in valid_options]:
                return choice
            else:
                options_str = ", ".join(valid_options)
                print_error(f"Invalid choice. Valid options: {options_str}")
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Fore.YELLOW}Returning to menu...{Style.RESET_ALL}")
            return None


def get_player_name():
    """Prompt for and validate a player name."""
    while True:
        try:
            name = input(f"{Fore.CYAN}Enter your name: {Style.RESET_ALL}").strip()
            if not name:
                print_error("Name cannot be empty.")
                continue
            if len(name) > 30:
                print_error("Name must be 30 characters or fewer.")
                continue
            if not all(c.isalnum() or c in " _-" for c in name):
                print_error("Name can only contain letters, numbers, spaces, hyphens, and underscores.")
                continue
            return name
        except (EOFError, KeyboardInterrupt):
            return "Player"


# ── Fuzzy Search ────────────────────────────────────────────────────────────

def fuzzy_search(query, items, key_fields=None):
    """
    Flexible search function that matches partial strings
    against item names/attributes.

    Parameters
    ----------
    query : str
        Search query (e.g., "ham", "max", "charles").
    items : list of dict
        The items to search through.
    key_fields : list of str, optional
        The dictionary keys to search against.
        Defaults to ['Full Name', 'Surname', 'Name'].

    Returns
    -------
    list of dict
        Matching items, sorted by relevance (exact match first).

    Examples
    --------
    >>> fuzzy_search("ham", drivers, ["Full Name", "Surname"])
    [{'Full Name': 'Lewis Hamilton', ...}]
    >>> fuzzy_search("max", drivers)
    [{'Full Name': 'Max Verstappen', ...}]
    """
    if key_fields is None:
        key_fields = ['Full Name', 'Surname', 'Name']

    query = query.strip().lower()
    if not query:
        return []

    exact_matches = []
    starts_with = []
    contains = []

    for item in items:
        for field in key_fields:
            if field not in item:
                continue
            value = item[field].strip().lower()

            # Exact match (highest priority)
            if value == query:
                if item not in exact_matches:
                    exact_matches.append(item)
                break

            # Full name match (e.g., "lewis hamilton")
            if ' ' in value and query == value:
                if item not in exact_matches:
                    exact_matches.append(item)
                break

            # Starts with query
            if value.startswith(query):
                if item not in starts_with and item not in exact_matches:
                    starts_with.append(item)
                break

            # Any word starts with query
            words = value.split()
            if any(w.startswith(query) for w in words):
                if item not in starts_with and item not in exact_matches:
                    starts_with.append(item)
                break

            # Contains query
            if query in value:
                if item not in contains and item not in starts_with and item not in exact_matches:
                    contains.append(item)
                break

    return exact_matches + starts_with + contains


def select_from_matches(matches, display_field="Full Name"):
    """
    Let the user select from multiple fuzzy search matches.

    Parameters
    ----------
    matches : list of dict
        The matched items.
    display_field : str
        Which field to display for each match.

    Returns
    -------
    dict or None
        The selected item, or None if cancelled.
    """
    if not matches:
        return None

    if len(matches) == 1:
        return matches[0]

    # Show up to 10 matches
    shown = matches[:10]
    print(f"\n{Fore.YELLOW}Multiple matches found:{Style.RESET_ALL}")
    for i, item in enumerate(shown, 1):
        name = item.get(display_field, item.get('Name', 'Unknown'))
        extra = ""
        if 'Current Team' in item:
            extra = f" ({item['Current Team']})"
        elif 'Country' in item:
            extra = f" ({item['Country']})"
        print(f"  {Fore.CYAN}{i}.{Style.RESET_ALL} {name}{Fore.WHITE}{extra}{Style.RESET_ALL}")

    if len(matches) > 10:
        print(f"  {Fore.WHITE}... and {len(matches) - 10} more. Try a more specific search.{Style.RESET_ALL}")

    while True:
        try:
            choice = input(f"\n{Fore.CYAN}Select a number (or 0 to cancel): {Style.RESET_ALL}").strip()
            if choice == '0':
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(shown):
                return shown[idx]
            print_error(f"Please enter a number between 1 and {len(shown)}.")
        except ValueError:
            print_error("Please enter a valid number.")
        except (EOFError, KeyboardInterrupt):
            return None


# ── Comparison Table ────────────────────────────────────────────────────────

def compare_values(guessed_val, target_val, is_numeric=False):
    """
    Compare two values and return a result symbol.

    Parameters
    ----------
    guessed_val : str or int/float
        The guessed driver's attribute value.
    target_val : str or int/float
        The target driver's attribute value.
    is_numeric : bool
        If True, compare numerically and show higher/lower arrows.

    Returns
    -------
    str
        Colored symbol string (MATCH, WRONG, HIGHER, or LOWER).
    """
    if is_numeric:
        try:
            g = float(str(guessed_val).replace(',', ''))
            t = float(str(target_val).replace(',', ''))
            if g == t:
                return MATCH
            elif t > g:
                return HIGHER  # target is higher
            else:
                return LOWER   # target is lower
        except (ValueError, TypeError):
            return WRONG

    # String comparison
    g = str(guessed_val).strip().lower()
    t = str(target_val).strip().lower()
    if g == t:
        return MATCH
    return WRONG


def display_comparison_table(guessed, target, attributes):
    """
    Display a formatted comparison table between guessed and target.

    Parameters
    ----------
    guessed : dict
        The guessed item's data.
    target : dict
        The target item's data.
    attributes : list of tuple
        Each tuple: (display_name, dict_key, is_numeric).
    """
    # Table header
    print(f"\n{Fore.WHITE}{Style.BRIGHT}{'Attribute':<25} {'Your Guess':<20} {'Result':<15}{Style.RESET_ALL}")
    print(f"{Fore.RED}{'─' * 60}{Style.RESET_ALL}")

    for display_name, key, is_numeric in attributes:
        guessed_val = guessed.get(key, 'N/A')
        target_val  = target.get(key, 'N/A')
        result = compare_values(guessed_val, target_val, is_numeric)

        # Truncate long values for display
        display_val = str(guessed_val)[:18]

        # Color the guessed value based on result
        if MATCH_SHORT.replace(Style.RESET_ALL, '') in result.replace(Style.RESET_ALL, '') or "✅" in result:
            colored_val = f"{Fore.GREEN}{display_val}{Style.RESET_ALL}"
        elif "⬆" in result or "⬇" in result:
            colored_val = f"{Fore.YELLOW}{display_val}{Style.RESET_ALL}"
        else:
            colored_val = f"{Fore.RED}{display_val}{Style.RESET_ALL}"

        print(f"  {Fore.WHITE}{display_name:<23}{Style.RESET_ALL} {colored_val:<30} {result}")

    print(f"{Fore.RED}{'─' * 60}{Style.RESET_ALL}")


def display_guess_result(guess_num, max_guesses, guessed_name, won=None):
    """Display the result header for a guess attempt."""
    remaining = max_guesses - guess_num
    print(f"\n{Fore.CYAN}Guess {guess_num}/{max_guesses}: {Fore.WHITE}{Style.BRIGHT}{guessed_name}{Style.RESET_ALL}")
    if won is True:
        print_success("CORRECT! You guessed it!")
    elif won is False and remaining == 0:
        print_error("GAME OVER!")
    else:
        color = Fore.GREEN if remaining > 3 else (Fore.YELLOW if remaining > 1 else Fore.RED)
        print(f"  {color}Attempts remaining: {remaining}{Style.RESET_ALL}")


# ── Score Display ───────────────────────────────────────────────────────────

SCORE_TABLE = {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 10}

def calculate_score(guess_num):
    """Calculate score based on which guess was correct."""
    return SCORE_TABLE.get(guess_num, 0)


def display_score(guess_num, score):
    """Display the score earned for this game."""
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}🏆 Score: {score} points (Guess #{guess_num}){Style.RESET_ALL}")


# ── Miscellaneous ───────────────────────────────────────────────────────────

def format_number(n):
    """Format a number with commas for readability."""
    try:
        return f"{int(n):,}"
    except (ValueError, TypeError):
        return str(n)


def safe_int(value, default=0):
    """Safely convert a value to int."""
    try:
        return int(float(str(value).replace(',', '')))
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Safely convert a value to float."""
    try:
        return float(str(value).replace(',', ''))
    except (ValueError, TypeError):
        return default
