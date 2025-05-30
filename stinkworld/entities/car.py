"""Car entity module."""
import random
from stinkworld.core.settings import CAR_SPEED, TILE_ROAD
from stinkworld.utils.debug import debug_log

class Car:
    """Car entity that can be driven by players or NPCs."""
    
    def __init__(self, x, y, car_type='sedan'):
        """Initialize car."""
        self.x = x
        self.y = y
        self.type = car_type
        self.speed = CAR_SPEED
        # Restore original direction logic: up/down/left/right
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.driver = None  # Can be Player or NPC
        self.hp = 100
        self.max_hp = 100
        self.destination = None
        self.path = []
        self.is_locked = False
    
    def debug(self, message):
        """Log debug messages."""
        debug_log(message)
    
    def set_driver(self, driver):
        """Set the driver of this car."""
        if self.is_locked and driver != self.driver:
            return False
            
        self.driver = driver
        if hasattr(driver, 'in_car'):
            driver.in_car = self
        return True
        
    def remove_driver(self):
        """Remove the current driver."""
        if self.driver and hasattr(self.driver, 'in_car'):
            self.driver.in_car = None
        self.driver = None
        
    def hijack(self, new_driver):
        """Attempt to hijack this car from current driver."""
        if not self.driver:
            return self.set_driver(new_driver)
            
        # NPCs may resist hijacking based on personality
        if hasattr(self.driver, 'personality') and 'aggressive' in self.driver.personality:
            if random.random() < 0.7:  # 70% chance to resist
                return False
                
        # Force out current driver
        self.remove_driver()
        return self.set_driver(new_driver)
        
    def update_ai(self, city_map, traffic_lights, npcs):
        """Update car's AI movement."""
        if self.driver or self.hp <= 0:
            return
        
        old_pos = (self.x, self.y)
        
        if not self.destination:
            road_tiles = []
            for y in range(len(city_map)):
                for x in range(len(city_map[0])):
                    if city_map[y][x] == TILE_ROAD:
                        road_tiles.append((x, y))
            if road_tiles:
                self.destination = random.choice(road_tiles)
                
        # Simple pathfinding toward destination
        if self.destination:
            dx = self.destination[0] - self.x
            dy = self.destination[1] - self.y
            
            # Prefer moving in the direction with largest difference
            if abs(dx) > abs(dy):
                step = 1 if dx > 0 else -1
                self.handle_player_input(step, 0, city_map, [], npcs)
            elif abs(dy) > 0:
                step = 1 if dy > 0 else -1
                self.handle_player_input(0, step, city_map, [], npcs)
            
            # If reached destination, clear it
            if self.x == self.destination[0] and self.y == self.destination[1]:
                self.destination = None
        
        if (self.x, self.y) != old_pos:
            debug_log(f"CAR MOVED: {self.type} from {old_pos} to ({self.x},{self.y})")
        else:
            debug_log(f"CAR STUCK: {self.type} at {old_pos}")
    
    def get_tiles(self):
        """Get all tiles occupied by the car."""
        # Restore: car occupies 2 tiles based on up/down/left/right
        if self.direction == 'left':
            return [(self.x, self.y), (self.x - 1, self.y)]
        elif self.direction == 'right':
            return [(self.x, self.y), (self.x + 1, self.y)]
        elif self.direction == 'up':
            return [(self.x, self.y), (self.x, self.y - 1)]
        elif self.direction == 'down':
            return [(self.x, self.y), (self.x, self.y + 1)]
        else:
            return [(self.x, self.y)]

    def handle_player_input(self, dx, dy, city_map, cars, npcs):
        """Handle player input for car movement."""
        # Only allow one axis of movement at a time (no diagonal driving)
        if dx != 0 and dy != 0:
            return False
        # Set direction based on input, but only if moving in that axis
        if dx == 1:
            self.direction = 'right'
        elif dx == -1:
            self.direction = 'left'
        elif dy == 1:
            self.direction = 'down'
        elif dy == -1:
            self.direction = 'up'
        else:
            # No movement
            return False
        new_x = self.x + dx
        new_y = self.y + dy
        # Get new tiles based on direction
        new_tiles = self.get_tiles_for_position(new_x, new_y, self.direction)
        # Check for collisions with other cars
        for car in cars:
            if car != self:
                if any(tile in car.get_tiles() for tile in new_tiles):
                    return False
        # Check for collisions with NPCs
        for npc in npcs:
            if (npc.x, npc.y) in new_tiles and not npc.is_dead:
                damage = random.randint(50, 100)
                npc.hp = max(0, npc.hp - damage)
                if npc.hp <= 0:
                    npc.is_dead = True
                    npc.is_knocked_out = True
                else:
                    npc.is_knocked_out = True if npc.hp < 3 else False
                return f"You hit {npc.name} with the car! They take {damage} damage!"
        # Check if new position is on road
        for tile_x, tile_y in new_tiles:
            if not self.is_valid_position(tile_x, tile_y, city_map):
                return False
        # Move car
        self.x = new_x
        self.y = new_y
        return True

    def get_tiles_for_position(self, x, y, direction):
        """Get tiles for the car's position based on direction."""
        if direction == 'left':
            return [(x, y), (x - 1, y)]
        elif direction == 'right':
            return [(x, y), (x + 1, y)]
        elif direction == 'up':
            return [(x, y), (x, y - 1)]
        elif direction == 'down':
            return [(x, y), (x, y + 1)]
        else:
            return [(x, y)]

    def is_valid_position(self, x, y, city_map):
        """Check if position is valid for car."""
        if 0 <= x < len(city_map[0]) and 0 <= y < len(city_map):
            return city_map[y][x] == TILE_ROAD
        return False