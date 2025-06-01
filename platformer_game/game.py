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

class Game:

    collision_tiles = {"Dirt", "Stone"}

    def __init__(self):

        pygame.init()

        self.window: pygame.Surface = pygame.display.set_mode()

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

        self.tilemap.load_tiles("my_map.json")

        self.player = Player(self.display, (200, 652), self, self.animations["Player/Idle"].copy())

        self.bullets: list[Bullet] = []
        
        self.enemies: list[Enemy] = [
            Enemy(self.display, (400, 352), self, self.animations["Enemy/Idle"].copy()),
            Enemy(self.display, (1045, 500), self, self.animations["Enemy/Idle"].copy()),
            Enemy(self.display, (1028, 308), self, self.animations["Enemy/Idle"].copy()),
            Enemy(self.display, (775, 211), self, self.animations["Enemy/Idle"].copy()),
            Enemy(self.display, (660, 560), self, self.animations["Enemy/Idle"].copy()),
        ]

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

            if collided_tile is not None:
                # print(collided_tile)
                if collided_tile["tile_type"] in self.collision_tiles:
                    self.bullets.remove(bullet)
                    # for _ in range(random.randint(3, 6)):
                    #     new_impact = Impact(
                    #         self.display,
                    #         (bullet.x, bullet.y),
                    #         random.randint(6, 12),
                    #         random.random() * 2,
                    #         random.random() * 2 * math.pi,
                    #         color=(255, 255, 150),
                    #         speed=1,
                    #         dissipation=0.2
                    #     )
                    #     self.impacts.append(new_impact)
                    self.spawn_impacts(
                        5, 
                        (bullet.x, bullet.y), 
                        (6, 12), 
                        (0, 2), 
                        (255, 255, 150)
                    )
                    continue
            
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
                            dissipation=0.4
                        )
                        self.bullets.remove(bullet)
            else:
                if self.player.rect.collidepoint((bullet.x, bullet.y)):
                    self.bullets.remove(bullet)
                    self.player.get_hit(1)
                    self.spawn_impacts(
                            5, 
                            (bullet.x, bullet.y), 
                            (4, 5), 
                            (0, 2), 
                            (150, 0, 0),
                            dissipation=0.4
                        )

            bullet.draw()

    def spawn_impacts(self,
                    n: int,
                    pos: tuple[float, float], 
                    size_range: tuple[float, float],
                    base_size_range: tuple[float, float],
                    color="white",
                    speed: float = 1,
                    dissipation: float = 0.2
                ) -> list[Impact]:
        for _ in range(n):
            new_impact = Impact(
                self.display,
                (pos),
                random.randint(*size_range),
                base_size_range[0] + random.random() * (base_size_range[1] - base_size_range[0]),
                random.random() * 2 * math.pi,
                color=color,
                speed=speed,
                dissipation=dissipation
            )
            self.impacts.append(new_impact)

    def manage_enemies(self) -> None:
        for enemy in self.enemies[:]:
            enemy.update()
            enemy.draw()

            if not enemy.alive:
                self.spawn_impacts(
                    15, 
                    enemy.rect.center, 
                    (10, 20), 
                    (3, 5), 
                    (150, 0, 0),
                    dissipation=0.05
                )
                Camera.shake_screen(10)
                self.enemies.remove(enemy)

    def manage_impacts(self) -> None:
        for impact in self.impacts[:]:
            impact.update() 
            impact.draw()

            if not impact.active:
                self.impacts.remove(impact)            

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

            self.tilemap.draw_tiles()

            self.player.update()
            self.player.draw()

            self.manage_enemies()
            self.manage_bullets()
            self.manage_impacts()

            self.window.blit(
                pygame.transform.scale(self.display, (self.disp_size[0] * 2, self.disp_size[1] * 2)), 
                (0, 0)
            )
            Camera.update_shake()
            pygame.display.update()

            self.clock.tick(60)

        
        pygame.quit()
