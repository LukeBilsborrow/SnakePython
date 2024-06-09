from enum import Enum


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


SNAKE_DEFAULT_SPEED = 1
SNAKE_DEFAULT_SPEED_INCREMENT = 0.05
SNAKE_DEFAULT_SIZE = 3
