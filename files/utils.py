import pygame
import os

def loadImage(path, newSize=None):
    base_path = os.path.dirname(os.path.dirname(__file__))
    full_path = os.path.join(base_path, path)
    image = pygame.image.load(full_path)
    if newSize:
        image = pygame.transform.scale(image, newSize)
    return image

