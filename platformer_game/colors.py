from typing import Any, Union
import random


COLORS = {
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "green": (0, 255, 0)
}


class ColorPoint:

    def __init__(self, color: Union[tuple[int, ...], str], scale: float):
        self.color: tuple[int, ...] = (0, 0, 0)
        if isinstance(color, str):
            if color.startswith("#"):  # Convert hex to rgb
                self.color = hex_to_rgb(color)
            else:  # Get color from name
                try:
                    self.color = COLORS[color]
                except KeyError:
                    raise ValueError(f"Not a valid color, must be one of these {list(COLORS.keys())}, got {color} instead")
        else:
            self.color = color

        self.scale = scale

    def __repr__(self):
        return f"{self.__class__.__name__}({self.color}, {self.scale})"


class ColorGradient:

    COLOR_GRADIENTS = {
        "rainbow": [
            ColorPoint((255, 0, 0), 0),
            ColorPoint((255, 255, 0), 1),
            ColorPoint((0, 255, 0), 2),
            ColorPoint((0, 200, 255), 3),
            ColorPoint((0, 0, 255), 4),
            ColorPoint((0, 255, 255), 5)
        ],
        "green_to_red": [
            ColorPoint((0, 255, 0), 0),
            ColorPoint((255, 255, 0), 1),
            ColorPoint((255, 0, 0), 2)
        ],

        "white_to_black": [
            ColorPoint((255, 255, 255), 0),
            ColorPoint((0, 0, 0), 1)
        ]
    }

    def __init__(self, *color_points: ColorPoint, auto_scale: bool = True):
        min_scale = min(color_points, key=lambda cp: cp.scale).scale
        max_scale = max(color_points, key=lambda cp: cp.scale).scale
        self.color_points = list(color_points)
        if auto_scale:
            self.color_points = list(map(lambda cp: ColorPoint(cp.color, (cp.scale - min_scale) / (max_scale - min_scale)), color_points))

        self.color_points.sort(key=lambda cp: cp.scale)

    def color_scale(self, scale: float) -> tuple[int, ...]:
        if scale < self.color_points[0].scale:
            return self.color_points[0].color
        if scale > self.color_points[-1].scale:
            return self.color_points[-1].color

        for i in range(len(self.color_points)):
            cp1 = self.color_points[i]
            cp2 = self.color_points[i + 1]

            if cp1.scale <= scale <= cp2.scale:
                new_color = []
                scale_ratio = (scale - cp1.scale) / (cp2.scale - cp1.scale)
                for component_index in range(3):
                    color_diff = cp2.color[component_index] - cp1.color[component_index]
                    new_color.append(round(cp1.color[component_index] + scale_ratio * color_diff))

                return tuple(new_color)

    def reverse(self):
        max_scale = max(self.color_points, key=lambda cp: cp.scale).scale
        self.color_points = [ColorPoint(cp.color, max_scale - cp.scale) for cp in self.color_points]
        self.color_points.reverse()

        return self

    def __call__(self, scale: float) -> tuple[int, ...]:
        return self.color_scale(scale)

    @classmethod
    def from_color_gradient_name(cls, color_gradient_name: str):
        if color_gradient_name not in cls.COLOR_GRADIENTS:
            raise ValueError(f"Argument color_gradient_name must be one of these {list(cls.COLOR_GRADIENTS.keys())}. Got {color_gradient_name} instead;")

        return cls(*cls.COLOR_GRADIENTS[color_gradient_name])


def rgb_to_hex(rgb: tuple[int, ...]) -> str:
    return '%02x%02x%02x' % rgb


def hex_to_rgb(hexa: str) -> tuple[int, ...]:
    hexa = hexa.lstrip('#')
    return tuple(int(hexa[i:i + 2], 16) for i in (0, 2, 4))


def get_random_color() -> tuple[int, int, int]:
    return tuple(random.randint(0, 255) for _ in range(3))

