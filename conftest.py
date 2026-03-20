import pytest
import json

from unittest.mock import MagicMock, patch, mock_open
from src.runner import Runner

MOCK_SAVE_STATE = {
    "Cash": 75,
    "Coffee": 60,
    "Bugs": 10,
    "Morale": 90,
    "Hype": 65,
    "Location": 2,
    "Day": 3
}


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def runner(mock_logger):
    return Runner(mock_logger)


@pytest.fixture
def new_runner(runner):
    with patch("builtins.input", return_value="0"), patch("os.system"):
        runner.start_game()
    return runner


@pytest.fixture
def loaded_runner(runner):
    with patch("builtins.input", side_effect=["1", "0"]), \
         patch("os.system"), \
         patch("os.listdir", return_value=["save1.json"]), \
         patch("builtins.open",
               mock_open(read_data=json.dumps(MOCK_SAVE_STATE))):
        runner.start_game()
    return runner
