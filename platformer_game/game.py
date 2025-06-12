import os
import random
import math

import pygame

from .camera import Camera
from .tilemap import TileMap
from .utils import load_tile_assets, load_folder
from .player import Player
from .animation import Animation
from .bullet import Bullet
from .enemy import Enemy
from .impact import Impact
from .grass_blade import GrassBlade
from .cloud import Cloud

class Game:

    collision_tiles = {"Dirt", "Stone"}

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

        self.impacts: list[Impact] = []

    def load_assets(self, asset_path: str) -> None:
        self.assets = {}

        self.assets["tiles"] = load_tile_assets(os.path.join(asset_path, "Tile_assets"))

        self.assets["characters"] = {}

        for character in os.listdir(os.path.join(asset_path, "Characters")):
            self.assets["characters"][character] = {}
            for animation in os.listdir(os.path.join(asset_path, "Characters", character)):
                self.assets["characters"][character][animation] = load_folder(
                    os.path.join(asset_path, "Characters", character, animation),
                    colorkey=(255, 255, 255)
                )

        # print(self.assets)

    def manage_player_controls(self, key_pressed, all_events) -> None:

        if key_pressed[pygame.K_q]:
            self.player.move_sideway(-1)
        if key_pressed[pygame.K_d]:
            self.player.move_sideway(1)

        if key_pressed[pygame.K_SPACE]:
            self.player.jump()

        for event in all_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
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
                # Check bullet hit player
                if self.player.rect.collidepoint((bullet.x, bullet.y)):
                    self.bullets.remove(bullet)
                    self.player.get_hit(1)
                    self.spawn_impacts(
                            5, 
                            (bullet.x, bullet.y), 
                            (4, 5), 
                            (0, 2), 
                            (150, 0, 0),
                            dissipation=0.4,
                            speed=(0.5, 3)
                        )
                    # if not self.player.alive:
                    #     self.spawn_impacts(
                    #         15, 
                    #         self.player.rect.center, 
                    #         (10, 20), 
                    #         (3, 5), 
                    #         (150, 0, 0),
                    #         dissipation=0.05,
                    #         speed=(0.5, 3)
                    #     )
                    #     Camera.shake_screen(10)
                    

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
                # self.spawn_impacts(
                #     15, 
                #     enemy.rect.center, 
                #     (10, 20), 
                #     (3, 5), 
                #     (150, 0, 0),
                #     dissipation=0.05,
                #     speed=(0.5, 3)
                # )
                # Camera.shake_screen(10)
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
            
            self.player.update()
            self.player.draw()

            self.manage_enemies()
            self.manage_bullets()
            self.manage_impacts()

            self.manage_grasses()
            self.draw_grasses()

            self.tilemap.draw_tiles()
            self.manage_game_over()
            
            self.window.blit(
                pygame.transform.scale(self.display, (self.disp_size[0] * 2, self.disp_size[1] * 2)), 
                (0, 0)
            )
            Camera.update_shake()
            self.manage_and_draw_level_transition()
            pygame.display.update()

            self.clock.tick(60)

