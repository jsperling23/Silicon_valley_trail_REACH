import openmeteo_requests
import requests_cache
import random

from game import Game
from retry_requests import retry
from data import Event, RANDOM_EVENT, CHOICES


class Runner():
    def __init__(self):
        self._game: Game | None = None
        self._weather = None
        self._win = None

    def new_turn(self) -> bool:
        if not self._game:
            return False

        # Setup conditions for current turn
        random_event = self.random_event()
        self.weather_request()
        self._game.advance_location()

        return True

    def random_event(self) -> Event | None:
        random_event = None
        chance = random.randint(1, 4)
        if chance == 1:
            random_event = random.choice(RANDOM_EVENT)
        return random_event

    def new_game(self) -> bool:
        game = Game.new_game()
        self._game = game
        return True if self._game else False

    def load_game(self) -> bool:
        return True

    def save_game(self) -> bool:
        return True

    def weather_request(self) -> tuple:
        cur_temp = None
        cur_precip = None
        try:
            # Setup the Open-Meteo API client with cache and retry on error
            cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
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

        return (cur_temp, cur_precip)


if __name__ == "__main__":
    run = Runner()
    run.new_game()
    print(run.weather_request())
