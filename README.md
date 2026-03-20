# Silicon Valley Trail

A terminal-based adventure game inspired by the Oregon Trail, set in Silicon Valley. Navigate from San Jose to San Francisco while managing your startup's cash, coffee, bugs, morale, and hype.

---

## Quick Start

### Prerequisites
- Python 3.11+
- pip

### Setup from a fresh machine

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Silicon_valley_trail_REACH

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the game
python3 src/main.py
```

---

## API Keys

This project uses the [Open-Meteo API](https://open-meteo.com/) for live weather data. This API does not require an API key and there is no authenitcation required.

### Running with mock weather data

If the weather request fails for any reason (no internet, API down, etc.), the game automatically falls back to randomized mock weather data. This is handled under the `weather_request` class method in `runner.py`:

```python
except Exception as e:
    self._logger.info(f"Weather request failed: {e}, mock data used")
    cur_temp = random.choice(["Cold", "Mild", "Hot"])
    cur_precip = random.choice(["Dry", "Raining"])
```

To force mock data during development, you can disable the network or simply let the exception trigger naturally. If doing this, make sure the cache file that automatically generates when using the API is clear.

---

## Architecture Overview

```
Silicon_valley_trail_REACH/
├── src/
│   ├── main.py        # Entry point — sets up logging and runs the game loop
│   ├── runner.py      # Runner class — manages I/O and turn logic
│   ├── game.py        # Game class — tracks and updates player state
│   └── data.py        # Data — Event dataclass and Location dataclass
├── tests/
│   └── test_runner.py # Test suite for Runner and Game
├── save_files/        # JSON save files created at runtime
├── conftest.py        # Shared pytest fixtures
├── pyproject.toml     # Pytest configuration
└── requirements.txt   # Python dependencies
```

### Key Components

**`Runner`** — This controls everything related to the `Game` instance state. Handles all user input/output, manages all state changes each turn, calls the weather API, applies random events, and determines win/loss conditions.

**`Game`** — This handles the state of the game. Tracks cash, coffee, bugs, morale, hype, location, and day. No I/O. Exposes methods to update and read state for the Runner class.

**`data.py`** — This file contains static game data that `Runner` uses to update the game state as the game progresses. Defines the `Event` dataclass and the four data tables:`CHOICES`, `RANDOM_EVENT`, and `SIDE_EFFECTS`. The `Locations` dataclass is defined here as well and contains a data table, `LOCATIONS` representing a map of all the locations a player has to travel through.

### Dependencies

| Package | Purpose |
|---|---|
| `openmeteo-requests` | Open-Meteo weather API client |
| `requests-cache` | Caches API responses to reduce redundant calls |
| `retry-requests` | Adds retry logic to HTTP requests |
| `pytest` | Test runner |

---

## How to Run Tests

```bash
# From the root directory with your virtual environment activated

# Run all tests
pytest tests/

# Run with verbose output
pytest -v tests/
```

### Test structure

Tests are organized in `tests/test_runner.py` under a single `TestRunner` class. Shared fixtures live in `conftest.py` at the root:

| Fixture | Description |
|---|---|
| `mock_logger` | A `MagicMock` logger — silent, no setup needed |
| `runner` | A bare `Runner` instance with no game loaded |
| `new_runner` | A `Runner` with a new game already started |
| `loaded_runner` | A `Runner` with a save file loaded from a mock state |

All I/O (`input`, `os.system`, file operations, weather API) is mocked in tests so the suite runs fully offline with no user interaction required.