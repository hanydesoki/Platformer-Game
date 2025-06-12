import pygame


class Button:
    offset: int = 2
    def __init__(self, surface: pygame.Surface, text: str, width: int, height: int, pos: tuple[int, int]):
        self.surface = surface
        self.text = text

        self.width, self.height = width, height
        self.x, self.y = pos

        self.font = pygame.font.SysFont("Arial", 20)

        self.bottom_surf = pygame.Surface((width, height))
        self.bottom_surf.fill("yellow")
        
        self.top_surf = pygame.Surface((width, height))
        self.top_surf.fill((50, 50, 50))
        
        self.bottom_rect = self.bottom_surf.get_rect(topleft=pos)
        self.top_rect = self.top_surf.get_rect(center=(self.bottom_rect.centerx, self.bottom_rect.centery - self.offset))

        text_surf = self.font.render(text, True, "white")
        text_rect = text_surf.get_rect(center=(self.top_surf.get_width() // 2, self.top_surf.get_height() // 2))

        self.top_surf.blit(text_surf, text_rect)

        self.click_history: list[bool, bool] = [False, False]

    def is_hovered(self) -> bool:
        return self.top_rect.collidepoint(pygame.mouse.get_pos())
    
    def manage_click(self) -> None:
        mouse_clicked = pygame.mouse.get_pressed()[0]

        self.click_history = [self.click_history[1]] + [mouse_clicked and self.is_hovered()]
        # print(self.click_history)

    def clicked(self) -> bool:
        return self.click_history == [True, False]
    
    def draw(self) -> None:
        
        self.surface.blit(self.bottom_surf, self.bottom_rect)
        self.surface.blit(self.top_surf, self.top_rect)

    def update(self) -> None:
        self.manage_click()