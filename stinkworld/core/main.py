"""
StinkWorld - Main Game Entry Point
"""
import pygame
import sys
import os
import traceback

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from stinkworld.core.game import Game
from stinkworld.core.settings import Settings
from stinkworld.ui.menus import main_menu
from stinkworld.entities.character_creation import character_creation
from stinkworld.utils.debug import debug_log

def main():
    """Main entry point for the game."""
    try:
        pygame.init()
        settings = Settings()
        screen = pygame.display.set_mode((settings.screen_width, settings.screen_height))
        pygame.display.set_caption("Slop Theft Auto")
        
        # Start with main menu
        running = True
        while running:
            choice = main_menu(screen)
            if choice == 0:  # New Game
                # Create character first
                player = character_creation(screen, settings)
                if player:  # Only start game if character was created
                    game = Game(settings)
                    game.player = player  # Set the created player
                    game.run()
            elif choice == 2:  # Exit
                running = False
        pygame.quit()
    except Exception as e:
        debug_log(f"[FATAL ERROR] {e}\n" + traceback.format_exc())
        raise

if __name__ == "__main__":
    main()