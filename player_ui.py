import pygame
from inventory_ui import InventoryUI

class PlayerUI:
    def __init__(self, player, inventory):
        self.player = player
        self.inventory = inventory
        self.is_open = False
        self.font = pygame.font.SysFont(None, 24)
        self.inventory_ui = InventoryUI(inventory)
        self.action_feedback = {
            "message": "",
            "timer": 0,
            "color": (255, 255, 255)
        }

    def toggle_ui(self):
        """Toggle UI with debug prints."""
        self.is_open = not self.is_open
        print(f"[DEBUG] UI State: {'OPEN' if self.is_open else 'CLOSED'}")  # Debug toggle state
        try:
            if self.is_open:
                pygame.mixer.Sound.play(pygame.mixer.Sound("open_inventory.wav"))
            else:
                pygame.mixer.Sound.play(pygame.mixer.Sound("close_inventory.wav"))
        except Exception as e:
            print(f"[DEBUG] Sound error: {e}")  # Debug sound issues

    def _show_feedback(self, message: str, color=(255, 255, 255)) -> None:
        """Show a temporary message with optional color coding."""
        self.action_feedback["message"] = message
        self.action_feedback["timer"] = 60  # ~2 seconds at 30 FPS
        self.action_feedback["color"] = color

    def _render_feedback(self, screen: pygame.Surface) -> None:
        """Render the current feedback message."""
        if self.action_feedback["timer"] > 0:
            text = self.font.render(
                self.action_feedback["message"], 
                True, 
                self.action_feedback["color"]
            )
            screen.blit(text, (50, screen.get_height() - 50))
            self.action_feedback["timer"] -= 1

    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle input with visual feedback for actions."""
        if not self.is_open:
            return False

        # Delegate to InventoryUI first
        self.inventory_ui.handle_input(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u and self.inventory_ui.selected_item:
                if self.inventory.use_item(self.inventory_ui.selected_item):
                    self._show_feedback(f"Used {self.inventory_ui.selected_item.name}!", (0, 255, 0))
                else:
                    self._show_feedback("Can't use that!", (255, 0, 0))
                return True
            
            elif event.key == pygame.K_e and self.inventory_ui.selected_item:
                if self.inventory.equip_item(self.inventory_ui.selected_item, "hands"):
                    self._show_feedback(f"Equipped {self.inventory_ui.selected_item.name}!", (0, 255, 0))
                else:
                    self._show_feedback("Can't equip that!", (255, 0, 0))
                return True

        return False

    def render(self, screen: pygame.Surface) -> None:
        """Render UI with debug prints."""
        print(f"[DEBUG] Rendering UI. is_open={self.is_open}", end='\r')  # Debug render call
        if not self.is_open:
            return

        # Semi-transparent background (pauses gameplay)
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Render core UI and inventory
        self._render_stats(screen)
        self._render_injuries(screen)
        self.inventory_ui.render(screen)
        self._render_feedback(screen)

    def _render_stats(self, screen):
        stats = [
            f"Health: {self.player.health if hasattr(self.player, 'health') else 'N/A'}",
            f"Stamina: {self.player.stamina if hasattr(self.player, 'stamina') else 'N/A'}"
        ]
        y_offset = 50
        for stat in stats:
            text = self.font.render(stat, True, (255, 255, 255))
            screen.blit(text, (50, y_offset))
            y_offset += 30

    def _render_injuries(self, screen):
        # Default to healthy if no injury data
        injuries = getattr(self.player, 'injuries', {})
        limb_colors = {
            'head': (0, 255, 0) if injuries.get('head', 0) == 0 else (255, 0, 0),
            'left_arm': (0, 255, 0) if injuries.get('left_arm', 0) == 0 else (255, 0, 0),
            'right_arm': (0, 255, 0) if injuries.get('right_arm', 0) == 0 else (255, 0, 0),
            'left_leg': (0, 255, 0) if injuries.get('left_leg', 0) == 0 else (255, 0, 0),
            'right_leg': (0, 255, 0) if injuries.get('right_leg', 0) == 0 else (255, 0, 0)
        }

        # Draw stick figure with injury overlays
        center_x, center_y = screen.get_width() // 2, screen.get_height() // 2
        pygame.draw.circle(screen, limb_colors['head'], (center_x, center_y - 50), 20)  # Head
        pygame.draw.line(screen, limb_colors['left_arm'], (center_x, center_y - 30), (center_x - 30, center_y), 5)  # Left arm
        pygame.draw.line(screen, limb_colors['right_arm'], (center_x, center_y - 30), (center_x + 30, center_y), 5)  # Right arm
        pygame.draw.line(screen, limb_colors['left_leg'], (center_x, center_y + 30), (center_x - 20, center_y + 60), 5)  # Left leg
        pygame.draw.line(screen, limb_colors['right_leg'], (center_x, center_y + 30), (center_x + 20, center_y + 60), 5)  # Right leg

    def _render_inventory(self, screen):
        # Default empty inventory if none exists
        inventory = getattr(self.player, 'inventory', [])
        slot_size = 50
        margin = 10
        start_x = screen.get_width() - 300
        start_y = 50

        for i, item in enumerate(inventory):
            x = start_x + (i % 4) * (slot_size + margin)
            y = start_y + (i // 4) * (slot_size + margin)
            pygame.draw.rect(screen, (100, 100, 100), (x, y, slot_size, slot_size))
            if item:
                text = self.font.render(item[:3], True, (255, 255, 255))
                screen.blit(text, (x + 10, y + 10))

    def _render_crafting(self, screen):
        # Hardcoded recipes for now
        recipes = [
            "Stick + Stone = Tool",
            "Cloth + Stick = Bandage"
        ]
        start_x = 50
        start_y = 200

        for i, recipe in enumerate(recipes):
            text = self.font.render(recipe, True, (255, 255, 255))
            screen.blit(text, (start_x, start_y + i * 30)) 