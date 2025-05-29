"""Player entity module."""
import pygame
import random
from stinkworld.core.settings import (
    TILE_SIZE, COLOR_PLAYER, PLAYER_SPEED, PLAYER_MAX_HP, PLAYER_MAX_ENERGY,
    PLAYER_MAX_HUNGER, PLAYER_MAX_THIRST, PLAYER_MAX_STRESS,
    COLOR_WHITE
)
from stinkworld.ui.appearance import SKIN_TONES, draw_portrait
from stinkworld.utils.debug import debug_log

class Player:
    """Player character class."""
    
    def __init__(self, settings):
        """Initialize player."""
        self.name = ""
        self.x = 0
        self.y = 0
        
        # Stats
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.energy = PLAYER_MAX_ENERGY
        self.max_energy = PLAYER_MAX_ENERGY
        self.hunger = 0
        self.max_hunger = PLAYER_MAX_HUNGER
        self.thirst = 0
        self.max_thirst = PLAYER_MAX_THIRST
        self.stress = 0
        self.max_stress = PLAYER_MAX_STRESS
        
        # Attributes
        self.strength = 5
        self.agility = 5
        self.intelligence = 5
        self.charisma = 5
        self.reputation = 0
        self.book_smarts = 0
        self.street_smarts = 0  # Add this line
        
        # Inventory and equipment
        self.money = 1000
        self.inventory = []
        self.equipped = {
            'weapon': None,
            'armor': None,
            'accessory': None
        }
        
        # State
        self.speed = PLAYER_SPEED
        self.direction = 'right'
        self.is_moving = False
        self.in_car = None
        self.is_knocked_out = False
        self.is_dead = False
        
        # Skills and abilities
        self.skills = {
            'driving': 1,
            'fighting': 1,
            'stealth': 1,
            'persuasion': 1,
            'hacking': 1
        }
        
        self.max_hp = 100
        self.max_energy = 100
        self.max_hunger = 100
        self.max_thirst = 100
        self.max_stress = 100
        self.points = 0
        self.journal = []
        self.skin_tone = SKIN_TONES['medium']  # Use proper skin tone from appearance
        
        # Economy attributes
        self.current_job = None
        self.job_experience = {}  # Track experience in different jobs
        self.appearance = {
            'skin_tone': self.skin_tone,
            'face_shape': 'round',
            'eye_type': 'bright',
            'hair_style': 'short',
            'hair_color': 'brown',
            'clothes': 'casual',
            'vitiligo': 0.0,
            'vitiligo_patches': []
        }
        self.ko_timer = 0
        self.personality = None

    def handle_event(self, event):
        """Handle player input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.moving_left = True
            elif event.key == pygame.K_d:
                self.moving_right = True
            elif event.key == pygame.K_w:
                self.moving_up = True
            elif event.key == pygame.K_s:
                self.moving_down = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.moving_left = False
            elif event.key == pygame.K_d:
                self.moving_right = False
            elif event.key == pygame.K_w:
                self.moving_up = False
            elif event.key == pygame.K_s:
                self.moving_down = False
    
    def update(self):
        """Update player state."""
        if self.is_dead:
            return
            
        # Update needs
        self.hunger = min(self.hunger + 0.01, self.max_hunger)
        self.thirst = min(self.thirst + 0.02, self.max_thirst)
        self.energy = max(0, self.energy - 0.01)
        
        # Effects of needs
        if self.hunger >= self.max_hunger * 0.8:
            self.energy = max(0, self.energy - 0.02)
        if self.thirst >= self.max_thirst * 0.8:
            self.energy = max(0, self.energy - 0.03)
        if self.energy <= self.max_energy * 0.2:
            self.stress = min(self.stress + 0.02, self.max_stress)
        
        # Recovery from knockout
        if self.is_knocked_out:
            if random.random() < 0.01:  # 1% chance per update to wake up
                self.is_knocked_out = False
    
    def render(self, screen):
        """Render player on screen."""
        # For now, just draw a rectangle
        pygame.draw.rect(screen, (255, 0, 0), (self.x - 16, self.y - 16, 32, 32))
    
    def take_damage(self, amount):
        """Take damage and update health."""
        self.hp = max(0, self.hp - amount)
        return self.hp <= 0
    
    def heal(self, amount):
        """Heal player."""
        self.hp = min(self.max_hp, self.hp + amount)

    def move(self, dx, dy, city_map, npcs, cars):
        """Handle player movement."""
        if self.is_knocked_out or self.is_dead:
            return False
            
        if self.in_car:
            return self.in_car.handle_player_input(dx, dy, city_map, cars, npcs)
            
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Update direction
        if dx > 0:
            self.direction = 'right'
        elif dx < 0:
            self.direction = 'left'
        elif dy > 0:
            self.direction = 'down'
        elif dy < 0:
            self.direction = 'up'
        
        # Check for collisions with NPCs
        for npc in npcs:
            if npc.x == new_x and npc.y == new_y and not npc.is_dead:
                return False
        
        # Check for collisions with cars
        for car in cars:
            if (new_x, new_y) in car.get_tiles():
                return False
        
        # Check if new position is walkable
        if self.is_valid_position(new_x, new_y, city_map):
            self.x = new_x
            self.y = new_y
            self.is_moving = True
            return True
            
        return False
    
    def is_valid_position(self, x, y, city_map):
        """Check if position is valid for player."""
        if 0 <= x < len(city_map[0]) and 0 <= y < len(city_map):
            tile = city_map[y][x]
            return tile in [0, 1, 2, 3, 4, 5]  # Now includes TILE_FLOOR (5)
        return False

    def draw(self, screen, camera_x, camera_y):
        """Draw player on screen."""
        screen_x = (self.x - camera_x) * TILE_SIZE
        screen_y = (self.y - camera_y) * TILE_SIZE
        
        if self.is_knocked_out:
            color = (128, 128, 128)  # Gray when knocked out
        elif self.hp < self.max_hp * 0.3:
            color = (255, 0, 0)  # Red when low health
        else:
            color = COLOR_WHITE
        
        pygame.draw.rect(screen, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
        
        # Draw direction indicator
        indicator_color = (0, 255, 0)
        if self.direction == 'right':
            pygame.draw.line(screen, indicator_color,
                           (screen_x + TILE_SIZE - 4, screen_y + TILE_SIZE//2),
                           (screen_x + TILE_SIZE, screen_y + TILE_SIZE//2), 3)
        elif self.direction == 'left':
            pygame.draw.line(screen, indicator_color,
                           (screen_x, screen_y + TILE_SIZE//2),
                           (screen_x + 4, screen_y + TILE_SIZE//2), 3)
        elif self.direction == 'down':
            pygame.draw.line(screen, indicator_color,
                           (screen_x + TILE_SIZE//2, screen_y + TILE_SIZE - 4),
                           (screen_x + TILE_SIZE//2, screen_y + TILE_SIZE), 3)
        else:  # up
            pygame.draw.line(screen, indicator_color,
                           (screen_x + TILE_SIZE//2, screen_y),
                           (screen_x + TILE_SIZE//2, screen_y + 4), 3)
        
        # Draw player portrait
        portrait_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        portrait_surface.fill((0, 0, 0))
        draw_portrait(portrait_surface, 0, 0, TILE_SIZE, self.appearance)
        
        # Draw player on screen
        screen.blit(portrait_surface, (screen_x, screen_y))
        
        # Draw injury indicators if any
        if hasattr(self, 'injuries') and self.injuries:
            font = pygame.font.SysFont(None, 18)
            text = font.render("+", True, (255, 0, 0))
            screen.blit(text, (screen_x + 2, screen_y + 2))

    def equip_item(self, item_name, item_info):
        """Equip an item and apply its effects."""
        if item_name not in self.inventory:
            return False, "You don't have this item."
        
        category = item_info['category']
        if category == 'clothing':
            # Determine slot based on item name
            if 'Shirt' in item_name:
                slot = 'shirt'
            elif 'Pants' in item_name:
                slot = 'pants'
            elif 'Jacket' in item_name:
                slot = 'jacket'
            elif 'Shoes' in item_name:
                slot = 'shoes'
            else:
                return False, "Unknown clothing type."
            
            # Unequip current item if any
            if self.equipped[slot]:
                self.inventory.append(self.equipped[slot])
            
            # Equip new item
            self.equipped[slot] = item_name
            self.inventory.remove(item_name)
            return True, f"Equipped {item_name}"
            
        elif category == 'accessories':
            # Handle accessories
            if self.equipped['accessory']:
                self.inventory.append(self.equipped['accessory'])
            self.equipped['accessory'] = item_name
            self.inventory.remove(item_name)
            return True, f"Equipped {item_name}"
            
        return False, "This item cannot be equipped."

    def unequip_item(self, slot):
        """Unequip an item from a slot."""
        if not self.equipped[slot]:
            return False, "Nothing equipped in this slot."
            
        self.inventory.append(self.equipped[slot])
        self.equipped[slot] = None
        return True, f"Unequipped item from {slot}"

    def use_item(self, item_name):
        """Use an item from inventory."""
        if item_name not in self.inventory:
            return False, "You don't have this item."
            
        # Apply item effects
        if item_name == "Food":
            self.hunger = max(0, self.hunger - 30)
        elif item_name == "Water":
            self.thirst = max(0, self.thirst - 30)
        elif item_name == "Energy Drink":
            self.energy = min(self.max_energy, self.energy + 20)
        elif item_name == "First Aid Kit":
            self.hp = min(self.max_hp, self.hp + 30)
        else:
            return False, "This item cannot be used."
            
        self.inventory.remove(item_name)
        return True, f"Used {item_name}."

    def enter_car(self, car):
        """Enter a car."""
        if not car or car.driver or car.hp <= 0:
            return False
            
        self.in_car = car
        car.driver = self
        return True
    
    def exit_car(self):
        """Exit current car."""
        if not self.in_car:
            return False
            
        self.in_car.driver = None
        self.in_car = None
        return True

    def get_total_style(self):
        """Calculate total style points from equipped clothing."""
        style = 0
        for slot, item_name in self.equipped.items():
            if item_name:
                # This would need to reference the economy's items dictionary
                # style += economy.items[item_name].get('style', 0)
                style += 1  # Simplified version
        return style

    def get_speed_bonus(self):
        """Calculate speed bonus from equipped items."""
        bonus = 0
        for slot, item_name in self.equipped.items():
            if item_name:
                # This would need to reference the economy's items dictionary
                # bonus += economy.items[item_name].get('speed_bonus', 0)
                if 'Running Shoes' in item_name:
                    bonus += 1
        return bonus