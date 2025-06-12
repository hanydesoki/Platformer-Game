import os
import shutil

import pygame

from .game import Game
from .level_editor import LevelEditor
from .button import Button
from .camera import Camera
from .popup import get_text_input


class LevelSelection:

    def __init__(self, folderpath: str):
        pygame.init()
        
        self.folderpath = folderpath

        self.window = pygame.display.set_mode()

        self.level_sets: list[str] = os.listdir(self.folderpath)

        self.level_set_font: pygame.font.Font = pygame.font.SysFont("Arial", 20, True)

        self.level_set_surf_rects: list[tuple[pygame.Surface, pygame.Rect]] = []
        self.level_surf_rects: list[tuple[pygame.Surface, pygame.Rect]] = []
         
        self.selected_level_set: str = None

        self.generate_level_set_menu()

        self.game: Game = None
        self.level_editor: LevelEditor = None

        self.return_button = Button(
            self.window,
            "<",
            40,
            20,
            (10, 10)
        )

        self.add_button = Button(
            self.window,
            "+",
            40,
            20,
            (self.window.get_width() // 2 - 20, self.window.get_height() - 60)
        )

        self.game_loop: bool = True

        self.clock = pygame.time.Clock()

        

    def generate_level_set_menu(self) -> None:
        self.level_sets = os.listdir(self.folderpath)
        self.level_set_surf_rects.clear()
        for i, level_set in enumerate(self.level_sets):
            surf = pygame.Surface((int(self.window.get_width() * 0.7), 60))
            surf.fill("gray")
            level_set_text_surf = self.level_set_font.render(level_set, True, "white")

            surf.blit(level_set_text_surf, (20, 20))

            rect = surf.get_rect(topleft=((int(self.window.get_width() * 0.15), 50 + i * (60 + 10))))

            self.level_set_surf_rects.append((surf, rect, level_set))

    def draw_level_menu(self) -> None:
        if self.selected_level_set is None:
            for surf, rect, _ in self.level_set_surf_rects:
                self.window.blit(surf, rect)

        if self.selected_level_set is not None:
            for surf, rect, _ in self.level_surf_rects:
                self.window.blit(surf, rect)

            self.return_button.draw()

        self.add_button.draw()


    def manage_level_selection(self, all_events: list[pygame.event.Event]) -> None:
        left_clicked: bool = False
        right_clicked: bool = False

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        key_pressed = pygame.key.get_pressed()

        ctrl_pressed = key_pressed[pygame.K_LCTRL]

        for event in all_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                left_clicked = mouse_pressed[0]
                right_clicked = mouse_pressed[2]

        if self.selected_level_set is not None:
            if self.return_button.clicked():
                self.selected_level_set = None
                return
        
        # Chose level set
        if (left_clicked or right_clicked) and self.selected_level_set is None:
            for _, rect, level_set in self.level_set_surf_rects:
                if rect.collidepoint(mouse_pos):
                    if left_clicked:
                        self.set_level_set(level_set)
                        
                    elif right_clicked and ctrl_pressed:
                        self.delete_level_set(level_set)

        # Chose level
        elif (left_clicked or right_clicked) and self.selected_level_set is not None:

            for _, rect, level_name in self.level_surf_rects:
                if rect.collidepoint(mouse_pos):
                    if ctrl_pressed and left_clicked:
                        self.level_editor = LevelEditor(self, self.window, os.path.join(self.folderpath, self.selected_level_set, level_name))
                    elif ctrl_pressed and right_clicked:
                        self.delete_level(self.selected_level_set, level_name)
                    elif left_clicked:
                        self.game = Game(self, self.window, os.path.join(self.folderpath, self.selected_level_set, level_name))
                    


        
        if self.add_button.clicked():
            text = get_text_input("Level set name" if self.selected_level_set is None else "Level name")
            if text is None:
                return
            
            if text.strip() == "":
                return
            
            if self.selected_level_set is None:
                self.create_level_set(text)
            else:
                self.create_level(self.selected_level_set, text)

    def delete_level(self, level_set: str, level_name: str) -> None:
        level_path = os.path.join(self.folderpath, level_set, level_name)
        if os.path.exists(level_path):
            os.remove(level_path)
            self.set_level_set(self.selected_level_set)


    def delete_level_set(self, level_set: str) -> None:
        level_set_path = os.path.join(self.folderpath, level_set)

        if os.path.exists(level_set_path):
            shutil.rmtree(level_set_path)
            self.generate_level_set_menu()

    def create_level_set(self, level_set: str) -> None:
        level_set_path = os.path.join(self.folderpath, level_set)
        if not os.path.exists(level_set_path):
            os.makedirs(level_set_path)
            self.generate_level_set_menu()

    def create_level(self, level_set: str, level_name: str) -> None:
        level_path = os.path.join(self.folderpath, level_set, level_name + ".json")
        if not os.path.exists(level_path):
            LevelEditor(self, self.window, level_path).save_map()
            self.set_level_set(self.selected_level_set)

        

    def set_level_set(self, level_set: str) -> None:
        self.selected_level_set = level_set
        self.level_surf_rects.clear()

        for i, level_name in enumerate(os.listdir(os.path.join(self.folderpath, level_set))):
            surf = pygame.Surface((int(self.window.get_width() * 0.7), 60))
            surf.fill("gray")
            level_text_surf = self.level_set_font.render(level_name.split(".")[0], True, "white")

            surf.blit(level_text_surf, (20, 20))

            rect = surf.get_rect(topleft=((int(self.window.get_width() * 0.15), 50 + i * (60 + 10))))

            self.level_surf_rects.append((surf, rect, level_name))

    def update(self, all_events: list[pygame.event.Event]) -> None:
        if self.selected_level_set is not None:
            self.return_button.update()

        self.add_button.update()

        self.manage_level_selection(all_events)
        self.draw_level_menu()

        

    def run(self) -> None:
        
        while self.game_loop:

            all_events: list[pygame.event.Event] = pygame.event.get()

            for event in all_events:
                if event.type == pygame.QUIT:
                    self.game_loop = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_loop = False
            
            self.window.fill("black")

            if self.level_editor is not None:
                self.level_editor.run()
                self.level_editor = None
                Camera.reset_camera()

            if self.game is not None:
                self.game.run()
                self.game = None
                Camera.reset_camera()

            self.update(all_events)

            pygame.display.update()

            self.clock.tick(60)

        
        pygame.quit()
