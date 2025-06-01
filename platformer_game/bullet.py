import pygame

from .camera import Camera


class Bullet(Camera):

    def __init__(self, pos: tuple[float, float], x_vel: float, y_vel: float, game, owner, max_duration: int = 240):
        super().__init__()

        self.x, self.y = pos
        self.x_vel = x_vel
        self.y_vel = y_vel

        self.game = game

        self.owner = owner

        self.max_duration = max_duration
        self.frame: int = 0

    @property
    def active(self) -> bool:
        return self.frame <= self.max_duration

    def current_index(self) -> tuple[int, int]:
        return int(self.x // self.game.tilemap.tilesize), int(self.y // self.game.tilemap.tilesize)
        
    def draw(self) -> None:
        pygame.draw.circle(
            self.game.display,
            "yellow",
            self.convert_pos((self.x, self.y)),
            2
        )
        pygame.draw.circle(
            self.game.display,
            "black",
            self.convert_pos((self.x, self.y)),
            2,
            1
        )

    def update(self) -> None:
        if self.active:
            self.x += self.x_vel
            self.y += self.y_vel

            self.frame += 1

