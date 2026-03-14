import random
from map import Location, LOCATIONS


class Game:
    def __init__(self):
        self._cash = 0
        self._coffee = 0
        self._bugs = 0
        self._tech_debt = 0
        self._morale = 0
        self._hype = 0
        self._location_index = 0
        self._started = False

    @classmethod
    def new_game(cls) -> "Game":
        game = cls()
        game.update_cash(random.randint(50, 100))
        game.update_coffee(random.randint(50, 70))
        game.update_bugs(random.randint(0, 20))
        game.update_tech_debt(random.randint(0, 10))
        game.update_morale(random.randint(80, 100))
        game.update_hype(random.randint(0, 20))
        game._started = True
        return game

    @property
    def state(self) -> dict:
        return {"Cash": self._cash,
                "Coffee": self._coffee,
                "Bugs": self._bugs,
                "Tech Debt": self._tech_debt,
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
            return LOCATIONS[self._location_index]

    @property
    def get_cash(self) -> int:
        return self._cash

    def update_cash(self, value) -> None:
        self._cash += value

    @property
    def get_coffee(self) -> int:
        return self._coffee

    def update_coffee(self, value) -> None:
        self._cash += value

    @property
    def get_bugs(self) -> int:
        return self._bugs

    def update_bugs(self, value) -> None:
        self._bugs += value

    @property
    def current_tech_debt(self) -> int:
        return self._tech_debt

    def update_tech_debt(self, value) -> None:
        self._tech_debt += value

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
