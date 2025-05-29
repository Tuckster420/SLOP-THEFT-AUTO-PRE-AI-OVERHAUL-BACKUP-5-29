"""Game menus module."""
import pygame
import sys
from stinkworld.utils.debug import debug_log

def main_menu(screen):
    """Display main menu and return user choice."""
    font = pygame.font.SysFont(None, 72)
    title_font = pygame.font.SysFont(None, 100)
    
    # Menu options
    options = ["New Game", "Load Game", "Exit"]
    selected = 0
    
    while True:
        screen.fill((0, 0, 0))
        
        # Draw title
        title = title_font.render("Slop Theft Auto", True, (255, 255, 0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        # Draw menu options
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected else (180, 180, 180)
            text = font.render(option, True, color)
            screen.blit(text, (screen.get_width()//2 - text.get_width()//2, 250 + i*80))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 2  # Exit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return selected
