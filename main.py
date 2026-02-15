import sys
import pygame
print("Pygame imported successfully!")
from files.game import SolitaireGame

def main():
    # Initialize pygame
    pygame.init()
    pygame.display.set_caption("Solitaire Classic")
    
    # Start the game
    game = SolitaireGame()
    game.run()

    # End the game
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()

