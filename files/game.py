import sys
import pygame
import random
import time
from .cards import Card
from .piles import Pile, StockPile, WastePile, FoundationPile, MovingPile
from .buttons import UndoButton, RedoButton, ResetButton
from .constants import screenSize, darkGreen
from .utils import loadImage

# ---------------- Deck Class ----------------
class Deck:
    def __init__(self):
        self.cards = [Card(number, suit) for suit in Card.suits for number in range(1, 14)]
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw(self):
        return self.cards.pop() if self.cards else None
# --------------------------------------------

class SolitaireGame:
    def __init__(self):
        # Set up the screen and clock
        self.screen = pygame.display.set_mode(screenSize)
        self.clock = pygame.time.Clock()

        # Initialize game components
        self.piles = []
        self.foundationPiles = []
        self.movingPile = MovingPile()
        self.stockPile = None
        self.wastePile = None
        self.resetButton = ResetButton(posX=1100, posY=710)
        self.undoButton = UndoButton(posX=670, posY=710)
        self.redoButton = RedoButton(posX=870, posY=710)

        self.undo_stack = []
        self.redo_stack = []

        # Time and move tracking
        self.startTime = time.time()
        self.moveCount = 0

        # Flag to reset game
        self.reset = True
        self.setup_game()

        # Set initial state after game setup

    def check_game_complete(self):
        for pile in self.foundationPiles:
            if len(pile.pile) != 13:
                return False
        return True
    

    def display_victory_message(self):
        overlay = pygame.Surface(screenSize)
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 80)
        text = font.render("YOU WIN!", True, (255, 215, 0))
        rect = text.get_rect(center=(screenSize[0]//2, screenSize[1]//2))
        self.screen.blit(text, rect)



    def setup_game(self):
        self.moveCount = 0

        # Clear previous state
        self.piles.clear()
        self.foundationPiles.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()

        # Create deck and shuffle
        deck = Deck()
        deck.shuffle()

        # Create tableau piles
        for i in range(7):
            pile = Pile(posX=100 + i * Pile.pileSpacing, posY=200)
            for j in range(i + 1):
                card = deck.draw()
                if j == i:
                    card.faceUp = True
                pile.addCard(card)
            pile.update()
            self.piles.append(pile)

        # Create foundation piles
        for i in range(4):
            foundation = FoundationPile(posX=600 + i * Pile.pileSpacing, posY=50)
            self.foundationPiles.append(foundation)

        # Create stock pile
        self.stockPile = StockPile(deck.cards, posX=50, posY=50)
        self.stockPile.update()

        # Create waste pile
        self.wastePile = WastePile(posX=200, posY=50)

        # 🔥🔥🔥 ADD THIS BLOCK RIGHT HERE 🔥🔥🔥
        # Save initial state properly
        self.undo_stack.append({
            "piles": [pile.get_state() for pile in self.piles],
            "foundations": [pile.get_state() for pile in self.foundationPiles],
            "stock": self.stockPile.get_state(),
            "waste": self.wastePile.get_state(),
            "moveCount": self.moveCount
        })
        self.redo_stack.clear()



    
    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ----------------------------
            # MOUSE BUTTON DOWN
            # ----------------------------
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Undo
                if self.undoButton.handleMouseDown():
                    self.undo()
                    return

                # Redo
                if self.redoButton.handleMouseDown():
                    self.redo()
                    return

                # Reset
                if self.resetButton.handleMouseDown():
                    self.reset = True
                    return

                # Left Click
                if event.button == 1:

                    mouseX, mouseY = pygame.mouse.get_pos()

                    # STOCK CLICK
                    if self.stockPile.emptyPileRect.collidepoint(mouseX, mouseY):
                        self.save_state()
                        self.wastePile.handleMouseDown(self.stockPile)
                        self.moveCount += 1
                        return

                    # PICK FROM TABLEAU
                    for pile in self.piles:
                        self.movingPile.handleMouseDown(pile)

                    # PICK FROM WASTE
                    self.movingPile.handleMouseDown(self.wastePile)

                    # PICK FROM FOUNDATION
                    for pile in self.foundationPiles:
                        self.movingPile.handleMouseDown(pile)

            # ----------------------------
            # MOUSE MOTION (DRAGGING)
            # ----------------------------
            elif event.type == pygame.MOUSEMOTION:
                if self.movingPile.pile:
                    self.movingPile.handleMouseMotion()

            # ----------------------------
            # MOUSE BUTTON UP (DROP)
            # ----------------------------
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.movingPile.pile:

                    # Save previous state BEFORE move
                    previous_state = {
                        "piles": [pile.get_state() for pile in self.piles],
                        "foundations": [pile.get_state() for pile in self.foundationPiles],
                        "stock": self.stockPile.get_state(),
                        "waste": self.wastePile.get_state(),
                        "moveCount": self.moveCount
                    }

                    moved = self.movingPile.handleMouseUp(
                        self.piles + self.foundationPiles
                    )

                    if moved:
                        self.undo_stack.append(previous_state)
                        self.redo_stack.clear()
                        self.moveCount += 1



    def draw_status_bar(self):
        elapsed = int(time.time() - self.startTime)
        minutes = elapsed // 60
        seconds = elapsed % 60

        font = pygame.font.Font(None, 32)

        pygame.draw.rect(self.screen, (20, 100, 20),
                        (0, screenSize[1] - 70, screenSize[0], 70))

        timeText = font.render(f"Time: {minutes:02}:{seconds:02}", True, (255,255,255))
        movesText = font.render(f"Moves: {self.moveCount}", True, (255,255,255))

        self.screen.blit(timeText, (50, screenSize[1] - 45))
        self.screen.blit(movesText, (250, screenSize[1] - 45))

        self.undoButton.draw(self.screen)
        self.redoButton.draw(self.screen)
        self.resetButton.draw(self.screen)

        label_font = pygame.font.Font(None, 32)

        undoText = label_font.render("Undo", True, (255,255,255))
        redoText = label_font.render("Redo", True, (255,255,255))
        resetText = label_font.render("Reset", True, (255,255,255))

        self.screen.blit(undoText, (self.undoButton.rect.x, self.undoButton.rect.y + 28))
        self.screen.blit(redoText, (self.redoButton.rect.x, self.redoButton.rect.y + 28))
        self.screen.blit(resetText, (self.resetButton.rect.x, self.resetButton.rect.y + 28))


    def run(self):
        # Main game loop
        while True:
            if self.reset:
                self.setup_game()
                self.reset = False

            self.handle_events()

            # Render game objects
            # self.screen.fill(darkGreen)
            for y in range(screenSize[1]):
                color = (
                    20,
                    90 + y // 20,
                    40
                )
                pygame.draw.line(self.screen, color, (0, y), (screenSize[0], y))
            for pile in self.piles: 
                pile.draw(self.screen)
            for pile in self.foundationPiles: 
                pile.draw(self.screen)
            self.stockPile.draw(self.screen)
            self.wastePile.draw(self.screen)
            self.movingPile.draw(self.screen)
            self.draw_status_bar()

            # Check for game completion
            if self.check_game_complete():
                self.display_victory_message()
                
            pygame.display.flip()
            self.clock.tick(60)

    def save_state(self):
        state = {
            "piles": [pile.get_state() for pile in self.piles],
            "foundations": [pile.get_state() for pile in self.foundationPiles],
            "stock": self.stockPile.get_state(),
            "waste": self.wastePile.get_state(),
            "moveCount": self.moveCount
        }
        self.undo_stack.append(state)
        self.redo_stack.clear()


    def load_state(self, state):
        for pile, saved in zip(self.piles, state["piles"]):
            pile.set_state(saved)
            pile.update()

        for pile, saved in zip(self.foundationPiles, state["foundations"]):
            pile.set_state(saved)
            pile.update()

        self.stockPile.set_state(state["stock"])
        self.stockPile.update()

        self.wastePile.set_state(state["waste"])
        self.wastePile.update()

        self.moveCount = state["moveCount"]

    def undo(self):
        if len(self.undo_stack) > 1:
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)

            previous_state = self.undo_stack[-1]
            self.load_state(previous_state)

    
    def get_current_state(self):
        return {
            "piles": [pile.get_state() for pile in self.piles],
            "foundations": [pile.get_state() for pile in self.foundationPiles],
            "stock": self.stockPile.get_state(),
            "waste": self.wastePile.get_state(),
            "moveCount": self.moveCount
        }



    
    def redo(self):
        if self.redo_stack:

            current_state = {
                "piles": [pile.get_state() for pile in self.piles],
                "foundations": [pile.get_state() for pile in self.foundationPiles],
                "stock": self.stockPile.get_state(),
                "waste": self.wastePile.get_state(),
                "moveCount": self.moveCount
            }

            self.undo_stack.append(current_state)

            next_state = self.redo_stack.pop()
            self.load_state(next_state)

    


