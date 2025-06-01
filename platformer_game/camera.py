import random


class Camera:
    
    offset_x: float = 0
    offset_y: float = 0
    
    shake_x: int = 0
    shake_y: int = 0
    
    duration: int = 0

    @classmethod
    def convert_pos(cls, pos: tuple[float, float]) -> tuple[float, float]:
        return pos[0] - cls.offset_x + cls.shake_x, pos[1] - cls.offset_y + cls.shake_y
    
    @classmethod
    def convert_to_screen_pos(cls, pos: tuple[float, float]) -> tuple[float, float]:
        return pos[0] + cls.offset_x - cls.shake_x, pos[1] + cls.offset_y - cls.shake_y

    @classmethod
    def shake_screen(cls, duration: int) -> None:
        Camera.duration = duration

    @classmethod
    def update_shake(cls) -> None:
        if Camera.duration:
            Camera.shake_x = random.randint(-1, 1) * Camera.duration
            Camera.shake_y = random.randint(-1, 1) * Camera.duration
            Camera.duration = max(Camera.duration - 1, 0)

        else:
            Camera.max_duration = 1
            Camera.shake_x = 0
            Camera.shake_y = 0

    @property
    def camera_offset(self) -> tuple[float, float]:
        return Camera.offset_x, Camera.offset_y
