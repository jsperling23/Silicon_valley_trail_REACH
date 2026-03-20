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
git clone (https://github.com/jsperling23/Silicon_valley_trail_REACH.git)
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
│   ├── runner.py      # Runner class — manages I/O, API calls, and turn logic
│   ├── game.py        # Game class — tracks and updates player state
│   └── data.py        # Data — Event dataclass and Location dataclass
├── tests/
│   └── test_runner.py # Test suite for Runner
├── save_files/        # JSON save files created at runtime
├── conftest.py        # Shared pytest fixtures
├── pyproject.toml     # Pytest configuration
└── requirements.txt   # Python dependencies
```

### Key Components
**`main.py`** - This initializes the logger instance, the `Runner` class instance, starts the game, and handles the game loop. It performs checks on each loop to see if win or loss flags int he `Runner` class are set.

**`Runner`** — This controls everything related to the `Game` instance state. Handles all user input/output, manages all state changes each turn, calls the weather API, applies random events, and determines win/loss conditions.

**`Game`** — This handles the state of the game. Tracks cash, coffee, bugs, morale, hype, location, and day. No I/O. Exposes methods to update and read state for the Runner class.

**`data.py`** — This file contains static game data that `Runner` uses to update the game state as the game progresses. Defines the `Event` dataclass and the three data tables:`CHOICES`, `RANDOM_EVENT`, and `SIDE_EFFECTS`. The `Locations` dataclass is defined here as well and contains a data table, `LOCATIONS`, which represents a map of all the locations a player has to travel through.

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
| `mock_logger` | A `MagicMock` logger, it is silent |
| `runner` | A bare `Runner` instance with no game loaded |
| `new_runner` | A `Runner` with a new game already started |
| `loaded_runner` | A `Runner` with a save file loaded from a mock state |

All I/O (`input`, `os.system`, file operations, weather API) is mocked in tests so the suite runs fully offline with no user interaction required.

### AI Usage

Throughout working on this project, I utilized AI in various ways. First off, I used it to help format and give me an outline for this README. While I've spent time making README's pretty before, AI handled stuff like making a nice folder structure for the architecture overview and listing out the dependencies in my project for me. Outside of the README, I have two main instances where I like to use it. Learning new libraries and debugging. While I've worked with Pytest before, its been a couple months, I used Claude AI to help get me started and provide the relevant documentation pages so I could continue on and write a testing suite. Along with that, I like to use it for debugging, especially when I'm getting really hyperfocused on a bug and can't figure it out, AI often helps point out the issue or at least provide a different persepctive. With that in mind, when I use AI, it is a tool, not the whole programmer. It can help me learn a library faster and help me debug, or outline a README for me, but I also have learned to be very careful of what it puts out and to make sure I understand it. Quite a few times in my programming journey has AI led me down a path that ended up in technical debt because I did not understand what I was working with. To clarify, AI helped write everything above this section, which I then whittled down and edited. Below this section, everything was written by hand. Along with that, almost all of the code in the project was written by hand.

### Design Notes

The game loop is all run through the `main.py` file. In there, a `logging` instance is created and injected into a newly made `Runner` instance. Next, the file uses the `Runner` instance to run the `start_game` class method. `Runner` is a class that handles creating a `Game` instance along with all logic with regards to I/O, API requests, updating state, and saving/loading the state. The `Game` class is to hold the state of the game at all times and exposes methods that allow the state to be loaded, updated, and viewed by the `Runner` class. When the `Runner.start_game` is called, the player is given two options. They can either start a new game or load a previous save. A new game randomly chooses stats in a given range for each player stat. After making their choice, the actual game loop is entered which continues until the player saves the game and exits, wins the game, or loses the game. On each turn, the `Runner.new_turn`method is called. First the game checks if the player is in San Francisco and sets the win flag if so. A player has a 1 in 4 chance of getting a random event, unless its the first turn and this is skipped, which affects their stats, (money, coffee, bugs, morale, hype), and potentially keeps them stuck at their location for an extra day. This change occurs before the user sees their stats when they arrive at their current location so they have a chance to make a choice based on the random event if it happens. On each turn, the player is presented with 4 random choices from 6 possible choices for things to do at their current location which will affect their stats. Along with that, the weather API is called and the weather affects player stats by increasing bugs in heat and decreasing morale if it is raining for example. However, certain random events can override the weather and their effects such as a freak thunderstorm. The changes from the players choice are loaded into a buffer as the method progresses which is then passed into `Game` to update the state of the game. From there, the method checks all `Game` stats to see if the player is able to continue or if they have lost. If any of the stats reaches 0, or if the bug count reaches 50, a losing message is displayed. If the player makes it from San Jose to San Francisco, they win the game. Throughout all of this, all actions are logged into a log file using the Python logging library.

The data for this game was all stored in the `data.py` file. For all the events that could affect the players, they used the `Events` data class which has stats for each of the player stats as well as information on the event, whether the event causes travel delay, and what effects the event has on each of the player stats. I choose to work with data classes because it was easy to pass them around in the `Runner` class and packaged all the information into clean, readable, and easy to work with objects. To allow for randomization, the events were added into lists suchs as `RANDOM_EVENTS` and `CHOICES` so I could use Python's random module to pick from these lists. The weather events, `SIDE_EFFECTS`, I packaged the events into a dictionary so it would be easy to get the associated effects based on what came off the API request, these were not random unless the API failed. The weather API takes into account temperature and precipitation and it is categorized into 'Hot', 'Mild', 'Cold', 'Dry' and 'Wet'. 'Dry' and 'Mild' do not affect the players stats while the others have negative effects. The map in this game once again used a data class, `Location`, which was packaged into a list of `Location` instances called `LOCATIONS`. I used a list because it was easy to keep track of the index and iterate along the map and use that index to get the current `Location` instance with its associated latitude and longitude at any point. For persistance, I decided to utilize JSON files in a save folder. The reason I choose JSON is because it is human readable, easy to add into a testing suite for a mock state, and converts easily between a Python dictionary and a JSON object. Along with that, it was easy to package the state into a dictionary and reload it later from a dictionary.

For the API I chose, I chose Open-Meteo because they had good documentation and Python library which made it very easy to setup and understand. Network failures and rate limits are handled by wrapping the Open-Meteo client with a cached session that stores responses for one hour, and a retry session that automatically retries failed requests up to five times. If the request still fails, the game falls back to randomized mock weather data so gameplay is never interrupted. For all error handling throughout the game, everything that could fail would also log into a log file for debugging later on. Other error handling includes mananging the input from the user which is handled with while loops that continue to try and prompt the user until they give valid input. Another example would be trying to load a game with no saves, it just displays a message and starts a new game instead.

If I had more time, theres a few things I would've liked to have done differently. A lot of the game dialogue is hardcoded into the methods in the `Runner` class which works, but it isn't the most scalable. I would've like to sit down and figure out some sort of class or dataclass that I could've used so it would be easy to swap the dialogue without having to go into `Runner` at all. The main challenge here is there are varying requirements for variables that fit into all of those strings. Along with that, I would've liked to test my game method by method instead of just testing all the paths a user could take in a game loop. Another thing is I think storing the events and save files in a relational database would provide a more scalable approach if the game got bigger in the future, but for the scope of this project, I felt it was overkill. The last thing I wish I could've spent more time on was testing, I would've liked to achieve full path coverage for the game on all methods.

Testing wise, I utilized Pytest because I believe that it is the industry standard. Since I didn't have time to sit down and write unit tests for all cases of each method in each class, I focused on two main methods, `Runner.start_game` and `Runner.new_turn`. These are the two main methods from which the whole game is run. Using two mock objects, one new and one with a loaded in a mock state, I tried to simulate all the paths that a user could take through a game from start, to save, to load, to win/lose. This kind of blended the line between integration, some tests utilized lots of different methods working together, and unit tests, some behaivor was mocked and simply tested the outcomes of those two methods. With that in mind, there is always room for improvement here and full path coverage of the code would be the end goal with enough time.



