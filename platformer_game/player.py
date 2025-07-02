import math

import pygame

from .entity import Entity
from .camera import Camera
from .bullet import Bullet

class Player(Entity):

    slow_down = 0.5
    blocking_radius = 24

    def __init__(self, surface, pos, game, animation = None, max_hp=3):
        super().__init__(surface, pos, game, animation, max_hp)

        self.status = ""

        self.set_status("Idle")

        self.x_comp: float = 1
        self.y_comp: float = 0

        self.blocking_frame: int = 0
        self.recovery_block: int = 0

        self.blocking_surf = pygame.Surface((100, 100))
        pygame.draw.circle(self.blocking_surf, (0, 100, 255), center=(50, 50), radius=self.blocking_radius)

        self.blocking_surf.set_colorkey("black")

        self.blocking_surf.set_alpha(100)

    def block(self) -> None:
        if self.status in {"Idle", "Walking", "Crouching"} and self.airtime == 0 and self.recovery_block == 0:
            self.set_status("Crouching")
            self.blocking_frame += 1

    def stop_block(self) -> None:
        self.set_status("Idle")
        self.blocking_frame = 0
        self.recovery_block = 15

    @property
    def parry_state(self) -> bool:
        return 0 < self.blocking_frame < 4

    def move_sideway(self, x_vel):
        if self.blocking_frame == 0:
            super().move_sideway(x_vel)        

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
        elif self.collisions["bottom"] and abs(self.x_vel) < 1 and self.status != "Crouching":
            self.set_status("Idle")

        if self.airtime >= 4:
            self.set_status("Jumping")

    def shoot(self) -> None:
        
        if self.status == "Crouching" or self.recovery_block > 0: return

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
        if self.status == "Crouching": return 

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

    def manage_recovery_block(self) -> None:
        self.recovery_block = max(self.recovery_block - 1, 0)

    def draw(self):
        super().draw()

        if self.blocking_frame:
            self.surface.blit(
                self.blocking_surf, 
                self.convert_pos((self.rect.centerx - 50, self.rect.centery - 50))
            )

    def update(self):
        if self.alive:
            # print(self.status)
            self.manage_status()
            self.manage_aim()
            self.manage_recovery_block()
            self.draw_aim()
            super().update()
            
            self.update_camera_pos()
    
