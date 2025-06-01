import math

import pygame

from .camera import Camera


class Impact(Camera):

    def __init__(
            self, 
            surface: pygame.Surface, 
            pos: tuple[float, float], 
            size: float, 
            base_size: float, 
            angle: float, 
            color="white"
        ):
        super().__init__()
        self.surface = surface

        self.x, self.y = pos
        self.size = size
        self.base_size = base_size
        self.angle = angle

        self.color = color

        self.x_comp = math.cos(self.angle)
        self.y_comp = math.sin(self.angle)

        self.base_x_comp = math.cos(self.angle + math.pi / 2)
        self.base_y_comp = math.sin(self.angle + math.pi / 2)

    @property
    def active(self) -> None:
        return self.base_size > 0

    def draw(self) -> None:
        

        end_pos = (self.x + self.x_comp * (self.size), self.y + self.y_comp * (self.size))
        base_1 = (self.x + self.base_x_comp * (self.base_size), self.y + self.base_y_comp * (self.base_size))
        base_2 = (self.x - self.base_x_comp * (self.base_size), self.y - self.base_y_comp * (self.base_size))

        pygame.draw.polygon(
            self.surface,
            self.color,
            [
                self.convert_pos(end_pos),
                self.convert_pos(base_1),
                self.convert_pos(base_2)
            ]
        )

    def update(self) -> None:
        if self.active:
            print(self.base_size, self.size)
            self.base_size = max(self.base_size - 0.2, 0)
            self.size += 0.2


