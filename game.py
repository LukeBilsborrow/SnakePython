import random
from events import EventHandler
import constants as G_const
import pygame
from snake import Snake as G_Snake
from pygame.math import Vector2 as PG_Vector2
import math


class Game:
    handler: EventHandler
    next_direction: G_const.Direction | None = None
    snake: G_Snake
    dt: float = 0
    finished = False

    # stores the current amount of accrued movement
    movement: float = 0

    # game over flags
    snake_collision = False
    wall_collision = False

    # the dimension of the square the grid should occupy
    gui_board_dimension: int

    # the calculated size for each grid tile
    gui_tile_size: int

    # the number of tiles along one axis
    board_tiles: int

    fruit_position: PG_Vector2 | None = None
    draw_rate = 0.01
    accrued_time = 0

    player_score: int = 0

    # this should be calculated based on the speed of the snake
    tick_rate = 0.1

    font: pygame.font.Font | None = None

    ui_height: int = 0
    resolution: int = None

    player_score: int = 0

    def __init__(self, board_tiles: int = 10, base_speed: float = 4, resolution: int = 801):
        # first calculate the

        self.handler = EventHandler()
        self.add_event_handlers()
        self.board_tiles = board_tiles

        self.handle_resolution_calculation(resolution)

        self.clock = pygame.time.Clock()
        self.next_direction = G_const.Direction.RIGHT
        self.snake = G_Snake(PG_Vector2(3, 3), self.next_direction, base_speed)
        #
        # additional setup
        pygame.font.init()
        font_size = int((self.ui_height * 1.45))
        self.font = pygame.font.SysFont("chalkduser.tff", font_size)
        print(f"font size: {font_size}")

    def handle_resolution_calculation(self, resolution: int):
        self.resolution = resolution

        # 15% of the vertical height of the screen should be for the ui
        self.ui_height = int(resolution * 0.1)
        print(f"ui height: {self.ui_height}")
        self.game_area_height = resolution

        self.setup_board_size()

    def setup_board_size(self):
        print(f"game area height: {self.game_area_height}", f"board tiles: {self.board_tiles}")
        optimal_size, tile_size = get_optimal_grid_size(self.game_area_height, self.board_tiles)
        print(f"optimal size: {optimal_size}, tile size: {tile_size}")
        self.content_padding = self.game_area_height - optimal_size
        self.ui_height += self.content_padding
        self.gui_board_dimension = optimal_size
        self.gui_tile_size = tile_size

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.resolution, self.resolution * 1.1))
        self.spawn_fruit()
        self.render()
        while not self.finished:

            self.handler.update()
            self.accrued_time += self.dt
            if self.accrued_time >= self.tick_rate:
                ticks = int(self.accrued_time // self.tick_rate)
                remaining_time = self.accrued_time % self.tick_rate
                self.accrued_time = remaining_time
                self.tick(ticks)

            if self.finished:
                break

            delta_rate = 1 / self.tick_rate * 5
            self.dt = self.clock.tick(delta_rate) / 1000

        # handle the break conditions (snake collision, wall collision)
        if self.snake_collision:
            print("Snake collision")

        if self.wall_collision:
            print("Wall collision")

        pygame.quit()

    # this is called each time the snake should move
    def tick(self, ticks: int):
        for _ in range(ticks):
            self.update()
            if self.finished:
                break

    def set_next_direction(self, direction: G_const.Direction):
        self.next_direction = direction

    def update(self):
        self.do_snake_movement()
        # set the new tick rate based on the snake's speed
        self.tick_rate = 1 / self.snake.speed

    def do_snake_movement(self) -> None:
        """Move the snake forward by 1 square"""
        self.handle_snake_movement()

    def handle_snake_movement(self):
        # we move one step
        self.snake.direction = self.next_direction
        self.snake.move_forward(1)
        self.on_enter_new_square(self.snake.head_position)

    def render(self):
        self.screen.fill((0, 0, 0))
        square_count = self.gui_board_dimension
        square_size = self.gui_tile_size
        padding: int = self.game_area_height - self.gui_board_dimension
        self.draw_grid(self.screen, square_count, square_size, self.board_tiles, padding=padding)
        self.draw_snake(pygame.display.get_surface(), self.snake, square_size, padding=padding)
        self.draw_fruit(pygame.display.get_surface(), self.fruit_position, square_size, padding=padding)

        pygame.display.flip()
        pygame.display.update()
        # draw the snake head

    def on_enter_new_square(self, square: PG_Vector2) -> None:
        # if there is a fruit in the square, eat it
        # if there is a wall in the square, die
        if self.snake.is_colliding_with_self():
            self.handle_snake_collision()
            return

        if self.snake.is_colliding_with_wall(self.board_tiles, self.board_tiles):
            self.handle_wall_collision()
            return

        # check if the snake has eaten a fruit
        if square == self.fruit_position:
            self.on_fruit_eaten()

        self.render()

    def on_fruit_eaten(self):
        # increase the snake's length
        # increase the snake's speed
        self.snake.grow()
        self.snake.increment_speed()
        self.player_score += 1
        # spawn new fruit
        self.spawn_fruit()

    def spawn_fruit(self):
        # this should always be run after the snake has moved
        # we need to make sure the fruit is not in the same square as the snake
        total_squares = self.board_tiles**2
        # turn each cell into a single number
        illegal_positions = [int(cell.x + cell.y * self.board_tiles) for cell in self.snake.cells]

        rand_index = random.randint(0, (total_squares - 1) - len(illegal_positions))
        i = 0
        fruit_pos = None
        for idx in range(total_squares):
            if idx in illegal_positions:
                continue

            if i == rand_index:

                x = idx % self.board_tiles
                y = idx // self.board_tiles
                fruit_pos = PG_Vector2(x, y)
            i += 1

        print(f"fruit pos: {fruit_pos}")
        self.fruit_position = fruit_pos

    def handle_snake_collision(self):
        self.snake_collision = True
        self.finished = True

    def handle_wall_collision(self):
        self.wall_collision = True
        self.finished = True

    def handle_g_key(self) -> None:
        self.finished = True

    def add_event_handlers(self):
        self.handler.add_handler(pygame.K_UP, self.handle_up_key)
        self.handler.add_handler(pygame.K_DOWN, self.handle_down_key)
        self.handler.add_handler(pygame.K_LEFT, self.handle_left_key)
        self.handler.add_handler(pygame.K_RIGHT, self.handle_right_key)
        self.handler.add_handler(pygame.K_g, self.handle_g_key)

    def handle_up_key(self) -> None:
        if self.snake.direction in [G_const.Direction.LEFT, G_const.Direction.RIGHT]:
            self.set_next_direction(G_const.Direction.UP)

    def handle_down_key(self) -> None:
        if self.snake.direction in [G_const.Direction.LEFT, G_const.Direction.RIGHT]:
            self.set_next_direction(G_const.Direction.DOWN)

    def handle_left_key(self) -> None:
        if self.snake.direction in [G_const.Direction.UP, G_const.Direction.DOWN]:
            self.set_next_direction(G_const.Direction.LEFT)

    def handle_right_key(self) -> None:
        if self.snake.direction in [G_const.Direction.UP, G_const.Direction.DOWN]:
            self.set_next_direction(G_const.Direction.RIGHT)

    def draw_grid(
        self,
        screen: pygame.Surface,
        grid_dim: int,
        tile_size: int,
        board_tiles: int,
        padding=0,
    ):
        start_pad = 0
        end_pad = math.floor(padding / 2)
        max_dim = (start_pad + grid_dim) - 1
        img = self.font.render(f"Score: {self.player_score}", True, (255, 0, 0))
        rect = img.get_rect()
        pygame.draw.rect(img, (0, 0, 255), rect, 1)
        screen.blit(img, (0, 0))
        for i in range(board_tiles + 1):
            # vertical
            x_start = 1 if i == 0 else tile_size
            new_sum = i * (tile_size - 1)
            x_start = start_pad + new_sum
            # x_start = start_pad + max((i * (tile_size - 1)) - 1, 0)
            # vertical
            pygame.draw.line(
                screen, (255, 0, 0), (x_start, start_pad + self.ui_height), (x_start, max_dim + self.ui_height)
            )
            pygame.draw.line(
                screen, (255, 0, 0), (start_pad, x_start + self.ui_height), (max_dim, x_start + self.ui_height)
            )

        # dist_sum = 0
        # while dist_sum <= grid_dim - 1:
        #     cur_dim += dist_sum
        #     pygame.draw.line(screen, (255, 0, 0), (cur_dim, start_pad), (cur_dim, max_dim))
        #     pygame.draw.line(screen, (255, 0, 0), (start_pad, cur_dim), (max_dim, cur_dim))

        #     dist_sum += tile_size - 1 if dist_sum != 0 else tile_size

    def draw_snake(self, screen: pygame.Surface, snake: G_Snake, tile_size: int, padding=0):
        # print(f"draw_snake: {tile_size}")
        start_pad = 0

        # draw the snake head
        head = snake.cells[0]
        x = start_pad + int(head.x * (tile_size - 1))
        y = start_pad + int(head.y * (tile_size - 1))
        pygame.draw.rect(screen, (0, 255, 0), (x, y + self.ui_height, tile_size, tile_size))

        for cell in [x for x in snake.cells][1:]:
            x = start_pad + int(cell.x * (tile_size - 1))
            y = start_pad + int(cell.y * (tile_size - 1))

            pygame.draw.rect(screen, (0, 0, 255), (x, y + self.ui_height, tile_size, tile_size))
            # use the bottom line to show the grid lines through the snake
            # pygame.draw.rect(screen, (0, 0, 255), (x + 1, y + 1, tile_size - 2, tile_size - 2))

        return

    def draw_fruit(self, screen: pygame.Surface, fruit_pos: PG_Vector2, tile_size: int, padding=0):
        start_pad = 0
        x = start_pad + int(fruit_pos.x * (tile_size - 1))
        y = start_pad + int(fruit_pos.y * (tile_size - 1))
        pygame.draw.rect(screen, (255, 0, 0), (x, y + self.ui_height, tile_size, tile_size))


def get_resulting_grid_size(square_size: int, num_squares: int) -> int:
    """Calculate the total size of the grid based on the square size and the number of squares.

    Args:
        square_size (int): The size of each square in the grid.
        num_squares (int): The number of squares in the grid.

    Returns:
        int: The total size of the grid.
    """
    total_size = square_size
    total_size += (num_squares - 1) * (square_size - 1)

    return total_size


def get_optimal_grid_size(dimension: int, num_tiles: int) -> tuple[int, int]:
    """Calculate the optimal grid size based on the dimension and the number of squares.
       Gets the overall grid dimension where each square is as large as possible.
       The overall size will be at most equal to the dimension.

    Args:
        dimension (int): The target dimension to fit the grid into.
        num_squares (int): The number of squares in the grid.

    Returns:
        tuple[int, int]: The total size of the grid and the size of each square.
    """
    new_dim = dimension + (num_tiles - 1)
    tile_size = new_dim // num_tiles

    return get_resulting_grid_size(tile_size, num_tiles), tile_size
