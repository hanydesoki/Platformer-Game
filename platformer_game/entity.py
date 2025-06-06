import pygame

from .camera import Camera
from .animation import Animation


class Entity(Camera):

    gravity = 0.4
    slow_down = 1

    def __init__(self, surface: pygame.Surface, pos: tuple[int, int], game, animation: Animation = None, max_hp: int = 1) -> None:
        super().__init__()

        self.surface = surface

        self.x, self.y = pos

        self.game = game

        self.animation = animation

        self.surf = pygame.Surface((30, 64))
        self.surf.fill("green")

        self.rect = self.surf.get_rect(midbottom=pos)

        self.x_vel = 0
        self.y_vel = 0

        self.collisions: dict[str, bool] = {
            "left": False,
            "right": False,
            "bottom": False,
            "top": False
        }

        self.airtime: int = 0

        self.max_speed = 4

        self.jump_vel_y = -8

        self.flip: bool = False

        self.max_hp = max_hp
        self.hp = self.max_hp

    def get_hit(self, damage: int) -> None:
        self.hp = max(self.hp - damage, 0)

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def update_position(self) -> None:
        
        self.collisions = {
            "left": False,
            "right": False,
            "bottom": False,
            "top": False
        }

        surrounding_tiles = self.get_surrounding_tiles()

        # for tile in surrounding_tiles:
        #     pygame.draw.rect(
        #         self.surface,
        #         "yellow",
        #         (*self.convert_pos((tile["indexes"][0] * self.game.tilemap.tilesize, tile["indexes"][1] * self.game.tilemap.tilesize)) ,self.game.tilemap.tilesize, self.game.tilemap.tilesize),
        #         width=1
        #     )

        self.airtime += 1

        if self.x_vel < 0:
            self.x_vel = min(self.x_vel + self.slow_down, 0)
        else:
            self.x_vel = max(self.x_vel - self.slow_down, 0)

        self.y_vel += self.gravity

                # Vertical movement
        self.y += self.y_vel
        self.rect.midbottom = (self.x, self.y)
        collided_tile, collided_tile_rect = self.collide_tile(surrounding_tiles)

        if collided_tile is not None:
            if self.y_vel > 0:
                self.rect.bottom = collided_tile_rect.top
                self.collisions["bottom"] = True
                self.airtime = 0
            else:
                self.rect.top = collided_tile_rect.bottom
                self.collisions["top"] = True

            self.y_vel = 0
            self.x, self.y = self.rect.midbottom

        # Horizontal movement
        self.x += self.x_vel
        self.rect.midbottom = (self.x, self.y)
        collided_tile, collided_tile_rect = self.collide_tile(surrounding_tiles)

        if collided_tile is not None:
            if self.x_vel > 0:
                self.rect.right = collided_tile_rect.left
            else:
                self.rect.left = collided_tile_rect.right

            self.x_vel = 0
            self.x, self.y = self.rect.midbottom


    def collide_tile(self, tiles: list[dict]) -> tuple[dict, pygame.Rect] | None:
        for tile in tiles:
            if tile["tile_type"] in self.game.collision_tiles:
                indexes = tile["indexes"]
                tile_rect = pygame.Rect(
                        indexes[0] * self.game.tilemap.tilesize,
                        indexes[1] * self.game.tilemap.tilesize,
                        self.game.tilemap.tilesize,
                        self.game.tilemap.tilesize,
                    ) 
                if self.rect.colliderect(tile_rect):
                      
                    return tile, tile_rect
                
        return None, None

    def get_surrounding_tiles(self) -> list[dict]:
        current_index = self.get_current_index()
        tiles: list[dict] = []
        for index_offset in self.game.tilemap.offset_corners + [(0, 0)] + [(-1, -2), (0, -2), (1, -2)]:
            neighbors_indexes = (current_index[0] + index_offset[0], current_index[1] + index_offset[1])
            tile = self.game.tilemap.get_tile(neighbors_indexes)
            if tile is not None:
                tiles.append(tile)

        return tiles

    def get_current_index(self) -> tuple[int, int]:
        return int(self.x // self.game.tilemap.tilesize), int(self.y // self.game.tilemap.tilesize)

    def draw(self) -> None:
        self.surface.blit(self.surf, self.convert_pos(self.rect.topleft))

    def update_surf(self) -> None:
        
        if self.animation is not None:
            self.animation.update()

        self.surf = self.animation.current_image if self.animation is not None else pygame.Surface((30, 64))
        self.surf = pygame.transform.flip(self.surf, self.flip, False)
        self.surf.set_colorkey("white")
        self.rect = self.surf.get_rect(midbottom=(self.x, self.y))
        # print(self.surf)
    def jump(self) -> None:
        if not self.airtime:
            self.y_vel = self.jump_vel_y

    def move_sideway(self, x_vel: float) -> None:
        
        self.x_vel = self.x_vel + x_vel

        self.x_vel = max(-self.max_speed, min(self.max_speed, self.x_vel))

    def update(self) -> None:
        self.update_surf()
        self.update_position()        

