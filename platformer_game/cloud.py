import pygame

from .camera import Camera


class Cloud(Camera):

    def __init__(self, surface: pygame.Surface, cloud_surf: pygame.Surface, pos: tuple[int, int], depth: float = 1, speed: float = 1):
        super().__init__()

        self.surface = surface
        self.surf = cloud_surf
        self.x, self.y = pos
        self.depth = depth
        self.speed = speed

    def update_pos(self) -> None:
        self.x += self.speed


    def draw(self) -> None:
        x = int(self.x - self.offset_x * self.depth) % (self.surface.get_width() + self.surf.get_width()) - self.surf.get_width()
        y = int(self.y - self.offset_y * self.depth) % (self.surface.get_height() + self.surf.get_height()) - self.surf.get_height()
        self.surface.blit(self.surf, (x, y))