import pygame


class Animation:

    def __init__(self, images: list[pygame.Surface], frame_duration: int, loop: bool = True):
        self.images = images
        self.frame_duration = frame_duration
        self.loop = loop

        self.frame: int = 0
        self.current_index: int = 0
        self.active: bool = True

    def reset(self) -> None:
        self.frame = 0
        self.current_index = 0
        self.active = True

    def copy(self) -> "Animation":
        return Animation(self.images, self.frame_duration, self.loop)

    def update(self) -> None:
        if not self.active: return
        # print(self.frame_duration * len(self.images))
        self.frame = (self.frame + 1) % (self.frame_duration * len(self.images))

        self.current_index = int(self.frame / (len(self.images) * self.frame_duration) * len(self.images))

        # print(self.frame, self.current_index)

        if not self.loop and self.current_index >= len(self.images) - 1:
            self.active = False
        
    @property
    def current_image(self) -> pygame.Surface:
        return self.images[self.current_index]
    