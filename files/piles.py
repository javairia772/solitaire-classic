import pygame
from .utils import loadImage
from .cards import Card
# pile class containing cards
class Pile:
    # pile and card spacing to define gaps between cards
    cardSpacing = 30
    pileSpacing = 140

    # set empty pile image
    emptyPileImage = loadImage(f"{Card.imagePath}/empty_pile_slot.png", Card.size)

    def __init__(self, pile=None, posX=0, posY=0):
        self.posX = posX
        self.posY = posY
        self.pile = pile if pile is not None else []
        self.emptyPileRect = pygame.Rect(posX, posY, Card.size[0], Card.size[1])

    def update(self):
        self.emptyPileRect = pygame.Rect(
            self.posX, self.posY, Card.size[0], Card.size[1]
        )

        for index, card in enumerate(self.pile):
            card.rect.x = self.posX
            card.rect.y = self.posY + index * Pile.cardSpacing


    
    # In piles.py, inside the Pile class
    def addCard(self, card):
        """Add a card to the pile."""
        self.pile.append(card)
        self.update()


    def draw(self, screen):
        # if pile exists
        if self.pile:
            # draw cards
            for card in self.pile:
                card.draw(screen)
        else: 
            # draw empty pile image
            screen.blit(Pile.emptyPileImage, self.emptyPileRect)
    
    def get_state(self):
        """Return a representation of the pile's state."""
        return [{'number': card.number, 'suit': card.suit, 'faceUp': card.faceUp} for card in self.pile]

    def set_state(self, state):
        """Load a saved state into the pile."""
        self.pile = [Card(card['number'], card['suit'], card['faceUp']) for card in state]

# Contains the remaining cards after setting up the tableau
class StockPile(Pile):
    def update(self):
        # update positions of the cards when being placed back in to stock pile
        for card in self.pile:
            card.faceUp = False
            card.rect.x = self.posX
            card.rect.y = self.posY
    
    def get_state(self):
        return super().get_state()  # Or add custom behavior if needed

    def set_state(self, state):
        super().set_state(state)  # Or add custom behavior if needed

# Contains the card(s) pulled from the stock
class WastePile(Pile):
    # move cards to waste pile when mouse button is pressed
    def handleMouseDown(self, stockPile):
        # get mouse position
        mouseX, mouseY = pygame.mouse.get_pos()
        
        if stockPile.emptyPileRect.collidepoint(mouseX, mouseY): 
            if stockPile.pile:
                # move top card into waste pile
                self.pile.append(stockPile.pile.pop())
                self.pile[-1].faceUp = True
                self.update()

            else:
                # return waste pile to stock pile
                self.pile.reverse()
                stockPile.pile = list(self.pile)
                self.pile.clear()
                stockPile.update()

    # overwrite update method
    def update(self):
    # update positions of the cards
        for card in self.pile:
            card.faceUp = True
            card.rect.x = self.posX
            card.rect.y = self.posY

    def get_state(self):
        return super().get_state()  # Or add custom behavior if needed

    def set_state(self, state):
        super().set_state(state)  # Or add custom behavior if needed

# completing 4 of these piles (1 for each suit) will win the game
class FoundationPile(WastePile):
    # overwrite update method
    def update(self):
        # update positions of the cards
        for card in self.pile:
            card.rect.x = self.posX
            card.rect.y = self.posY

    def get_state(self):
        return super().get_state()  # Or add custom behavior if needed

    def set_state(self, state):
        super().set_state(state)  # Or add custom behavior if needed

# When pile is being dragged by cursor
class MovingPile(Pile):
    # inherit pile class
    def __init__(self):
        Pile.__init__(self)
        # keep track of mouse positions
        self.prevMouseX = 0
        self.prevMouseY = 0
        # keep track of previous pile object
        self.previousPile = None

    def handleMouseDown(self, pile):
        # get current mouse position
        mouseX, mouseY = pygame.mouse.get_pos()

        # check if cursor is inside any of the cards in the pile (starting from last card)
        for index, card in reversed(list(enumerate(pile.pile))):
            # if mouse is inside card
            if card.rect.collidepoint(mouseX, mouseY) and card.faceUp: 
                # partition pile into moving pile
                self.pile = pile.pile[index:]
                pile.pile = pile.pile[:index]
                self.previousPile = pile
                
                # set moving pile position to the card
                self.posX = card.rect.x
                self.posY = card.rect.y

                # track position of mouse
                self.prevMouseX = mouseX
                self.prevMouseY = mouseY

                return

    def handleMouseMotion(self):
        # move card with cursor if held
        mouseX, mouseY = pygame.mouse.get_pos()
        
        # move pile based on previous position of mouse
        self.posX += mouseX - self.prevMouseX
        self.posY += mouseY - self.prevMouseY
        self.update()

        self.prevMouseX = mouseX
        self.prevMouseY = mouseY


    def handleMouseUp(self, piles):
        if not self.pile:
            return False

        moving_card = self.pile[0]
        target_pile = None

        # ----------------------------
        # FIND VALID TARGET
        # ----------------------------
        for pile in piles:

            # NON EMPTY PILE
            if pile.pile:
                top_card = pile.pile[-1]

                if moving_card.rect.colliderect(top_card.rect):

                    # FOUNDATION RULE (ascending same suit)
                    if isinstance(pile, FoundationPile):
                        if (moving_card.suit == top_card.suit and
                            moving_card.number == top_card.number + 1):
                            target_pile = pile

                    # TABLEAU RULE (descending opposite color)
                    else:
                        if (moving_card.isOppositeColourTo(top_card) and
                            moving_card.number == top_card.number - 1):
                            target_pile = pile

            # EMPTY PILE
            else:
                if moving_card.rect.colliderect(pile.emptyPileRect):

                    # FOUNDATION: only Ace
                    if isinstance(pile, FoundationPile):
                        if moving_card.number == 1:
                            target_pile = pile

                    # TABLEAU: only King
                    else:
                        if moving_card.number == 13:
                            target_pile = pile

        # ----------------------------
        # APPLY MOVE
        # ----------------------------
        if target_pile:

            # Snap animation (clean alignment)
            for i, card in enumerate(self.pile):
                card.rect.x = target_pile.posX
                card.rect.y = target_pile.posY + i * Pile.cardSpacing

            target_pile.pile.extend(self.pile)
            target_pile.update()

            # Auto flip previous pile top card
            if self.previousPile and self.previousPile.pile:
                top = self.previousPile.pile[-1]
                if not top.faceUp:
                    top.faceUp = True

            self.pile.clear()
            return True

        # ----------------------------
        # INVALID MOVE → RETURN BACK
        # ----------------------------
        else:
            if self.previousPile:
                self.previousPile.pile.extend(self.pile)
                self.previousPile.update()

            self.pile.clear()
            return False





    def get_state(self):
        return super().get_state()  # Or add custom behavior if needed

    def set_state(self, state):
        super().set_state(state)  # Or add custom behavior if needed

    def draw(self, screen):
        if self.pile:
            for card in self.pile:
                # Draw shadow
                shadow = pygame.Surface(Card.size, pygame.SRCALPHA)
                shadow.fill((0, 0, 0, 60))
                screen.blit(shadow, (card.rect.x + 6, card.rect.y + 6))

                # Draw card
                card.draw(screen)


    
    def animate_to_position(self, target_x, target_y, speed=20):
        for card in self.pile:
            dx = target_x - card.rect.x
            dy = target_y - card.rect.y
            card.rect.x += dx // speed
            card.rect.y += dy // speed
