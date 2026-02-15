import pygame
from .utils import loadImage
from .cards import Card

# Parent Button class
class Button:
    def __init__(self, imagePath, size, posX, posY):
        self.image = loadImage(imagePath, size)
        self.rect = self.image.get_rect()
        self.rect.x = posX
        self.rect.y = posY

    # Return true if pressed
    def handleMouseDown(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouseX, mouseY)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Reset button inheriting from Button
class ResetButton(Button):
    def __init__(self, posX, posY):
        super().__init__(f"{Card.imagePath}/icons8-reset-16.png", (60, 40), posX, posY)

# Undo button inheriting from Button
class UndoButton(Button):
    def __init__(self, posX, posY):
        super().__init__(f"{Card.imagePath}/icons8-undo-16.png", (60, 40), posX, posY)

# Redo button inheriting from Button
class RedoButton(Button):
    def __init__(self, posX, posY):
        super().__init__(f"{Card.imagePath}/icons8-redo-16.png", (60, 40), posX, posY)
