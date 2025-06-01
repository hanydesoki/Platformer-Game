import math

import pygame

from .entity import Entity
from .camera import Camera
from .bullet import Bullet

class Player(Entity):

    slow_down = 0.5

    def __init__(self, surface, pos, game, animation = None):
        super().__init__(surface, pos, game, animation)

        self.status = ""

        self.set_status("Idle")

        self.x_comp: float = 1
        self.y_comp: float = 0

    def update_camera_pos(self) -> None:
        Camera.offset_x += ((self.rect.centerx - self.game.tilemap.surface.get_width() // 4) - Camera.offset_x) * 0.1
        Camera.offset_y += ((self.rect.centery - self.game.tilemap.surface.get_height() // 4) - Camera.offset_y) * 0.1
        Camera.offset_x = int(Camera.offset_x)
        Camera.offset_y = int(Camera.offset_y)
        # Camera.offset_x = (self.rect.centerx - self.game.tilemap.surface.get_width() // 4)
        # Camera.offset_y = (self.rect.centery - self.game.tilemap.surface.get_height() // 4)
    

    def set_status(self, status: str) -> None:
        if self.status != status:
            self.status = status

            self.animation = self.game.animations[f"Player/{self.status}"].copy()

    def jump(self) -> None:
        super().jump()
        self.airtime = 4

    def manage_status(self) -> None:
        if self.collisions["bottom"] and abs(self.x_vel) > 1:
            self.set_status("Walking")
        elif self.collisions["bottom"] and abs(self.x_vel) < 1:
            self.set_status("Idle")

        if self.airtime >= 4:
            self.set_status("Jumping")

    def shoot(self) -> None:
        start_pos = self.rect.center

        new_bullet = Bullet(
            (start_pos[0] + self.x_comp * 10, start_pos[1] + self.y_comp * 10),
            self.x_comp * 5,
            self.y_comp * 5,
            self.game,
            self
        )

        self.game.bullets.append(new_bullet)

    def manage_aim(self) -> None:
        screen_center = (self.game.window.get_width() // 2, self.game.window.get_height() // 2)
        mouse_pos = pygame.mouse.get_pos()

        x_diff = mouse_pos[0] - screen_center[0]
        y_diff = mouse_pos[1] - screen_center[1]

        # print(x_diff, y_diff)

        norm = math.sqrt(pow(x_diff, 2) + pow(y_diff, 2))

        if norm == 0: return

        self.x_comp = x_diff / norm
        self.y_comp = y_diff / norm

        self.flip = self.x_comp < 0

    def draw_aim(self) -> None:
        start_pos = self.rect.center

        pygame.draw.line(
            self.surface,
            "red",
            self.convert_pos(start_pos),
            self.convert_pos((start_pos[0] + self.x_comp * 100, start_pos[1] + self.y_comp * 100))
        )

        pygame.draw.line(
            self.surface,
            "black",
            self.convert_pos(start_pos),
            self.convert_pos((start_pos[0] + self.x_comp * 10, start_pos[1] + self.y_comp * 10)),
            width=3
        )

    # def update_surf(self):
    #     super().update_surf()
    #     self.surf = pygame.transform.flip(self.surf, self.flip, False)
    #     self.surf.set_colorkey("white")

    def update(self):
        self.manage_status()
        self.manage_aim()
        self.draw_aim()
        super().update()
        
        self.update_camera_pos()
    
