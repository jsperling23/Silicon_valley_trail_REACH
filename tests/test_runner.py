from unittest.mock import patch
from src.data import CHOICES, RANDOM_EVENT


class TestRunner:
    def test_new_runner(self, new_runner):
        """
        Test whether a game loads in.
        """
        assert new_runner.current_game is not None

    def test_new_state(self, new_runner):
        """
        Test the starting state of a new game.
        """
        state = new_runner._game.state
        assert type(state) is dict
        assert 50 <= state["Cash"] <= 100
        assert 50 <= state["Coffee"] <= 70
        assert 0 <= state["Bugs"] <= 20
        assert 80 <= state["Morale"] <= 100
        assert 50 <= state["Hype"] <= 70
        assert state["Location"] == 0
        assert state["Day"] == 0

    def test_loaded_runner(self, new_runner):
        """
        Test whether a game loads in with the load game option.
        """
        assert new_runner.current_game is not None

    def test_loaded_state(self, loaded_runner):
        """
        Test the values when loading from a mock save file.
        """
        state = loaded_runner._game.state
        assert type(state) is dict
        assert state["Cash"] == 75
        assert state["Coffee"] == 60
        assert state["Bugs"] == 10
        assert state["Morale"] == 90
        assert state["Hype"] == 65
        assert state["Location"] == 2
        assert state["Day"] == 3

    def test_new_turn(self, loaded_runner):
        """
        Tests the values of a new turn using the hot weather and
        wet precipitation events along with the get supplies choice.
        No random event in this outcome. Checks whether the day and
        location advances as well.

        Get Supplies: cash -10, coffee +20
        Hot weather: bugs +5, morale -5
        Wet weather: cash -5, morale -5
        """
        state = loaded_runner.current_game.state
        initial_location = loaded_runner.current_game.current_location.index
        with patch.object(loaded_runner, "random_event", return_value=None), \
             patch.object(loaded_runner, "weather_request"), \
             patch.object(loaded_runner, "get_user_input",
                          return_value=CHOICES[2]), \
             patch.object(loaded_runner, "travel_animation"), \
             patch("os.system"):
            loaded_runner._weather = ("Hot", "Wet")
            loaded_runner.new_turn()

        # State change assertions
        assert loaded_runner.current_game.current_cash == \
            state["Cash"] - 10 - 5
        assert loaded_runner.current_game.current_coffee == \
            state["Coffee"] + 20
        assert loaded_runner.current_game.current_bugs == state["Bugs"] + 5
        assert loaded_runner.current_game.current_morale == \
            state["Morale"] - 5 - 5
        assert loaded_runner.current_game.current_hype == state["Hype"]
        assert loaded_runner.current_game.current_day == state["Day"] + 1
        assert loaded_runner.current_game.current_location.index == \
            initial_location + 1

    def test_new_turn_thunderstorm(self, loaded_runner):
        """
        Test that a random event with a delay, in this case, freak thunderstorm
        causes the party to be stuck for a single day. Also checks if the freak
        thunderstorm event overrides the current weather.

        Get Supplies: cash -10, coffee +20
        Freak Thunderstorm: cash -20, morale -20, causes delay
        """
        state = loaded_runner.current_game.state
        initial_location = loaded_runner.current_game.current_location.index
        with patch.object(loaded_runner, "random_event",
                          return_value=RANDOM_EVENT[0]), \
            patch.object(loaded_runner, "weather_request"), \
            patch.object(loaded_runner, "get_user_input",
                         return_value=CHOICES[2]), \
            patch.object(loaded_runner, "no_move_turn"), \
            patch.object(loaded_runner, "travel_animation"), \
                patch("os.system"):
            loaded_runner._weather = ("Hot", "Wet")
            loaded_runner.new_turn()

            # State change assertions
            assert loaded_runner.current_game.current_cash == \
                state["Cash"] - 10 - 20
            assert loaded_runner.current_game.current_coffee == \
                state["Coffee"] + 20
            assert loaded_runner.current_game.current_bugs == state["Bugs"]
            assert loaded_runner.current_game.current_morale == \
                state["Morale"] - 20
            assert loaded_runner.current_game.current_hype == state["Hype"]
            assert loaded_runner.current_game.current_day == state["Day"] + 1
            assert loaded_runner.current_game.current_location.index == \
                initial_location

    def test_new_turn_random_no_delay(self, loaded_runner):
        """
        Tests the values of a new turn using the hot weather and
        wet precipitation events along with the get supplies choice.
        No random event in this outcome. Checks whether the day and
        location advances as well.

        Get Supplies: cash -10, coffee +20
        Hot weather: bugs +5, morale -5
        Wet weather: cash -5, morale -5
        Positive investor email(random event): +20 cash, +20 morale, +20 hype
        """
        state = loaded_runner.current_game.state
        initial_location = loaded_runner.current_game.current_location.index
        with patch.object(loaded_runner, "random_event",
                          return_value=RANDOM_EVENT[1]), \
             patch.object(loaded_runner, "weather_request"), \
             patch.object(loaded_runner, "get_user_input",
                          return_value=CHOICES[2]), \
             patch.object(loaded_runner, "travel_animation"), \
             patch("os.system"):
            loaded_runner._weather = ("Hot", "Wet")
            loaded_runner.new_turn()

        # State change assertions
        assert loaded_runner.current_game.current_cash == \
            state["Cash"] - 10 - 5 + 20
        assert loaded_runner.current_game.current_coffee == \
            state["Coffee"] + 20
        assert loaded_runner.current_game.current_bugs == state["Bugs"] + 5
        assert loaded_runner.current_game.current_morale == \
            state["Morale"] - 5 - 5 + 20
        assert loaded_runner.current_game.current_hype == state["Hype"] + 20
        assert loaded_runner.current_game.current_day == state["Day"] + 1
        assert loaded_runner.current_game.current_location.index == \
            initial_location + 1

    def test_save_flag(self, loaded_runner):
        """
        Tests whether the save flag gets set when the save option is chosen.
        """
        initial_save_flag = loaded_runner._save_flag
        with patch.object(loaded_runner, "random_event",
                          return_value=RANDOM_EVENT[1]), \
            patch.object(loaded_runner, "weather_request"), \
            patch.object(loaded_runner, "get_user_input", return_value=None), \
            patch.object(loaded_runner, "save_game") as mock_save, \
                patch("os.system"):
            loaded_runner._weather = ("Hot", "Wet")
            loaded_runner._save_flag = True
            loaded_runner.new_turn()

        assert initial_save_flag is False
        assert loaded_runner._save_flag is True
        mock_save.assert_called_once()

    def test_win_game(self, loaded_runner):
        """
        Test that reaching San Francisco sets the win flag to True.
        """
        loaded_runner.current_game._location_index = 10
        with patch.object(loaded_runner, "random_event",
                          return_value=RANDOM_EVENT[1]), \
             patch.object(loaded_runner, "weather_request"), \
             patch.object(loaded_runner, "get_user_input",
                          return_value=CHOICES[2]), \
             patch.object(loaded_runner, "travel_animation"), \
             patch("os.system"):
            loaded_runner._weather = ("Hot", "Wet")
            loaded_runner.new_turn()

        assert loaded_runner._win is True
        assert loaded_runner.current_game.current_location.name == \
            "San Francisco"

    def test_lose_game(self, loaded_runner):
        """
        Test that having an out of bound parameter sets
        the win flag to False
        """
        loaded_runner.current_game.update_bugs(75)
        with patch.object(loaded_runner, "random_event",
                          return_value=RANDOM_EVENT[1]), \
             patch.object(loaded_runner, "weather_request"), \
             patch.object(loaded_runner, "get_user_input",
                          return_value=CHOICES[2]), \
             patch.object(loaded_runner, "travel_animation"), \
             patch.object(loaded_runner, "check_stats",
                          return_value=False), \
                patch("os.system"):
            loaded_runner._weather = ("Hot", "Wet")
            loaded_runner.new_turn()

        assert loaded_runner._win is False
