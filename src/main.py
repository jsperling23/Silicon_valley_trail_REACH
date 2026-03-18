from runner import Runner
import logging

# Initialize a logger instance, a runner instance, and fill a new game
logger = logging.getLogger(__name__)
logging.basicConfig(filename='silicon_valley.log',
                    encoding='utf-8',
                    format='%(name)s %(asctime)s %(message)s',
                    level=logging.INFO)
game_runner = Runner(logger)
game_runner.start_game()

# Game loop until the game saves
while True:
    logger.info("Game loop started")
    game_runner.new_turn()
    if game_runner._save_flag is True:
        break
    if game_runner._win is True:
        print("You made it! Good Job!!")
        logger.info("Game won")
        break
    elif game_runner._win is False:
        print("Too bad! You have lost, try again!")
        logger.info("Game lost")
        break
