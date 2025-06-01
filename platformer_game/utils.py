import os

import pygame


def load_tile_assets(tile_assets_folder: str, colorkey=(0, 0, 0)) -> dict[str, list[pygame.Surface]]:
    
    tile_assets: dict[str, list[pygame.Surface]] = {}

    for tilename in os.listdir(tile_assets_folder):
        tile_assets[tilename] = []
        for image_filename in os.listdir(os.path.join(tile_assets_folder, tilename)):
            surf = pygame.image.load(os.path.join(tile_assets_folder, tilename, image_filename)).convert()

            surf.set_colorkey(colorkey)

            tile_assets[tilename].append(surf)

    return tile_assets


def load_folder(folderpath: str, colorkey=(0, 0, 0)) -> list[pygame.Surface]:
    images: list[pygame.Surface] = []
    for filename in os.listdir(folderpath):
        surf = pygame.image.load(os.path.join(folderpath, filename)).convert()
        surf.set_colorkey(colorkey)

        images.append(surf)

    return images
