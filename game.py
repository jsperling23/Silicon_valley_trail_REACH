import random
from data import Location, LOCATIONS


class Game:
    def __init__(self):
        self._cash = 0
        self._coffee = 0
        self._bugs = 0
        self._morale = 0
        self._hype = 0
        self._location_index = 0
        self._started = False
        self._day = 0

    @classmethod
    def new_game(cls) -> "Game":
        game = cls()
        game.update_cash(random.randint(50, 100))
        game.update_coffee(random.randint(50, 70))
        game.update_bugs(random.randint(0, 20))
        game.update_morale(random.randint(80, 100))
        game.update_hype(random.randint(0, 20))
        game._started = True
        return game

    @property
    def state(self) -> dict:
        return {"Cash": self._cash,
                "Coffee": self._coffee,
                "Bugs": self._bugs,
                "Morale": self._morale,
                "Hype": self._hype,
                "Location": LOCATIONS[self._location_index]}

    @property
    def current_location(self) -> Location:
        return LOCATIONS[self._location_index]

    def advance_location(self) -> Location:
        if self._location_index == len(LOCATIONS) - 1:
            return LOCATIONS[self._location_index]
        else:
            self._location_index += 1
            self._day += 1
            return LOCATIONS[self._location_index]

    @property
    def current_day(self) -> int:
        return self._day

    @property
    def current_cash(self) -> int:
        return self._cash

    def update_cash(self, value) -> None:
        self._cash += value

    @property
    def current_coffee(self) -> int:
        return self._coffee

    def update_coffee(self, value) -> None:
        self._cash += value

    @property
    def get_bugs(self) -> int:
        return self._bugs

    def update_bugs(self, value) -> None:
        self._bugs += value

    @property
    def current_morale(self) -> int:
        return self._morale

    def update_morale(self, value) -> None:
        self._morale += value

    @property
    def current_hype(self) -> int:
        return self._hype

    def update_hype(self, value) -> None:
        self._hype += value
