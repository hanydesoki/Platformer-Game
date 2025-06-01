import os
import datetime

import pygame

from .tilemap import TileMap
from .utils import load_tile_assets
from .camera import Camera


class LevelEditor(Camera):

    offset_corners = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    offset_without_corners = [(-1, 0), (0, -1), (0, 1), (1, 0)]

    autotile_map: dict [tuple[tuple[int, int]], int] = {

        # Corners without middle [#]##
                                  #
                                  #

        tuple(sorted([(0, 1), (1, 0)])): 7, # Top left
        tuple(sorted([(-1, 0), (0, 1)])): 9, # Top right
        tuple(sorted([(0, -1), (1, 0)])): 1, # Bottom left
        tuple(sorted([(-1, 0), (0, -1)])): 3, # Bottom right


        # Side  #
        #      [#]
        #       #

        tuple(sorted([(0, -1), (0, 1), (1, 0)])): 4, # Left
        tuple(sorted([(0, -1), (0, 1), (-1, 0)])): 6, # Right
        tuple(sorted([(-1, 0), (1, 0), (0, -1)])): 2, # Bottom
        tuple(sorted([(-1, 0), (1, 0), (0, 1)])): 8, # Top

        # Center
        tuple(sorted([(0, -1), (0, 1)])): 5,
        tuple(sorted([(-1, 0), (0, -1), (0, 1), (1, 0)])): 5,

    }

    base_camera_speed = 3

    def __init__(self, filepath: str = None, tilesize: int = 36):

        pygame.init()
 
        self.filepath = filepath
        
        self.tilesize = tilesize

        self.window: pygame.Surface = pygame.display.set_mode()
        self.display: pygame.Surface = pygame.Surface(self.window.get_size())

        self.clock = pygame.time.Clock()

        self.game_loop: bool = True

        self.assets = {}

        self.load_assets("Assets")

        self.tile_types = list(self.assets.get("tiles", {}))

        self.tile_type_index: int = 0
        self.tile_variant_index: int = 0

        self.layer: int = 0

        self.tilemap = TileMap(self.display, assets=self.assets, tilesize=tilesize)

        if self.filepath is not None:
            if os.path.exists(self.filepath):
                self.tilemap.load_tiles(self.filepath)

        self.selection_mode: bool = False
        self.selection_1: tuple[int, int] = None
        # self.bottom_right_selection: tuple[int, int] = None
        # self.top_left_selection_rect: tuple[int, int] = None
        self.selection_2: tuple[int, int] = None
        self.selection_1_screen_coord: tuple[int, int] = None
        self.selection_2_screen_coord: tuple[int, int] = None
        self.select_dragging: bool = False
        self.selected_tiles: list[dict] = None

        self.camera_speed_multiplier: float = 1

        self.debugguer_font = pygame.font.SysFont("Arial", 12, True)

    def switch_selection_mode(self) -> None:

        self.selection_mode = not self.selection_mode

        # print(self.selection_mode)

        self.selection_1: tuple[int, int] = None
        self.selection_2: tuple[int, int] = None
        self.selected_tiles: list[dict] = None

        self.select_dragging = False


    # def set_selection_coord(self, pos: tuple[int, int]) -> None:
    #     pos = self.convert_pos(pos)
    #     # Reset selection
    #     if (
    #         self.top_left_selection is None
    #         or (self.top_left_selection is not None and self.bottom_right_selection is not None)
    #     ):
    #         self.top_left_selection = pos
    #         self.bottom_right_selection = None
    #         self.selected_tiles = None

    #         self.select_dragging = True

    #     # Bottom right selection (also work with negative width / height)
    #     elif (
    #         self.top_left_selection is not None
    #         and self.bottom_right_selection is None
    #     ):
    #         left = min(pos[0], self.top_left_selection[0])
    #         top = min(pos[1], self.top_left_selection[1])

    #         width = abs(pos[0] - self.top_left_selection[0])
    #         height = abs(pos[1] - self.top_left_selection[1])

    #         self.top_left_selection = (left, top)
    #         self.bottom_right_selection = (left + width, top + height)

    #         self.selected_tiles = []
    #         for i, j in self.get_selected_indexes():
    #             tile_key = self.tilemap.get_tile_key((i, j))

    #             if tile_key in self.tilemap.tiles:
    #                 self.selected_tiles.append(self.tilemap.get_tile((i, j)))

    #         self.select_dragging = False

    #     print(self.top_left_selection, self.bottom_right_selection)
            

    def get_selected_indexes(self) -> list[tuple[int, int]]:
        
        if (self.selection_1 is None or self.selection_2 is None):
            return []

        # top_left_indexes = self.coord_to_indexes(self.top_left_selection)
        # bottom_right_indexes = self.coord_to_indexes(self.bottom_right_selection)
        s1_indexes = (int(self.selection_1[0] // self.tilesize), int(self.selection_1[1] // self.tilesize))
        s2_indexes = (int(self.selection_2[0] // self.tilesize), int(self.selection_2[1] // self.tilesize))

        left_index = min(s1_indexes[0], s2_indexes[0])
        right_index = max(s1_indexes[0], s2_indexes[0])
        top_index = min(s1_indexes[1], s2_indexes[1])
        bottom_index = max(s1_indexes[1], s2_indexes[1])
        indexes: list[tuple[int, int]] = []

        for i in range(left_index, right_index + 1):
            for j in range(top_index, bottom_index + 1):
                indexes.append((i, j))

        return indexes


    def switch_tile_type(self, direction: int = 1) -> None:
        self.tile_type_index = (self.tile_type_index + direction) % len(self.tile_types)
        self.tile_variant_index = 0

    def switch_tile_variant(self, direction: int = 1) -> None:
        self.tile_variant_index = (self.tile_variant_index + direction) % len(self.assets["tiles"][self.tile_type])

    @property
    def tile_type(self) -> str:
        return self.tile_types[self.tile_type_index]

    def load_assets(self, asset_path: str) -> None:
        self.assets = {}

        self.assets["tiles"] = load_tile_assets(os.path.join(asset_path, "Tile_assets"))


    def manage_camera(self) -> None:

        key_pressed = pygame.key.get_pressed()

        if key_pressed[pygame.K_z]:
            Camera.offset_y += -1 * self.base_camera_speed * self.camera_speed_multiplier
        if key_pressed[pygame.K_s]:
            Camera.offset_y += 1 * self.base_camera_speed * self.camera_speed_multiplier
        if key_pressed[pygame.K_q]:
            Camera.offset_x += -1 * self.base_camera_speed * self.camera_speed_multiplier
        if key_pressed[pygame.K_d]:
            Camera.offset_x += 1 * self.base_camera_speed * self.camera_speed_multiplier

        # print((Camera.offset_x, Camera.offset_y))

    def manage_user_input(self, all_events: list[pygame.event.Event]) -> None:
        
        left_click: bool = False
        right_click: bool = False

        key_pressed = pygame.key.get_pressed()

        self.camera_speed_multiplier = 1

        if key_pressed[pygame.K_LSHIFT]:
            self.camera_speed_multiplier = 3
        
        for event in all_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.switch_tile_type(-1)
                if event.key == pygame.K_RIGHT:
                    self.switch_tile_type(1)
                if event.key == pygame.K_UP:
                    self.switch_tile_variant(-1)
                if event.key == pygame.K_DOWN:
                    self.switch_tile_variant(1)

                if event.key == pygame.K_m:
                    self.switch_selection_mode()

                if event.key == pygame.K_a and self.selected_tiles is not None:
                    self.autotile(self.selected_tiles)

                # Fill
                if event.key == pygame.K_f and self.selection_1 is not None and self.selection_2 is not None:
                    self.selected_tiles.clear()
                    for indexes in self.get_selected_indexes():
                        self.tilemap.set_tile(
                            indexes,
                            self.tile_type,
                            self.tile_variant_index + 1,
                            self.layer
                        )
                        self.selected_tiles.append(self.tilemap.get_tile(indexes))

                # Save 
                if key_pressed[pygame.K_LCTRL] and event.key == pygame.K_s:
                    self.save_map()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pressed = pygame.mouse.get_pressed()
                if mouse_pressed[0]:
                    left_click = True
                elif mouse_pressed[2]:
                    right_click = True

            if left_click:

                if self.selection_mode:
                    mouse_pos = pygame.mouse.get_pos()

                    # Start selection
                    if self.selection_1 is None or (self.selection_1 is not None and self.selection_2 is not None):
                        self.selection_1 = self.convert_to_screen_pos(mouse_pos)
                        self.selection_2 = None
                        self.select_dragging = True
                        self.selected_tiles = None
                        # print("Selection 1", (self.selection_1, self.selection_2), mouse_pos)
                    # Second selection
                    elif self.select_dragging:
                        self.selection_2 = self.convert_to_screen_pos(mouse_pos)

                        self.select_dragging = False

                        self.selected_tiles = []

                        # print("Selection 2", (self.selection_1, self.selection_2), mouse_pos)

                        for i, j in self.get_selected_indexes():

                            tile_key = self.tilemap.get_tile_key((i, j))

                            if tile_key in self.tilemap.tiles:
                                self.selected_tiles.append(self.tilemap.get_tile((i, j)))

                        # print(self.selected_tiles)

                    # self.set_selection_coord(pygame.mouse.get_pos())
                else:
                    self.tilemap.set_tile(
                        self.coord_to_indexes(pygame.mouse.get_pos()),
                        self.tile_type,
                        self.tile_variant_index + 1,
                        self.layer
                    )
            
            if right_click:
                if self.selected_tiles is not None:
                    for tile in self.selected_tiles:
                        self.tilemap.delete_tile(tile["indexes"])
                    self.selected_tiles.clear()
                else:
                    self.tilemap.delete_tile(
                            self.coord_to_indexes(pygame.mouse.get_pos()),
                        )

                # print(self.tilemap.tiles)


    def get_current_tile(self) -> pygame.Surface:
        return self.assets["tiles"][self.tile_type][self.tile_variant_index]
                
    def coord_to_indexes(self, coord: tuple[int, int]) -> tuple[int, int]:
        return int((coord[0] + self.offset_x) // self.tilesize), int((coord[1] + self.offset_y) // self.tilesize)
    
    def draw_grid(self) -> None:
        number_rows: int = int(self.display.get_height() // self.tilesize) + 1
        number_cols: int = int(self.display.get_width() // self.tilesize) + 1

        for i in range(number_rows):
            pygame.draw.line(
                self.display,
                color=(100, 100, 100),
                start_pos=(0, int(-self.offset_y) % self.tilesize + i * self.tilesize),
                end_pos=(self.display.get_width(), int(-self.offset_y) % self.tilesize + i * self.tilesize),
                width=1
            )

        for i in range(number_cols):
            pygame.draw.line(
                self.display,
                color=(100, 100, 100),
                start_pos=(int(-self.offset_x) % self.tilesize + i * self.tilesize, 0),
                end_pos=(int(-self.offset_x) % self.tilesize + i * self.tilesize, self.display.get_height()),
                width=1
            )
        
        # Main axis
        pygame.draw.line(
            self.display,
            color=(200, 200, 0),
            start_pos=(0, -self.offset_y),
            end_pos=(self.display.get_width(), -self.offset_y),
            width=3
        )

        pygame.draw.line(
            self.display,
            color=(200, 200, 0),
            start_pos=(-self.offset_x, 0),
            end_pos=(-self.offset_x, self.display.get_height()),
            width=3
        )

    def draw_selection(self) -> None:

        if not self.selection_mode: return

        if self.selection_2 is not None:
            left = min(self.selection_1[0], self.selection_2[0])
            top = min(self.selection_1[1], self.selection_2[1])
            width = abs(self.selection_1[0] - self.selection_2[0])
            height = abs(self.selection_1[1] - self.selection_2[1])
            pygame.draw.rect(
                self.display,
                color=(100, 255, 100),
                rect=(*self.convert_pos((left, top)), width, height),
                width=3
            )
        elif self.selection_1 is not None:
            mouse_pos = pygame.mouse.get_pos()
            s1 = self.convert_pos(self.selection_1)
            left = min(s1[0], mouse_pos[0])
            top = min(s1[1], mouse_pos[1])
            width = abs(s1[0] - mouse_pos[0])
            height = abs(s1[1] - mouse_pos[1])

            # print(left, top, width, height, mouse_pos, self.selection_1, s1)

            pygame.draw.rect(
                self.display,
                color=(100, 255, 100),
                rect=(left, top, width, height),
                width=3
            )
            
        # print(self.selected_tiles)
        if self.selected_tiles is not None:
            for tile in self.selected_tiles:
                indexes = tile["indexes"]
                pygame.draw.rect(
                    self.display,
                    (255, 100, 0),
                    rect=(*self.convert_pos((indexes[0] * self.tilesize, indexes[1] * self.tilesize)), self.tilesize, self.tilesize),
                    width=2
                )

        # pygame.draw.rect(
        #     self.display,
        #     color=(100, 255, 100),
        #     rect=(left, top, width, height),
        #     width=3
        # )

    def autotile(self, tiles: list[dict]) -> None:

        for tile in tiles:
            sourrounding_tiles = []
            indexes = tile["indexes"]

            for neighbors_index, offset_index in zip(self.get_surrounding_indexes(indexes, False), self.offset_without_corners):
                neighbors_tile = self.tilemap.get_tile(neighbors_index)

                if neighbors_tile is not None:
                    sourrounding_tiles.append(offset_index)

            automap_key = tuple(sorted(sourrounding_tiles))

            # print(automap_key)

            tile["variant"] = self.autotile_map.get(automap_key, 8)


    def get_surrounding_indexes(self, indexes: tuple[int, int], corners: bool = False) -> list[tuple[int, int]]:
        surrounding_tiles: list[tuple[int, int]] = []

        for off_x, off_y in (self.offset_corners if corners else self.offset_without_corners):
            surrounding_tiles.append((indexes[0] + off_x, indexes[1] + off_y))

        return surrounding_tiles
    
    def draw_debugger(self) -> None:

        all_texts: list[str] = [
            f"Current index: {self.coord_to_indexes(pygame.mouse.get_pos())}",
            f"Coords: {self.convert_to_screen_pos(pygame.mouse.get_pos())}",
            f"Total tiles: {len(self.tilemap.tiles)}",
            f"Tiles selected: {len(self.selected_tiles) if self.selected_tiles is not None else 0}",
            f"Selection mode: {self.selection_mode}",
            f"Tile type: {self.tile_type}",
            f"Tile variant: {self.tile_variant_index + 1}",
        ]
        

        for i, text in enumerate(all_texts):
            text_surf = self.debugguer_font.render(text, True, "white")
            text_rect = text_surf.get_rect(topright=(self.display.get_width() - 10, 10 + i * (text_surf.get_height() + 4)))

            self.display.blit(text_surf, text_rect)

        
    def save_map(self) -> None:
        if self.filepath is None:
            self.filepath = f"map_{datetime.datetime.now().isoformat().replace(':', '-').replace('.', '-')}.json"

        self.tilemap.save_tiles(self.filepath)

    def run(self) -> None:
        
        while self.game_loop:

            all_events: list[pygame.event.Event] = pygame.event.get()

            for event in all_events:
                if event.type == pygame.QUIT:
                    self.game_loop = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_loop = False

            self.manage_user_input(all_events)

            self.manage_camera()
            mouse_pos = pygame.mouse.get_pos()

            hovered_indexes = self.coord_to_indexes(mouse_pos)
            mouse_coord = self.convert_pos((
                hovered_indexes[0] * self.tilesize,
                hovered_indexes[1] * self.tilesize,
            ))
            mouse_rect = pygame.Rect(
                *mouse_coord,
                self.tilesize,
                self.tilesize
            )

            current_tile = self.get_current_tile().copy()
            current_tile.set_alpha(100)

            # Draw
            self.display.fill((50, 50, 50))

            self.draw_grid()

            # pygame.draw.rect(
            #     self.display,
            #     (255, 255, 255),
            #     mouse_rect,
            #     width=3
            # )

            self.tilemap.draw_tiles()

            if not self.selection_mode:
                self.display.blit(current_tile, mouse_rect)
            else:
                self.draw_selection()

            self.draw_debugger()

            self.window.blit(self.display, (0, 0))

            pygame.display.update()

            self.clock.tick(60)

        
        pygame.quit()
