import pygame

from .camera import Camera


class PickUp(Camera):

    def __init__(self, game, pos: tuple[float, float], surf: pygame.Surface = None):
        super().__init__()

        self.game = game
        self.surf = pygame.Surface((30, 30)) if surf is None else surf

        # self.rect = pygame.Rect(pos[0], pos[1], 30, 30)

        self.x_vel = 0
        self.y_vel = 0

        self.x, self.y = pos

        # self.rect.midbottom = (self.x, self.y)
        self.rect = self.surf.get_rect(midbottom=pos)

        self.content = None

        self.pickup_frame: int = 0

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
        return int(self.x // self.game.tilemap.tilesize), int((self.y) // self.game.tilemap.tilesize)

    def check_collision(self) -> dict | None:
        current_inndexes: tuple[int, int] = self.get_current_index()

        for surrouding_tile in self.get_surrounding_tiles():
            if tuple(surrouding_tile["indexes"]) == current_inndexes:
                return surrouding_tile
            
        return None

    def update_pos(self) -> None:

        self.y_vel += self.game.gravity

        self.y += self.y_vel

        collided_tile: dict | None = self.check_collision()

        if collided_tile is not None and self.y_vel:
            tile_rect = pygame.Rect(
                collided_tile["indexes"][0] * self.game.tilemap.tilesize,
                collided_tile["indexes"][1] * self.game.tilemap.tilesize,
                self.game.tilemap.tilesize,
                self.game.tilemap.tilesize,
            )


            if self.y_vel > 0:
                self.y = tile_rect.top - 0.01
            else:
                self.y = tile_rect.bottom

            self.y_vel *= -0.5

            if abs(self.y_vel) <= 0.5:
                self.y_vel = 0

        self.rect.midbottom = (self.x, self.y)
        # print(self.x, self.y, self.y_vel)

        
        if self.x_vel:
            self.x_vel += 0.1 if self.x_vel < 0 else -0.1

        if abs(self.x_vel) < 0.01:
            self.x_vel = 0

        self.x += self.x_vel

        collided_tile: dict | None = self.check_collision()

        if collided_tile is not None and self.x_vel:
            tile_rect = pygame.Rect(
                collided_tile["indexes"][0] * self.game.tilemap.tilesize,
                collided_tile["indexes"][1] * self.game.tilemap.tilesize,
                self.game.tilemap.tilesize,
                self.game.tilemap.tilesize,
            )

            if self.x_vel > 0:
                self.x = tile_rect.left - 1
            elif self.y_vel < 0:
                self.x = tile_rect.right + 1
                
            self.x_vel *= -1

            

    def draw(self) -> None:
        self.game.display.blit(
            self.surf,
            self.convert_pos(self.rect.topleft)
        )
    
    @property
    def active(self) -> bool:
        return self.y < self.game.tilemap.bottom_bound * self.game.tilemap.tilesize

    def update(self) -> None:
        self.pickup_frame = max(self.pickup_frame - 1, 0)
        self.update_pos()
        self.draw()
            
        

        