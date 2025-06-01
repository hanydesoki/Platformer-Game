import os

import pygame

from .tilemap import TileMap
from .utils import load_tile_assets, load_folder
from .player import Player
from .animation import Animation
from .bullet import Bullet
from .enemy import Enemy

class Game:

    collision_tiles = {"Dirt", "Stone"}

    def __init__(self):

        pygame.init()

        self.window: pygame.Surface = pygame.display.set_mode((800, 600))

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

        self.player = Player(self.display, (100, 352), self, self.animations["Player/Idle"].copy())

        self.bullets: list[Bullet] = []
        
        self.enemies: list[Enemy] = [
            Enemy(self.display, (400, 352), self, self.animations["Enemy/Idle"].copy())
        ]

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

                    continue

            bullet.draw()

    def manage_enemies(self) -> None:
        for enemy in self.enemies[:]:
            enemy.update()
            enemy.draw()            

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

            self.window.blit(
                pygame.transform.scale(self.display, (self.disp_size[0] * 2, self.disp_size[1] * 2)), 
                (0, 0)
            )

            pygame.display.update()

            self.clock.tick(60)

        
        pygame.quit()
