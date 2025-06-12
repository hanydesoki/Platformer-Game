import pygame


class TextInput:

    def __init__(self, pos: tuple[int, int], width: int, height: int, max_chars: int = 20):
        self.window = pygame.display.get_surface()
        self.x, self.y = pos
        self.width, self.height = width, height

        self.max_chars = max_chars

        self.font = pygame.font.SysFont("Arial", 20)

        self.active: bool = False

        self.surf = pygame.Surface((width, height))
        self.surf.fill((0, 100, 0))

        self.rect = self.surf.get_rect(topleft=pos)

        self.text = ""

        self.set_text("")

    def set_text(self, new_text: str) -> None:
        self.text = new_text

        text_surf = self.font.render(self.text, True, "white")
        # text_rect = text_surf.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        self.surf.fill((0, 100, 0))
        self.surf.blit(text_surf, (10, 10))


    def draw(self) -> None:
        self.window.blit(self.surf, (self.x, self.y))


    def update(self, all_events: list[pygame.event.Event]) -> None:

        for event in all_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.set_text(self.text[:-1])

                else:
                    text_unicode = event.unicode

                    self.set_text(self.text + text_unicode)

        self.draw()