import pygame

from .camera import Camera


class Weapon(Camera):

    fire_rate: int = 60
    damage: int = 1

    weapon_name: str = None

    def __init__(self, game, owner = None):
        super().__init__()

        self.game = game
        self.owner = owner

        self.cool_down: int = 0

        if self.weapon_name is not None:
            self.surf = self.game.assets["weapons"][self.weapon_name]
        else:
            self.surf = pygame.Surface((50, 20))
            self.surf.fill("purple")

    def set_owner(self, owner) -> None:
        self.owner = owner

    def shoot(self) -> bool:
        if self.cool_down == 0:
            self.cool_down = self.fire_rate
            return True
        
        return False
    
    def update(self) -> None:
        self.cool_down = max(self.cool_down - 1, 0)
    

class Pistol(Weapon):
    fire_rate: int = 45
    damage: int = 1

    weapon_name: str = "pistol"

class AR(Weapon):
    fire_rate: int = 10
    damage: int = 1

    weapon_name: str = "ar"
        
