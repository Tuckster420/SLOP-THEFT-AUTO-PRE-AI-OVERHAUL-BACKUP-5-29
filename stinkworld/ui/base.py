"""Base UI module."""
import pygame
import textwrap
from stinkworld.utils.debug import debug_log

def draw_wrapped_text(surface, text, font, color, rect, line_height):
    lines = textwrap.wrap(text, width=50)
    y = rect.top
    for line in lines:
        rendered = font.render(line, True, color)
        surface.blit(rendered, (rect.left, y))
        y += line_height

class UI:
    """Base UI class for rendering game interface."""
    
    def __init__(self, settings):
        """Initialize UI."""
        self.settings = settings
        self.font = pygame.font.SysFont(settings.ui_font, settings.ui_font_size)
        self.color = settings.ui_color
    
    def render_text(self, screen, text, x, y):
        """Render text on screen."""
        surface = self.font.render(text, True, self.color)
        screen.blit(surface, (x, y))
    
    def render(self, screen):
        """Render UI elements."""
        # Render FPS counter
        fps = int(pygame.time.Clock().get_fps())
        self.render_text(screen, f"FPS: {fps}", 10, 10)
        
        # Render coordinates
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.render_text(screen, f"Mouse: ({mouse_x}, {mouse_y})", 10, 30)
        
        # Render screen dimensions
        width, height = screen.get_size()
        self.render_text(screen, f"Screen: {width}x{height}", 10, 50)
