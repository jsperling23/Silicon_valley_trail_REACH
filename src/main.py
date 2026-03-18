from runner import Runner

# Initialize a runner instance and fill a new game
game_runner = Runner()
game_runner.start_game()

# Game loop until the game saves
while True:
    game_runner.new_turn()
    if game_runner._save_flag is True:
        break
    if game_runner._win is True:
        print("You made it! Good Job!!")
        break
    elif game_runner._win is False:
        print("Too bad! You have lost, try again!")
        break
