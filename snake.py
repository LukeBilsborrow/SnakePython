from constants import Direction as G_Direction
from pygame.math import Vector2 as PG_Vector2
from collections import deque

DEFAULT_SPEED = 1
DEFAULT_SPEED_INCREMENT = 0.03
DEFAULT_SIZE = 3


class Snake:
    direction: G_Direction
    speed: int
    cells: deque[PG_Vector2] = deque()
    prev_tail: PG_Vector2

    def __init__(
        self,
        head_position: PG_Vector2,
        direction: G_Direction,
        speed: int = DEFAULT_SPEED,
        size: int = DEFAULT_SIZE,
    ):
        self.speed = speed
        self.direction = direction

        self.cells.append(head_position)
        # assume we are moving right
        for i in range(1, size):
            self.cells.append(PG_Vector2(head_position.x - i, head_position.y))

    # technically this can also move the snake backwards
    def move_forward(self, distance: float):
        new_position = self.head_position.copy()
        if self.direction == G_Direction.UP:
            new_position.y -= distance

        if self.direction == G_Direction.DOWN:
            new_position.y += distance

        if self.direction == G_Direction.LEFT:
            new_position.x -= distance

        if self.direction == G_Direction.RIGHT:
            new_position.x += distance

        # add the new head position to the list of cells
        self.cells.appendleft(new_position)
        self.prev_tail = self.cells.pop()

    def consume_fruit(self):
        self.cells.append(self.prev_tail)
        # may as well return the tail
        return self.prev_tail

    def is_colliding_with_self(self) -> bool:
        return self.head_position in [x for x in self.cells][1:]

    def is_colliding_with_wall(self, width: int, height: int) -> bool:
        return (
            self.head_position.x < 0
            or self.head_position.y < 0
            or self.head_position.x >= width
            or self.head_position.y >= height
        )

    # we can only grow the snake after we have moved it
    def grow(self):
        self.cells.append(self.prev_tail)

    def increment_speed(self):
        self.speed += self.speed * DEFAULT_SPEED_INCREMENT

    @property
    def head_position(self) -> PG_Vector2:
        return self.cells[0]
