import random
import logging

from data import Location, LOCATIONS


class Game:
    """
    Represents the state and progression of a Silicon Valley Trail game.

    The Game class tracks player resources, current location, and the day
    of the game. It provides functionality to initialize a new game, load
    a saved game, apply updates from events, and advance the player
    through locations.

    Attributes:
        _cash (int): Current cash of the player.
        _coffee (int): Current coffee level of the player.
        _bugs (int): Current number of bugs in the app.
        _morale (int): Current team morale.
        _hype (int): Current product hype.
        _location_index (int): Index of the player's current location in
            LOCATIONS.
        _started (bool): Whether the game has started.
        _day (int): Current day in the game.
        _logger (logging.Logger): Logger instance for structured logging.
    """
    def __init__(self, logger: logging.Logger):
        self._cash = 0
        self._coffee = 0
        self._bugs = 0
        self._morale = 0
        self._hype = 0
        self._location_index = 0
        self._started = False
        self._day = 0
        self._logger = logger.getChild(self.__class__.__name__)

    @classmethod
    def new_game(cls, logger) -> "Game":
        """
        This method generates a new Game object and assigns random starting
        values to cash, coffee, bugs, morale, and hype. The game is marked
        as started, and a logger message is recorded.

        Args:
            logger (logging.Logger): Logger instance for structured logging.

        Returns:
            Game: A fully initialized Game instance with randomized starting
            stats.
        """
        game = cls(logger)
        game.update_cash(random.randint(50, 100))
        game.update_coffee(random.randint(50, 70))
        game.update_bugs(random.randint(0, 20))
        game.update_morale(random.randint(80, 100))
        game.update_hype(random.randint(50, 70))
        game._started = True
        game._logger.info("New game instance initialized")
        return game

    @classmethod
    def load_game(cls, state: dict, logger) -> "Game":
        """
        This method initializes a Game object using the provided state
        dictionary, restoring cash, coffee, bugs, morale, hype, current
        location, and day. The game is marked as started, and a logger
        message is recorded.

        Args:
            state (dict): Dictionary containing saved game values.
            logger (logging.Logger): Logger instance for structured logging.

        Returns:
            Game: A Game instance restored from the provided state.
        """
        game = cls(logger)
        game.update_cash(state["Cash"])
        game.update_coffee(state["Coffee"])
        game.update_bugs(state["Bugs"])
        game.update_morale(state["Morale"])
        game.update_hype(state["Hype"])
        game.update_location_index(state["Location"])
        game.update_day(state["Day"])
        game._started = True
        game._logger.info("Save game loaded and game instance created")
        return game

    @property
    def state(self) -> dict:
        """
        Property used to get the current game state.
        Returns:
            dict: Dictionary with keys "Cash", "Coffee", "Bugs", "Morale",
            "Hype", "Location", and "Day", representing the current game state.
        """
        return {"Cash": self._cash,
                "Coffee": self._coffee,
                "Bugs": self._bugs,
                "Morale": self._morale,
                "Hype": self._hype,
                "Location": self.current_location.index,
                "Day": self._day}

    def update_state(self, updates: list) -> list:
        """
        The method applies each change to the corresponding player stat and
        accumulates the total change for each parameter.

        Args:
            updates (list): A list of change lists/tuples affecting game stats.
            [type, cash, coffee, bugs, morale, hype].

        Returns:
            list[int]: Total net changes for [type, cash, coffee, bugs, morale, hype]
        """
        changes = [0 for x in range(5)]
        if updates:
            for change in updates:
                self._logger.info(change)
                self.update_cash(change[1])
                changes[0] += change[1]
                self.update_coffee(change[2])
                changes[1] += change[2]
                self.update_bugs(change[3])
                changes[2] += change[3]
                self.update_morale(change[4])
                changes[3] += change[4]
                self.update_hype(change[5])
                changes[4] += change[5]
            self._logger.info("Game state updated")
        self._logger.info(f"Changes in this turn: {changes}")
        return changes

    def advance_location(self) -> Location:
        if self._location_index == len(LOCATIONS) - 1:
            self._logger.info("Final destination reached")
            return LOCATIONS[self._location_index]
        else:
            self._location_index += 1
            self._day += 1
            self._logger.info("Location advanced")
            return LOCATIONS[self._location_index]

    @property
    def current_location(self) -> Location:
        """
        Returns the Location object of the current location
        """
        return LOCATIONS[self._location_index]

    def update_location_index(self, value: int) -> None:
        """
        Takes in value and updates the location index of the
        current Game instance.

        Args:
            value: int corresponding to index in LOCATIONS
        """
        self._location_index = value

    @property
    def current_day(self) -> int:
        """
        Returns the current day of the Game.
        """
        return self._day

    def update_day(self, value: int) -> None:
        """
        Takes in value and updates the day of the
        current Game instance.

        Args:
            value: int
        """
        self._day = value

    def increment_day(self) -> None:
        """
        Increments the day by 1.
        """
        self._day += 1

    @property
    def current_cash(self) -> int:
        """
        Returns the cash for the Game instance.
        """
        return self._cash

    def update_cash(self, value: int) -> None:
        """
        Takes in value and updates the cash of the
        current Game instance.

        Args:
            value: int
        """
        self._cash += value

    @property
    def current_coffee(self) -> int:
        """
        Returns the Game instances current coffee supply.
        """
        return self._coffee

    def update_coffee(self, value: int) -> None:
        """
        Takes in value and updates the coffee of the
        current Game instance.

        Args:
            value: int
        """
        self._coffee += value

    @property
    def current_bugs(self) -> int:
        """
        Returns the Game instances current bug count.
        """
        return self._bugs

    def update_bugs(self, value: int) -> None:
        """
        Takes in value and updates the bug count of the
        current Game instance.

        Args:
            value: int
        """
        self._bugs += value

    @property
    def current_morale(self) -> int:
        """
        Gets the current morale score for the Game instance.
        """
        return self._morale

    def update_morale(self, value: int) -> None:
        """
        Takes in value and updates the morale of the
        current Game instance.

        Args:
            value: int
        """
        self._morale += value

    @property
    def current_hype(self) -> int:
        """
        Returns the current hype level of the Game instance.
        """
        return self._hype

    def update_hype(self, value: int) -> None:
        """
        Takes in value and updates the hype value of the
        current Game instance.

        Args:
            value: int
        """
        self._hype += value
