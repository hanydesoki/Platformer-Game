from typing import Callable

import pygame

from .button import Button
from .text_input import TextInput


def get_text_input(message: str, text_check: Callable = None) -> str | None:

    window = pygame.display.get_surface()

    text: str = ""

    loop: bool = True

    pop_up_surf = pygame.Surface((500, 300))
    pop_up_surf.fill((20, 20, 20))
    pop_up_rect = pop_up_surf.get_rect(center=(window.get_width() // 2, window.get_height() // 2))

    clock = pygame.time.Clock()

    ok_button = Button(
        window,
        "OK",
        200,
        40,
        (pop_up_rect.left + 20, pop_up_rect.bottom - 60)
    )

    cancel_button = Button(
        window,
        "Cancel",
        200,
        40,
        (pop_up_rect.right - 220, pop_up_rect.bottom - 60)
    )

    text_input = TextInput(
        (window.get_width() // 2 - pop_up_surf.get_width() // 2 + 20, window.get_height() // 2),
        int(pop_up_surf.get_width() - 40),
        50,
    )

    message_surf = pygame.font.SysFont("Arial", 25, True).render(message, True, "white")
    message_rect = message_surf.get_rect(midbottom=(text_input.rect.centerx, text_input.rect.top - 20))

    while loop:

        all_events = pygame.event.get()

        cancel_button.update()
        ok_button.update()
        text_input.update(all_events)

        if cancel_button.clicked():
            return None
        
        if ok_button.clicked():
            return text_input.text
        
        window.blit(pop_up_surf, pop_up_rect)
        window.blit(message_surf, message_rect)

        cancel_button.draw()
        ok_button.draw()
        text_input.draw()

        clock.tick(60)
        pygame.display.update()
        
    return None


