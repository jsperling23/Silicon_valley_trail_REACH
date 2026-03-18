import openmeteo_requests
import requests_cache
import random
import os
import json
import time
import logging

from game import Game
from retry_requests import retry
from data import Event, RANDOM_EVENT, CHOICES, SIDE_EFFECTS


class Runner():
    """
    Manages the main game loop and player interactions for the Silicon Valley
    Trail game.

    Responsibilities:
        - Start a new game or load a saved game.
        - Handle turns, including random events, weather effects,
          and player choices.
        - Track the game state and determine win/loss conditions.
        - Save and load game state to and from disk.
        - Display game stats, weather effects, and simple animations.

    Attributes:
        _logger (logging.Logger): Logger instance for structured logging.
        _game (Game | None): The current game instance, or None if not started.
        _weather (tuple | None): Current weather conditions as
            (temperature, precipitation).
        _win (bool | None): Tracks whether the player has won, lost,
            or None if ongoing.
        _save_flag (bool): Indicates whether the player requested to save
            and quit.
    """
    def __init__(self, logger: logging.Logger):
        self._logger = logger.getChild(self.__class__.__name__)
        self._game: Game | None = None
        self._weather: tuple | None = None
        self._win = None
        self._save_flag = False

    def start_game(self) -> None:
        """
        Method takes in in no parameters. It displays a welcome message and
        allows the user to enter an integer in order to start a new game or
        load a previous save. Both result in the self._game instance attribute
        being filled.
        """
        self._logger.info("Game Started")
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
                        self._logger.info("Something went wrong starting a \
                                          new game")
                elif temp == 1:
                    game = self.load_game()
                    choice = temp
                    if game is False:
                        choice = None
                        self._logger.info("Something went wrong loading that \
                                          file...")
                else:
                    print("Number out of bounds, try again.")
            except ValueError:
                print("That is not a number, try again")

    def new_turn(self) -> None:
        """
        Method takes in no parameters. It goes in the following o
        """
        self._logger.info("New turn started.")
        random_event = None
        if not self._game:
            return

        # Check if win:
        if self._game.current_location.name == "San Francisco":
            self._win = True
            return

        # Setup conditions for current turn and skip random event if first day
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

        # Check whether the party can move or not depending on the random event
        if random_event is not None and random_event.delay is True:
            self.no_move_turn(random_event)
            self._game.increment_day()
        else:
            self._game.advance_location()
        self.travel_animation()

        return

    def no_move_turn(self, random_event: Event) -> None:
        """
        With certain random events, the party is unable to move forward. This
        function prints out a message letting the user know.
        """
        os.system("clear")
        print(f"Because of {random_event.type}, you are stuck in {self._game.current_location.name}.\
              and will not move forward today")
        input("Press enter to continue")

    def check_stats(self) -> bool:
        """
        Check current game stats against win/lose conditions.

        Evaluates the player's resources and game state to determine whether
        the game should continue. If any losing condition is met (e.g., cash,
        coffee, morale, hype depleted, or too many bugs), the game ends and
        a message is displayed.

        Returns:
            bool: True if the player is still alive (game continues),
            False if a losing condition has been met.
        """
        alive = True
        if self._game:
            if self._game.current_cash <= 0:
                alive = False
                os.system("clear")
                print("Unfortunately you ran out of cash and can't afford to \
                      move on")
            elif self._game.current_coffee <= 0:
                alive = False
                os.system("clear")
                print("Unfortunately you ran out of coffee and are too tired \
                      to continue")
            elif self._game.current_bugs > 50:
                alive = False
                os.system("clear")
                print("Your app has too many bugs, it fails to work and you \
                      lose.")
            elif self._game.current_morale <= 0:
                alive = False
                os.system("clear")
                print("Your team is too depressed to continue, morale is too \
                      low.")
            elif self._game.current_hype <= 0:
                alive = False
                os.system("clear")
                print("The hype for your product is too low, nobody wants it. \
                      You fail.")
            elif self._game.current_location.name == "San Francisco":
                alive = True
        return alive

    def random_event(self) -> Event | None:
        """
        Rolls between 1 and 4 to see if a random event happens. If
        it hits 1 then a random event is randomly chosen from the
        random event table.

        Returns:
            Event: Event Object from RANDOM_EVENT table if the roll 1
            None otherwise

        """
        random_event = None
        chance = random.randint(1, 4)
        if chance == 1:
            self._logger.info("A random event roll has hit")
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
        """
        Append event data to the changes buffer.

        Extracts relevant attributes from the given event and stores them
        as a list in the provided changes collection.

        Args:
            event (Event): The event containing affects game state values.
            changes (list): A list used to accumulate change records.

        Returns:
            None
        """
        changes.append([
            event.type,
            event.cash,
            event.coffee,
            event.bugs,
            event.morale,
            event.hype,
        ])

    def new_game(self) -> bool:
        """
        Initialize and assign a new game instance.

        Returns:
            bool: True if the game was successfully created and assigned,
            False otherwise.
        """
        game = Game.new_game(self._logger)
        self._game = game
        return True if self._game else False

    def load_game(self) -> bool:
        """
        Load a saved game from disk.

        Displays available save files to the user, prompts for a selection,
        and attempts to load the chosen file. If successful, the game state
        is restored and assigned to the instance.

        Returns:
            bool: True if the game was successfully loaded, False if an
            error occurred during loading.
        """
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
                self._game = Game.load_game(load_state, self._logger)
            self._logger.info(f"File {filepath} successfully loaded")
        except Exception as e:
            self._logger.info(f"Error opening file: {e}")
            return False
        return True

    def save_game(self) -> None:
        """
        Save a new game to a new file.
        Prompts the user to enter in their choice of filename and
        attempts to save to that filename.
        """
        os.system("clear")
        save_state = self._game.state
        file_name = input("Please enter a file name:", )
        file_name = file_name.split('.')[0] + ".json"
        os.makedirs("save_files", exist_ok=True)
        filepath = os.path.join(os.getcwd(), "save_files", file_name)
        try:
            with open(filepath, 'w') as f:
                json.dump(save_state, f, indent=4)
            self._logger.info(f"File {filepath} successfully saved")
        except Exception as e:
            self._logger.info(f"Error saving file {e}")

    def get_current_stats(self) -> None:
        """
        Clears the screen, gets the current game stats, puts them in a
        dictionary, and prints them to the screen
        """
        os.system("clear")
        stats = (f"""Your Current Stats:\n
                Cash: {self._game.current_cash}
                Coffee: {self._game.current_coffee}
                Bugs: {self._game.current_bugs}
                Morale: {self._game.current_morale}
                Hype: {self._game.current_hype}
                Current Location: {self._game.current_location.name}
                Days on the Trail: {self._game.current_day}
        """)
        print(stats)

    def get_user_input(self) -> Event | None:
        """
        Prompt the player to make a game choice or save and quit.

        Displays the player's current stats and location, applies weather
        effects, and shows all available choices. The player is repeatedly
        prompted until they select a valid choice or choose to save and quit.

        Returns:
            Event | None: The chosen Event object if a valid choice was made,
            or None if the player chose to save and quit.
        """
        choice = None
        save = False

        # Show player their current stats and their location
        self.get_current_stats()

        # Show the player how the weather affects their stats
        self.weather_effects()

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
        """
        Iterates through a list to create an animation of a moving
        dotted trail.
        """
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
        """
        This function takes in no parameters and uses the openmeteo_requests
        library to access the OpenMeteo API and get the current weather
        for the location of the player. If something goes wrong with the
        request, randomized mock data is used instead.
        """
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

            self._logger.info("Weather successfully obtained from OpenMeteo")

        except Exception as e:
            self._logger.info(f"Weather request failed: {e}, mock data used")
            mock_temps = ["Cold", "Mild", "Hot"]
            mock_precip = ["Dry", "Raining"]
            cur_temp = random.choice(mock_temps)
            cur_precip = random.choice(mock_precip)

        self._weather = (cur_temp, cur_precip)

    def weather_effects(self):
        """
        Prints out the effects of the current weather to display on the
        screen of the current turn.
        """
        if self._weather[0] == "Hot":
            print("The weather is hot, bug count +5 and morale -5")
        elif self._weather[0] == "Cold":
            print("Brrrr...cold weather. Coffee -5 and moral -5")
        else:
            print("Nice day out, weather is mild")

        if self._weather[1] == "Wet":
            print("What a nice day...its raining. Take cover inside. -5 Cash\
                  and -5 Morale.")
        else:
            print("Nice dry day, no rain!")

    @property
    def current_game(self):
        """
        Returns the instances Game object.
        """
        return self._game


if __name__ == "__main__":
    run = Runner()
    run.load_game()
