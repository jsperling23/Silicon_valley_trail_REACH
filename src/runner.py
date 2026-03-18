import openmeteo_requests
import requests_cache
import random
import os
import json
import time

from game import Game
from retry_requests import retry
from data import Event, RANDOM_EVENT, CHOICES, SIDE_EFFECTS


class Runner():
    def __init__(self):
        self._game: Game | None = None
        self._weather: tuple | None = None
        self._win = None
        self._save_flag = False

    def start_game(self) -> None:
        """
        Method takes in in no parameters. It displays a welcome message and
        allows the user to enter an integer in order to start a new game or
        load a previous save. Both result in the self._game instance attribute
        being filled. This method does not return anything.
        """
        os.system("clear")
        choice = None
        print("""
              Welcome to the Silicon Valley Trail!!\n
              Try and get from San Jose to San Francisco with your new
              product. The choices you make along the way will decide
              your fate. It is essential that you keep your cash, coffee,
              morale, and hype above zero and your bug count below 50 otherwise
              you will perish, like many others, along ye old Silicon Valley
              Trail.

              Would you like to start a new game or load a previous save?
              Enter the number corresponding to your choice
              0: New Game
              1: Load Game 
              """)
        while choice is None:
            try:
                temp = int(input("Enter your choice: "))
                if temp == 0:
                    choice = temp
                    game = self.new_game()
                    if game is False:
                        print("Something went wrong starting a new game...")
                elif temp == 1:
                    game = self.load_game()
                    choice = temp
                    if game is False:
                        choice = None
                        print("Something went wrong loading that file...")
                else:
                    print("Number out of bounds, try again.")
            except ValueError:
                print("That is not a number, try again")

    def new_turn(self) -> None:
        """
        Method takes in no parameters. It goes in the following o"""
        random_event = None
        if not self._game:
            return

        # Check if win:
        if self._game.current_location.name == "San Francisco":
            self._win = True
            return

        # Setup conditions for current turn and skip random event if first
        changes = []
        if self._game.current_day != 0:
            random_event = self.random_event()
        self.weather_request()

        # Get input from user and check if the save_flag is True
        choice = self.get_user_input()
        if self._save_flag is True:
            self.save_game()
            return

        # Begin filling changes list
        if random_event:
            self.fill_changes_buffer(random_event, changes)
        self.fill_changes_buffer(choice, changes)

        # If there is a freak thunderstorm ignore the weather
        if (random_event is None) or (random_event and random_event.index != 0):
            self.fill_changes_buffer(SIDE_EFFECTS[self._weather[0]], changes)
            self.fill_changes_buffer(SIDE_EFFECTS[self._weather[1]], changes)

        # Apply changes, check if still alive, and move forward
        self._game.update_state(changes)
        if not self.check_stats():
            self._win = False

        # Depending on the event
        if random_event is not None and random_event.delay is True:
            self.no_move_turn(random_event)
        else:
            self._game.advance_location()
        self.travel_animation()

        return
    def no_move_turn(self, random_event: Event) -> None:
        os.system("clear")
        print(f"Because of {random_event.type}, you are stuck in {self._game.current_location.name}.\
              and will not move forward today")
        input("Press enter to continue")
        self._game.increment_day()

    def check_stats(self) -> bool:
        alive = True
        if self._game:
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

    def load_game(self) -> bool:
        # List save files and print them to screen
        files = os.listdir("save_files")
        os.system("Clear")
        for i in range(len(files)):
            print(f"{i}: {files[i]}")
        chosen_file = None

        # Get users input
        while chosen_file is None:
            try:
                temp = int(input("Enter the number corresponding to your save file: "))
                if temp > len(files) - 1:
                    print("Number choice out of bounds please try again")
                else:
                    chosen_file = files[temp]
            except ValueError:
                print("That is not a number please try again")

        # Construct filepath, try opening file and setting state
        filepath = os.path.join(os.getcwd(), "save_files", chosen_file)
        print(filepath)
        try:
            with open(filepath) as f:
                load_state = json.load(f)
                self._game = Game.load_game(load_state)
        except Exception as e:
            print(f"Error opening file: {e}")
            return False
        return True

    def save_game(self) -> None:
        os.system("clear")
        save_state = self._game.state
        file_name = input("Please enter a file name:", )
        file_name = file_name.split('.')[0] + ".json"
        os.makedirs("save_files", exist_ok=True)
        filepath = os.path.join(os.getcwd(), "save_files", file_name)
        try:
            with open(filepath, 'w') as f:
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
                Days on the Trail: {self._game.current_day}
                Temperature: {self._weather[0]}
                Precipitation: {self._weather[1]}
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

    def travel_animation(self) -> None:
        travel_deck = [
            "Moving along the ol dusty trail.",
            "Moving along the ol dusty trail..",
            "Moving along the ol dusty trail..."
            ]
        for i in range(2):
            for string in travel_deck:
                os.system("clear")
                print(string)
                time.sleep(0.5)

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
            elif 50 > temp < 80:
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

    @property
    def current_game(self):
        return self._game


if __name__ == "__main__":
    run = Runner()
    run.load_game()
