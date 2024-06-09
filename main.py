import sys

# This is hacky, but it allows us to have the demo separate from the source code
sys.path.append("./source")
from game import Game

game = Game()
game.run()
