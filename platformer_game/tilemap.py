import json

import pygame

from .camera import Camera


class TileMap(Camera):

    offset_corners = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    offset_without_corners = [(-1, 0), (0, -1), (0, 1), (1, 0)]
    
    def __init__(self, surface: pygame.Surface, assets: dict, tilesize: int = 36):
        self.surface = surface
        self.assets = assets
        self.tilesize = tilesize

        self.tiles: dict[str, dict] = {}
        self.offgrid_elements: list[dict] = []
        self.enemies: dict[str, dict] = {}
        self.grasses: dict[str, dict] = {}

        self.player: dict = {"indexes": (0, 0), "coord": (self.tilesize // 2, self.tilesize)}

    def set_tile(self, indexes: tuple[int, int], tile_type: str, tile_variant: int, layer: int=0) -> None:
        tile_obj = {
            "indexes": indexes,
            "tile_type": tile_type,
            "variant": tile_variant, 
            "layer": layer
        }

        self.tiles[self.get_tile_key(indexes)] = tile_obj

    def get_tile(self, indexes: tuple[int, int]) -> dict | None:
        return self.tiles.get(self.get_tile_key(indexes), None)


    def delete_tile(self, indexes: tuple[int, int]) -> None:
        tile_key = self.get_tile_key(indexes)

        if tile_key in self.tiles:
            del self.tiles[tile_key]

        
    def set_enemy(self, indexes: tuple[int, int]) -> None:
        tile_key = self.get_tile_key(indexes)
        coord = indexes[0] * self.tilesize + int(self.tilesize * 0.5), indexes[1] * self.tilesize + self.tilesize

        enemy_obj = {
            "indexes": indexes,
            "coord": coord,
            "variant": 0
        }

        self.enemies[tile_key] = enemy_obj

    def delete_enemy(self, indexes: tuple[int, int]) -> None:
        tile_key = self.get_tile_key(indexes)

        if tile_key in self.enemies:
            del self.enemies[tile_key]

    def set_player(self, indexes: tuple[int, int]) -> None:
        self.player = {
            "indexes": indexes,
            "coord": (indexes[0] * self.tilesize + self.tilesize // 2, indexes[1] * (1 + self.tilesize))
        }

    

    def set_grass(self, indexes: tuple[int, int]) -> None:
        tile_key = self.get_tile_key(indexes)
        self.grasses[tile_key] = {
            "indexes": indexes,
            "coord": (indexes[0] * self.tilesize, indexes[1] * self.tilesize)
        }

    def delete_grass(self, indexes: tuple[int, int]) -> None:
        tile_key = self.get_tile_key(indexes)
        if tile_key in self.grasses:
            del self.grasses[tile_key]

    def draw_tiles(self) -> None:

        start_x_index = int(Camera.offset_x // self.tilesize)
        end_x_index = int(start_x_index + self.surface.get_width() // self.tilesize)

        start_y_index = int(Camera.offset_y // self.tilesize)
        end_y_index = int(start_y_index + self.surface.get_height() // self.tilesize)

        for i in range(start_x_index - 1, end_x_index + 2):
            for j in range(start_y_index - 1, end_y_index + 2):
                tile = self.get_tile((i, j))

                if tile is not None:
                    indexes = tile["indexes"]
                    tile_type = tile["tile_type"]
                    variant = tile["variant"]
                    self.surface.blit(
                        self.assets["tiles"][tile_type][variant - 1],
                        self.convert_pos((indexes[0] * self.tilesize, indexes[1] * self.tilesize))
                    )

    def load_tiles(self, filepath: str) -> None:
        
        with open(filepath) as f:
            map_obj: dict = json.load(f)

        self.tiles = map_obj.get("tiles", {})
        self.offgrid_elements = map_obj.get("offgrid_elements", [])
        self.enemies = map_obj.get("enemies", {})
        self.grasses = map_obj.get("grasses", {})
        
        player = map_obj.get("player", None)

        if player is not None:
            self.player = player

    def save_tiles(self, filepath: str) -> None:

        map_obj = {
            "tiles": self.tiles,
            "offgrid_elements": self.offgrid_elements,
            "enemies": self.enemies,
            "grasses": self.grasses,
            "player": self.player
        }

        with open(filepath, "w") as f:
            json.dump(map_obj, f)

    @staticmethod
    def get_tile_key(indexes: tuple[int, int]) -> str:
        return ";".join(map(str, indexes))
    



        