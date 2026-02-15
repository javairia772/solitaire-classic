import pygame
from .utils import loadImage
# --------------------creating card and pile classes---------------------#
# card class containing image, position, and size data
class Card:
    # set global card attributes
    size = width, height = 95, 125
    imagePath = "assets"
    suits = ("clubs", "diamonds", "hearts", "spades")

    # set cardback image
    cardbackImage = loadImage(f"{imagePath}/playingCardBack.png", size)

    def __init__(self, number, suit, face_up=False):
        # set main card attributes
        self.number = number
        self.suit = suit
        self.colour = Card.getColour(suit)

        # set image attributes
        self.__faceUp = face_up
        self.image = loadImage(f"{Card.imagePath}/{number}_of_{suit}.png", Card.size)
        self.imageBuffer = self.image if face_up else Card.cardbackImage
        self.rect = self.image.get_rect()

    @staticmethod
    def getColour(suit):
        if suit == "clubs" or suit == "spades":
            return "black"
        return "red"

    @property
    def faceUp(self):
        return self.__faceUp

    @faceUp.setter
    def faceUp(self, faceUp):
        self.__faceUp = faceUp
        # if set face up, change buffer image to card image
        if self.__faceUp:
            self.imageBuffer = self.image
        else:
            self.imageBuffer = Card.cardbackImage
  
    def isOppositeColourTo(self, card):
        # return true if different colours
        return self.colour != card.colour

    def isOneMoreThan(self, card):
        # return true if this card is valued 1 more
        return self.number == card.number + 1

    def draw(self, screen):
        screen.blit(self.imageBuffer, self.rect)

    
    