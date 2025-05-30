import pygame
from typing import List, Dict, Optional
from inventory import Inventory
from items import Item

class InventoryUI:
    def __init__(self, inventory: Inventory):
        self.inventory = inventory
        self.selected_item: Optional[Item] = None
        self.hovered_item: Optional[Item] = None
        self.highlight_timer = 0  # For pulse animation
        self.font = pygame.font.SysFont(None, 24)
        self.slot_size = 50
        self.margin = 10

    def _render_highlight(self, screen: pygame.Surface, x: int, y: int) -> None:
        """Render a pulsing highlight effect for selected/hovered items."""
        if self.highlight_timer > 0 and (self.selected_item or self.hovered_item):
            alpha = min(255, self.highlight_timer * 5)  # Fade out over time
            highlight = pygame.Surface((self.slot_size, self.slot_size), pygame.SRCALPHA)
            highlight.fill((255, 255, 0, alpha))  # Yellow glow
            screen.blit(highlight, (x, y))
            self.highlight_timer -= 1

    def _trigger_highlight(self) -> None:
        """Start the highlight animation (call when item is selected/used)."""
        self.highlight_timer = 30  # ~1 second at 30 FPS

    def render(self, screen: pygame.Surface) -> None:
        """Render inventory with highlights."""
        items = self.inventory.get_inventory_items()
        start_x, start_y = 50, 50

        for i, item in enumerate(items):
            x = start_x + (i % 4) * (self.slot_size + self.margin)
            y = start_y + (i // 4) * (self.slot_size + self.margin)
            
            # Base slot
            pygame.draw.rect(screen, (100, 100, 100), (x, y, self.slot_size, self.slot_size))
            
            # Highlight if selected/hovered
            if item == self.selected_item or item == self.hovered_item:
                self._render_highlight(screen, x, y)
            
            # Item text
            text = self.font.render(item.name[:3], True, (255, 255, 255))
            screen.blit(text, (x + 5, y + 5))

    def handle_input(self, event: pygame.event.Event) -> None:
        """Update selection and trigger highlights."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            self.selected_item = self.hovered_item
            if self.selected_item:
                self._trigger_highlight()
        elif event.type == pygame.MOUSEMOTION:
            self._handle_hover(event.pos)

    def _handle_hover(self, mouse_pos: tuple) -> None:
        """Update hovered item and trigger highlight."""
        items = self.inventory.get_inventory_items()
        start_x, start_y = 50, 50

        for i, item in enumerate(items):
            x = start_x + (i % 4) * (self.slot_size + self.margin)
            y = start_y + (i // 4) * (self.slot_size + self.margin)
            if (x <= mouse_pos[0] <= x + self.slot_size and 
                y <= mouse_pos[1] <= y + self.slot_size):
                self.hovered_item = item
                return
        self.hovered_item = None 