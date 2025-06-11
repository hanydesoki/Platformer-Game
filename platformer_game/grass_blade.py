import math
import random

import pygame

from .camera import Camera


class GrassBlade(Camera):

    grass_colors: list[tuple[int, int, int]] = [
        (0 ,100, 0),
        (0, 150, 0),
        (0, 200, 0)
    ]

    def __init__(self, surface: pygame.Surface, game, pos: tuple[int, int]):
        super().__init__()

        self.surface = surface
        self.game = game

        self.x, self.y = pos

        self.angle = 0

        self.original_surf = pygame.Surface((self.game.tilemap.tilesize, self.game.tilemap.tilesize))
        

        pygame.draw.polygon(
            self.original_surf,
            random.choice(self.grass_colors),
            [
                (self.game.tilemap.tilesize // 2 - 3, self.game.tilemap.tilesize // 2 + 3),
                (self.game.tilemap.tilesize // 2 + 3, self.game.tilemap.tilesize // 2 + 3),
                (self.game.tilemap.tilesize // 2 + random.randint(-3, 3), random.randint(0, 5)),
            ]
        )

        self.original_surf.set_colorkey("black")
        self.surf = self.original_surf.copy()

        self.rect = self.surf.get_rect(center=(self.x, self.y))

    def draw(self) -> None:
        # print(self.convert_pos(self.rect.topleft))
        self.surface.blit(self.surf, self.convert_pos(self.rect.topleft))

    def update_angle(self, source_pos: tuple[int, int]) -> None:
        dist = math.dist(source_pos, self.rect.center)

        self.angle = 40 * int(max((self.game.tilemap.tilesize - dist), 0)) / self.game.tilemap.tilesize * (-1 if source_pos[0] < self.rect.centerx else 1)
        
        self.surf = pygame.transform.rotate(self.original_surf, self.angle)
        self.surf.set_colorkey("black")
        self.rect = self.surf.get_rect(center=(self.x, self.y))

        # pygame.draw.circle(
        #     self.surface,
        #     "red",
        #     self.convert_pos((self.rect.center)),
        #     2
        # )