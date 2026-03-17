import openmeteo_requests
import requests_cache
import random
import os
import json

from game import Game
from retry_requests import retry
from data import Event, RANDOM_EVENT, CHOICES, SIDE_EFFECTS


class Runner():
    def __init__(self):
        self._game: Game | None = None
        self._weather: tuple | None = None
        self._win = None
        self._save_flag = False

    def new_turn(self) -> bool:
        if not self._game:
            return False

        # Check if win:
        if self._game.current_location.name == "San Francisco":
            self._win = True
            return True

        # Setup conditions for current turn
        changes = []
        random_event = self.random_event()
        self.weather_request()

        # Get input from user and check if the save_flag is True
        choice = self.get_user_input()
        if self._save_flag is True:
            self.save_game()
            return True

        # Begin filling changes list
        if random_event:
            self.fill_changes_buffer(random_event, changes)
        self.fill_changes_buffer(choice, changes)

        # If there is a freak thunderstorm ignore the weather
        if (random_event is None) or (random_event and random_event.type != "Freak Thunderstorm"):
            self.fill_changes_buffer(SIDE_EFFECTS[self._weather[0]], changes)
            self.fill_changes_buffer(SIDE_EFFECTS[self._weather[1]], changes)

        # Apply changes, check if still alive, and move forward
        self._game.update_state(changes)
        if not self.check_stats():
            self._win = False

        self._game.advance_location()

        return True

    def check_stats(self) -> bool:
        alive = True
        if self._game.current_cash <= 0:
            alive = False
        elif self._game.current_coffee <= 0:
            alive = False
        elif self._game.current_bugs > 100:
            alive = False
        elif self._game.current_morale <= 0:
            alive = False
        elif self._game.current_hype <= 0:
            alive = False
        elif self._game.current_location.name == "San Francisco":
            alive = True
        return alive

    def random_event(self) -> Event | None:
        random_event = None
        chance = random.randint(1, 4)
        if chance == 1:
            os.system('clear')
            print("\n----------Random Event Alert!!----------\n")
            random_event = random.choice(RANDOM_EVENT)
            print(f"\n----------{random_event.type}----------\n")
            print(f"""Your stats will be affected the following ways:
                    Cash: {random_event.cash}
                    Coffee: {random_event.coffee}
                    Bugs: {random_event.bugs}
                    Morale: {random_event.morale}
                    Hype: {random_event.hype}\n
                  """)
            input("Press any key to continue")
        return random_event

    def fill_changes_buffer(self, event: Event, changes: list) -> None:
        changes.append([
            event.type,
            event.cash,
            event.coffee,
            event.bugs,
            event.morale,
            event.hype,
        ])

    def new_game(self) -> bool:
        game = Game.new_game()
        self._game = game
        return True if self._game else False

    def load_game(self) -> None:
        files = os.listdir("save_files")
        print(files)
        return

    def save_game(self) -> None:
        os.system("clear")
        save_state = self._game.state
        file_name = input("Please enter a file name:", )
        file_name = file_name.split('.')[0] + ".json"
        os.makedirs("save_files", exist_ok=True)
        try:
            with open(f'save_files/{file_name}', 'w') as f:
                json.dump(save_state, f, indent=4)
        except Exception as e:
            print(f"Error saving file {e}")

    def get_current_stats(self) -> None:
        os.system("clear")
        stats = (f"""Your Current Stats:\n
                Cash: {self._game.current_cash}
                Coffee: {self._game.current_coffee}
                Bugs: {self._game.current_bugs}
                Morale: {self._game.current_morale}
                Hype: {self._game.current_hype}
                Current Location: {self._game.current_location.name}
        """)
        print(stats)

    def get_user_input(self) -> Event | None:
        choice = None
        save = False

        # Show player their current stats and their location
        self.get_current_stats()

        # Get the players choice and verify it is correct
        while choice is None and save is False:
            temp = None
            print(f"\nEnter the number of your given choice or Press '{len(CHOICES)}' to save and quit\n")

            for i in range(len(CHOICES)):
                print(f"""{i}: {CHOICES[i].type}
                        Cash -> {CHOICES[i].cash}
                        Coffee -> {CHOICES[i].coffee}
                        Bugs -> {CHOICES[i].bugs} Morale -> {CHOICES[i].morale}
                        Hype -> {CHOICES[i].hype}
                """)

            try:
                temp = int(input("Enter your choice: "))
            except ValueError:
                print("That is not a number, try again")

            if temp is not None:
                if temp == len(CHOICES):
                    save = True
                    self._save_flag = True
                elif temp >= 0 and temp < len(CHOICES):
                    choice = temp

        return None if choice is None else CHOICES[choice]

    def weather_request(self) -> None:
        cur_temp = None
        cur_precip = None
        try:
            # Setup the Open-Meteo API client with cache and retry on error
            cache_session = requests_cache.CachedSession('.cache',
                                                         expire_after=3600)
            retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
            openmeteo = openmeteo_requests.Client(session=retry_session)

            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": self._game.current_location.lat,
                "longitude": self._game.current_location.long,
                "current": ["temperature_2m", "precipitation"],
                "temperature_unit": "fahrenheit",
            }

            responses = openmeteo.weather_api(url, params=params)
            response = responses[0]
            current = response.Current()
            temp = current.Variables(0).Value()
            precip = current.Variables(1).Value()

            if temp < 50:
                cur_temp = "Cold"
            elif temp > 50 < 80:
                cur_temp = "Mild"
            else:
                cur_temp = "Hot"

            if precip == 0:
                cur_precip = "Dry"
            else:
                cur_precip = "Raining"

        except Exception as e:
            print(f"Weather request failed: {e}")
            mock_temps = ["Cold", "Mild", "Hot"]
            mock_precip = ["Dry", "Raining"]
            cur_temp = random.choice(mock_temps)
            cur_precip = random.choice(mock_precip)

        self._weather = (cur_temp, cur_precip)


if __name__ == "__main__":
    run = Runner()
    run.load_game()
