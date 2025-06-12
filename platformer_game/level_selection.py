import os

import pygame


class LevelSelection:

    

    def __init__(self, folderpath: str = None):
        self.game_loop: bool = True

        self.clock = pygame.time.Clock()

    def run(self) -> None:
        
        while self.game_loop:

            all_events: list[pygame.event.Event] = pygame.event.get()

            for event in all_events:
                if event.type == pygame.QUIT:
                    self.game_loop = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_loop = False

            

            pygame.display.update()

            self.clock.tick(60)

        
        pygame.quit()
