"""UI utility functions."""
import pygame
from stinkworld.utils.debug import debug_log

def draw_wrapped_text(surface, text, font, color, rect, aa=True, bkg=None):
    """Draw text that automatically wraps within a given rectangle.
    
    Args:
        surface: The surface to draw on
        text: The text to draw
        font: The pygame font object to use
        color: The color of the text
        rect: The rectangle to contain the text
        aa: Whether to use anti-aliasing
        bkg: Background color (optional)
    """
    rect = pygame.Rect(rect)
    y = rect.top
    line_spacing = -2

    # Get the height of the font
    font_height = font.size("Tg")[1]

    while text:
        i = 1

        # Determine if the row of text will be outside our area
        if y + font_height > rect.bottom:
            break

        # Determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # If we've wrapped the text, then adjust the wrap to the last word      
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # Render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], aa, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += font_height + line_spacing

        # Remove the text we just blitted
        text = text[i:]

    return y