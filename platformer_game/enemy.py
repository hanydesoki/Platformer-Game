import math
import random

import pygame

from .entity import Entity
from .bullet import Bullet
from .weapon import Pistol

class Enemy(Entity):

    slow_down = 0.5

    def __init__(self, surface, pos, game, animation = None, max_hp=2):
        super().__init__(surface, pos, game, animation, max_hp)

        self.status = ""

        self.set_status("Idle")

        self.x_comp: float = 1
        self.y_comp: float = 0

        self.player_spotted: bool = False

        # self.shoot_cooldown: int = 0

        self.movement_status: str = "stop"
        self.movement_frame: int = 0

        self.set_weapon(Pistol(self.game, self))
    

    def set_status(self, status: str) -> None:
        if self.status != status:
            self.status = status

            self.animation = self.game.animations[f"Enemy/{self.status}"].copy()

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

        if self.weapon is None: return

        if self.weapon.shoot():

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
        character_center = self.rect.center
        player_pos = self.game.player.rect.center

        x_diff = player_pos[0] - character_center[0]
        y_diff = player_pos[1] - character_center[1]

        # print(x_diff, y_diff)

        norm = math.sqrt(pow(x_diff, 2) + pow(y_diff, 2))

        if norm == 0: return

        x_comp = x_diff / norm
        y_comp = y_diff / norm

        self.player_spotted = False

        if self.coord_insight(self.game.player.rect.center, x_comp, y_comp, 10):
            self.x_comp = x_comp
            self.y_comp = y_comp
            self.player_spotted = True

        self.flip = self.x_comp < 0

    def coord_insight(self, coord: tuple[float, float], x_comp: float, y_comp: float, iteration: int = 10) -> bool:
        x_diff = abs(self.rect.centerx - coord[0])
        y_diff = abs(self.rect.centery - coord[1])
        for i in range(iteration):
            x_increment = i * x_comp * self.game.tilemap.tilesize * 0.8
            y_increment = i * y_comp * self.game.tilemap.tilesize * 0.8
            new_coord = (self.rect.centerx + x_increment, self.rect.centery + y_increment)
            indexes = (int(new_coord[0] // self.game.tilemap.tilesize), int(new_coord[1] // self.game.tilemap.tilesize))

            # pygame.draw.circle(
            #     self.surface,
            #     "red",
            #     self.convert_pos(new_coord),
            #     1
            # )
            if abs(x_increment) >= x_diff and abs(y_increment) >= y_diff:
                return True
            
            tile = self.game.tilemap.get_tile(indexes)

            if tile is not None:
                if tile["tile_type"] in self.game.collision_tiles:
                    return False
                
            

        return False
    
    def manage_ai(self) -> None:

        self.movement_frame = max(self.movement_frame - 1, 0)

        if self.movement_frame == 0:
            self.movement_status = "stop"

        if self.player_spotted:
            self.shoot()
            # self.shoot_cooldown = 120
            self.movement_status = "stop"
            self.movement_frame = 0
            
        if self.movement_status == "stop" and random.random() < 0.01:
            self.movement_status = random.choice(["left", "right"])
            self.x_comp = -1 if self.movement_status == "left" else 1
            self.y_comp = 0
            self.movement_frame = random.randint(30, 45)

        
        if self.movement_status in ["left", "right"]:
            
            current_index = self.get_current_index()

            # Stop enemy movement if the he is close to an edge or wall.  
            front_tile = self.game.tilemap.get_tile((current_index[0] + (-1 if self.movement_status == "left" else 1), current_index[1]))
            front_bottom_tile = self.game.tilemap.get_tile((current_index[0] + (-1 if self.movement_status == "left" else 1), current_index[1] + 1))

            if front_tile is not None:
                if front_tile["variant"] in self.game.collision_tiles:
                    self.movement_status = "stop"
                    self.movement_frame = 0
                    return
                
            if front_tile is None:
                if front_bottom_tile is not None:
                    if front_bottom_tile["variant"] not in self.game.collision_tiles:
                        self.movement_status = "stop"
                        self.movement_frame = 0
                        return
                else:
                    self.movement_status = "stop"
                    self.movement_frame = 0
                    return

            self.move_sideway(-1 if self.movement_status == "left" else 1)


    def draw_aim(self) -> None:
        start_pos = self.rect.center

        # pygame.draw.line(
        #     self.surface,
        #     "red",
        #     self.convert_pos(start_pos),
        #     self.convert_pos((start_pos[0] + self.x_comp * 100, start_pos[1] + self.y_comp * 100))
        # )

        pygame.draw.line(
            self.surface,
            "black",
            self.convert_pos(start_pos),
            self.convert_pos((start_pos[0] + self.x_comp * 10, start_pos[1] + self.y_comp * 10)),
            width=3
        )

        # Draw weapon
        if self.weapon is not None:
            angle = -math.degrees(math.atan2(self.y_comp, self.x_comp))
            surf: pygame.Surface = self.game.assets["weapons"][self.weapon.weapon_name]
            surf = pygame.transform.flip(
                surf,
                self.x_comp < 0,
                False
            )
            surf.set_colorkey("white")
            surf = pygame.transform.rotozoom(
                surf,
                (angle + 90) % 180 - 90,
                0.3
            )
            
            surf.set_colorkey("black")

            self.surface.blit(
                surf,
                self.convert_pos((start_pos[0] + self.x_comp * 10 - surf.get_width() // 2, start_pos[1] + self.y_comp * 10 - surf.get_height() // 2))
            )


    def update(self):
        if self.alive:
            # self.shoot_cooldown = max(self.shoot_cooldown - 1, 0)
            self.manage_status()
            self.manage_aim()
            self.manage_ai()
            self.draw_aim()
            super().update()

        # print(self.player_spotted)
        # print((self.x, self.y), self.rect.midbottom, (self.offset_x, self.offset_y))
    
