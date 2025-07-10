import os
import random
import math

import pygame

from .camera import Camera
from .tilemap import TileMap
from .utils import load_tile_assets, load_folder, squared_distance
from .player import Player
from .animation import Animation
from .bullet import Bullet
from .enemy import Enemy
from .impact import Impact
from .grass_blade import GrassBlade
from .cloud import Cloud
from .weapon import Weapon, AR, Pistol
from .pick_up import PickUp

class Game:

    collision_tiles = {"Dirt", "Stone"}

    fps: int = 60
    max_fps: int = 60

    game_speed: float = 1

    game_shade: float = 1

    gravity: float = 0.4

    weapons: dict[str, type[Weapon]] = {
        "pistol": Pistol,
        "ar": AR
    }

    def __init__(self, level_selection, window: pygame.Surface, level_path: str):

        self.level_selection = level_selection

        self.window: pygame.Surface = window

        self.level_path = level_path

        self.display = pygame.Surface(self.window.get_size())

        self.disp_size = self.display.get_size()

        self.clock = pygame.time.Clock()

        self.game_loop: bool = True

        self.assets = {}

        self.load_assets("Assets")

        self.animations: dict[str, Animation] = {
            "Player/Idle": Animation(self.assets["characters"]["Player"]["Idle"], 30, True),
            "Player/Walking": Animation(self.assets["characters"]["Player"]["Walking"], 5, True),
            "Player/Jumping": Animation(self.assets["characters"]["Player"]["Jumping"], 20, False),
            "Player/Crouching": Animation(self.assets["characters"]["Player"]["Crouching"], 60, True),
            "Enemy/Idle": Animation(self.assets["characters"]["Enemy"]["Idle"], 30, True),
            "Enemy/Walking": Animation(self.assets["characters"]["Enemy"]["Walking"], 5, True),
            "Enemy/Jumping": Animation(self.assets["characters"]["Enemy"]["Jumping"], 20, False),
        }
        
        self.tilemap = TileMap(self.display, assets=self.assets, tilesize=36)

        self.tilemap.load_tiles(self.level_path)

        self.player = Player(self.display, self.tilemap.player["coord"], self, self.animations["Player/Idle"].copy())
        
        self.bullets: list[Bullet] = []
        

        self.enemies: list[Enemy] = [
            Enemy(self.display, enemy["coord"], self, self.animations["Enemy/Idle"].copy())
            for enemy in self.tilemap.enemies.values()
        ]

        self.grasses: dict[str, list[GrassBlade]] = {}

        for tile_key, grass_obj in self.tilemap.grasses.items():
            x, y = grass_obj["coord"]
            self.grasses[tile_key] = []
            for _ in range(random.randint(4, 10)):
                grass_blade = GrassBlade(
                    self.display,
                    self,
                    (
                        x + random.randint(3, self.tilemap.tilesize - 3),
                        y + self.tilemap.tilesize
                    )
                )
                self.grasses[tile_key].append(grass_blade)

        # print(self.grasses)

        self.weapon_pickups: list[PickUp] = []

        for metadata in self.tilemap.tile_metadata.values():
            if metadata["text"].startswith("weapon___"):
                weapon_name = metadata["text"].split("___")[-1]
                weapon = self.weapons[weapon_name](self, None)
                weapon_surf = pygame.transform.rotozoom(self.assets["weapons"][weapon_name], 0, 0.4)

                weapon_surf.set_colorkey("black")

                pickup = PickUp(
                    self,
                    (metadata["indexes"][0] * self.tilemap.tilesize, metadata["indexes"][1] * self.tilemap.tilesize),
                    weapon_surf
                )

                pickup.content = weapon

                self.weapon_pickups.append(pickup)

        self.impacts: list[Impact] = []

        self.in_level_transition: bool = False
        self.level_transition_frames: int = 0

        self.clouds: list[Cloud] = []

        cloud_surfs = load_folder("Assets/Other/Clouds")

        for _ in range(20):
            cloud = Cloud(
                self.display,
                random.choice(cloud_surfs),
                (random.randint(0, self.display.get_width()), random.randint(0, self.display.get_height())),
                depth=0.03 + random.random() * 0.50,
                speed=random.random() * 0.5 + 0.3
            )

            self.clouds.append(cloud)

        self.clouds.sort(key=lambda c: c.depth)

        

    def load_level(self, level_path: str) -> None:
        self.tilemap.load_tiles(level_path)

        self.player = Player(self.display, self.tilemap.player["coord"], self, self.animations["Player/Idle"].copy())
        
        Camera.offset_x = self.player.rect.centerx - self.tilemap.surface.get_width() // 4
        Camera.offset_y = self.player.rect.centery - self.tilemap.surface.get_height() // 4
        self.bullets: list[Bullet] = []
        

        self.enemies: list[Enemy] = [
            Enemy(self.display, enemy["coord"], self, self.animations["Enemy/Idle"].copy())
            for enemy in self.tilemap.enemies.values()
        ]

        self.grasses: dict[str, list[GrassBlade]] = {}

        for tile_key, grass_obj in self.tilemap.grasses.items():
            x, y = grass_obj["coord"]
            self.grasses[tile_key] = []
            for _ in range(random.randint(4, 10)):
                grass_blade = GrassBlade(
                    self.display,
                    self,
                    (
                        x + random.randint(3, self.tilemap.tilesize - 3),
                        y + self.tilemap.tilesize
                    )
                )
                self.grasses[tile_key].append(grass_blade)

        # print(self.grasses)

        self.weapon_pickups: list[PickUp] = []

        for metadata in self.tilemap.tile_metadata.values():
            if metadata["text"].startswith("weapon___"):
                weapon_name = metadata["text"].split("___")[-1]
                weapon = self.weapons[weapon_name](self, None)
                weapon_surf = pygame.transform.rotozoom(self.assets["weapons"][weapon_name], 0, 0.4)

                weapon_surf.set_colorkey("black")

                pickup = PickUp(
                    self,
                    (metadata["indexes"][0] * self.tilemap.tilesize, metadata["indexes"][1] * self.tilemap.tilesize),
                    weapon_surf
                )

                pickup.content = weapon

                self.weapon_pickups.append(pickup)

        self.impacts: list[Impact] = []

    def load_assets(self, asset_path: str) -> None:
        self.assets = {}

        self.assets["tiles"] = load_tile_assets(os.path.join(asset_path, "Tile_assets"))

        self.assets["characters"] = {}
        self.assets["weapons"] = {}

        for character in os.listdir(os.path.join(asset_path, "Characters")):
            self.assets["characters"][character] = {}
            for animation in os.listdir(os.path.join(asset_path, "Characters", character)):
                self.assets["characters"][character][animation] = load_folder(
                    os.path.join(asset_path, "Characters", character, animation),
                    colorkey=(255, 255, 255)
                )

        for weapon in os.listdir(os.path.join(asset_path, "Weapons")):
            self.assets["weapons"][weapon.split(".")[0]] = pygame.image.load(
                os.path.join(asset_path, "Weapons", weapon)
            ).convert()

    def manage_player_controls(self, key_pressed, all_events) -> None:

        mouse_pressed = pygame.mouse.get_pressed()

        if key_pressed[pygame.K_q]:
            self.player.move_sideway(-1)
        if key_pressed[pygame.K_d]:
            self.player.move_sideway(1)

        if key_pressed[pygame.K_SPACE]:
            self.player.jump()

        if key_pressed[pygame.K_s]:
            self.player.block()
        elif self.player.blocking_frame > 0:
            self.player.stop_block()
            
        # for event in all_events:
        #     if event.type == pygame.MOUSEBUTTONDOWN and mouse_pressed[0]:
        #         self.player.shoot()

        if mouse_pressed[0]:
            self.player.shoot()

    def manage_bullets(self) -> None:
        for bullet in self.bullets[:]:
            bullet.update()
            
            if not bullet.active:
                self.bullets.remove(bullet)
                continue

            collided_tile = self.tilemap.get_tile(bullet.current_index())

            # Check Bullet hit tile
            if collided_tile is not None:
                if collided_tile["tile_type"] in self.collision_tiles:
                    self.bullets.remove(bullet)

                    self.spawn_impacts(
                        5, 
                        (bullet.x, bullet.y), 
                        (6, 12), 
                        (0, 2), 
                        (255, 255, 150),
                        speed=(0.5, 3)
                    )
                    continue
            
            # Check Bullet hit enemy
            if bullet.owner == self.player:
                for enemy in self.enemies[:]:
                    if enemy.rect.collidepoint((bullet.x, bullet.y)):
                        enemy.get_hit(1)
                        self.spawn_impacts(
                            5, 
                            (bullet.x, bullet.y), 
                            (4, 5), 
                            (0, 2), 
                            (150, 0, 0),
                            dissipation=0.4,
                            speed=(0.5, 3)
                        )
                        self.bullets.remove(bullet)
                        break
            else:

                # Player block or parry
                if self.player.status == "Crouching":
                    
                    # Bullet hit shield
                    bullet_squared_dist = squared_distance(self.player.rect.center, (bullet.x, bullet.y))
                    if bullet_squared_dist < pow(self.player.blocking_radius, 2):
                        if self.player.parry_state:
                            bullet.owner = self.player
                            bullet.x_vel *= -2
                            bullet.y_vel *= -2
                            self.set_game_speed(0.05)
                            self.set_game_shade(0.05)
                            Camera.shake_screen(15)
                            self.spawn_impacts(
                                10, 
                                (bullet.x, bullet.y), 
                                (10, 20), 
                                (2, 4), 
                                (100, 100, 255),
                                dissipation=0.05,
                                speed=(2, 3)
                            )
                        else:
                            self.bullets.remove(bullet)
                            self.spawn_impacts(
                                5, 
                                (bullet.x, bullet.y), 
                                (5, 10), 
                                (1, 2), 
                                (100, 100, 255),
                                dissipation=0.1,
                                speed=(2, 3)
                            )
                            continue

                # Check bullet hit player
                if self.player.rect.collidepoint((bullet.x, bullet.y)):
                    self.bullets.remove(bullet)
                    self.player.get_hit(1)
                    Camera.shake_screen(10)
                    self.spawn_impacts(
                            5, 
                            (bullet.x, bullet.y), 
                            (4, 5), 
                            (0, 2), 
                            (150, 0, 0),
                            dissipation=0.4,
                            speed=(0.5, 3)
                        )

                    

            bullet.draw()

    def spawn_impacts(self,
                    n: int,
                    pos: tuple[float, float], 
                    size_range: tuple[float, float],
                    base_size_range: tuple[float, float],
                    color="white",
                    speed: tuple[float, float] = (1, 1),
                    dissipation: float = 0.2
                ) -> list[Impact]:
        for _ in range(n):
            
            impact_speed = speed[0] + random.random() * (speed[1] - speed[0])

            new_impact = Impact(
                self.display,
                (pos),
                random.randint(*size_range),
                base_size_range[0] + random.random() * (base_size_range[1] - base_size_range[0]),
                random.random() * 2 * math.pi,
                self,
                color=color,
                speed=impact_speed,
                dissipation=dissipation
            )
            self.impacts.append(new_impact)

    def manage_enemies(self) -> None:
        for enemy in self.enemies[:]:
            enemy.update()
            enemy.draw()

            if not enemy.alive:
                self.enemies.remove(enemy)

    def manage_impacts(self) -> None:
        for impact in self.impacts[:]:
            impact.update() 
            impact.draw()

            if not impact.active:
                self.impacts.remove(impact)

    def manage_grasses(self) -> None:
        current_index = self.player.get_current_index()
        for index_offset in self.tilemap.offset_corners + [(0, 0)] + [(-1, -2), (0, -2), (1, -2)]:
            neighbors_indexes = (current_index[0] + index_offset[0], current_index[1] + index_offset[1])
            tile_key = self.tilemap.get_tile_key(neighbors_indexes)

            for grass_blade in  self.grasses.get(tile_key, []):
                grass_blade.update_angle(self.player.rect.midbottom)

    def manage_pickup(self) -> None:
        for pickup in self.weapon_pickups[:]:
            pickup.update()
            if self.player.rect.colliderect(pickup.rect) and self.player.weapon_pickup_frame == 0:
                self.weapon_pickups.remove(pickup)
                if self.player.weapon is not None:
                    # print("dropped", self.player.weapon.weapon_name)
                    self.player.drop_weapon()
                    

                self.player.set_weapon(pickup.content)
                # print("picked", self.player.weapon.weapon_name, pickup.content)
            # print(pickup.active, pickup.y, self.tilemap.bottom_bound)
            if not pickup.active:
                self.weapon_pickups.remove(pickup)
        # print([(p.x, p.y) for p in self.weapon_pickups])
    def draw_pickups(self) -> None:
        for pickup in self.weapon_pickups:
            pickup.draw()                

    def draw_grasses(self) -> None:
        for grass_tile in self.grasses.values():
            for grass_blade in grass_tile:
                grass_blade.draw()

    def update_clouds(self) -> None:
        for cloud in self.clouds:
            cloud.update_pos()
            cloud.draw()
            # print(cloud.x, cloud.y)

    def manage_game_over(self) -> None:
        if len(self.enemies) == 0 and not self.in_level_transition:
            self.level_transition_frames = -60
            self.in_level_transition = True

        elif not self.player.alive and not self.in_level_transition:
            self.level_transition_frames = -60
            self.in_level_transition = True

    def manage_and_draw_level_transition(self) -> None:
        if not self.in_level_transition: return

        self.level_transition_frames = self.level_transition_frames + 1

        if self.level_transition_frames >= 60:
            self.in_level_transition = False
            self.level_transition_frames = -60

        if self.level_transition_frames == 0:
            self.load_level(self.level_path)

        surf = pygame.Surface(self.window.get_size())
        pygame.draw.circle(
            surf,
            "red",
            (surf.get_width() // 2, surf.get_height() // 2),
            (abs(self.level_transition_frames) / 60) * max(surf.get_size())
        )
        # print((abs(self.level_transition_frames) / 60) * max(surf.get_size()))
        surf.set_colorkey("red")

        self.window.blit(surf, (0, 0))

    @classmethod
    def set_game_speed(cls, game_speed: float = 1) -> None:
        cls.game_speed = game_speed

    @classmethod
    def set_game_shade(cls, game_shade: float = 1) -> None:
        cls.game_shade = game_shade

    @classmethod
    def manage_game_speed(cls) -> None:
        cls.game_speed = min(cls.game_speed + 0.02, 1)


    @classmethod
    def manage_game_shade(cls) -> None:
        cls.game_shade = min(cls.game_shade + 0.02, 1)
    

    def run(self) -> None:
        
        while self.game_loop:

            all_events: list[pygame.event.Event] = pygame.event.get()
            key_pressed = pygame.key.get_pressed()

            for event in all_events:
                if event.type == pygame.QUIT:
                    self.game_loop = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_loop = False

            self.manage_player_controls(key_pressed, all_events)

            self.display.fill((100, 200, 255))
            self.update_clouds()
            
            shade_surf = pygame.Surface(self.window.get_size())
            shade_surf.set_alpha(int(255 * (1 - self.game_shade)))

            self.display.blit(shade_surf, (0, 0))

            self.player.update()
            self.player.draw()

            self.manage_enemies()
            self.manage_bullets()
            self.manage_impacts()

            self.manage_grasses()
            self.manage_pickup()
            self.draw_grasses()
            self.draw_pickups()

            self.tilemap.draw_tiles()
            self.manage_game_over()
            
            self.window.blit(
                pygame.transform.scale(self.display, (self.disp_size[0] * 2, self.disp_size[1] * 2)), 
                (0, 0)
            )
            Camera.update_shake()
            self.manage_game_speed()
            self.manage_game_shade()
            self.manage_and_draw_level_transition()
            pygame.display.update()

            self.clock.tick(self.fps)

