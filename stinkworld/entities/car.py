"""Car entity module."""
import random
from stinkworld.utils.debug import debug_log

class Car:
    """Car entity that can be driven by players or NPCs."""
    
    def __init__(self, x, y, direction='horizontal'):
        """Initialize car."""
        self.x = x
        self.y = y
        self.direction = direction  # 'horizontal' or 'vertical'
        self.type = random.choice(['sedan', 'truck', 'van'])
        self.hp = 100
        self.max_hp = 100
        self.speed = 2
        self.driver = None
        self.hijacked = False
    
    def get_tiles(self):
        """Get all tiles occupied by the car."""
        if self.direction == 'horizontal':
            return [(self.x, self.y), (self.x + 1, self.y)]
        else:
            return [(self.x, self.y), (self.x, self.y + 1)]
    
    def handle_player_input(self, dx, dy, city_map, cars, npcs):
        """Handle player input for car movement."""
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check if we need to change direction
        if dx != 0 and self.direction == 'vertical':
            self.direction = 'horizontal'
        elif dy != 0 and self.direction == 'horizontal':
            self.direction = 'vertical'
        
        # Get new tiles that would be occupied
        new_tiles = []
        if self.direction == 'horizontal':
            new_tiles = [(new_x, new_y), (new_x + 1, new_y)]
        else:
            new_tiles = [(new_x, new_y), (new_x, new_y + 1)]
        
        # Check for collisions with other cars
        for car in cars:
            if car != self:
                if any(tile in car.get_tiles() for tile in new_tiles):
                    return False
        
        # Check for collisions with NPCs
        for npc in npcs:
            if (npc.x, npc.y) in new_tiles:
                if not npc.is_dead:
                    damage = random.randint(50, 100)
                    npc.hp = max(0, npc.hp - damage)
                    if npc.hp <= 0:
                        npc.is_dead = True
                    return f"You hit {npc.name} with the car! They take {damage} damage!"
                return False
        
        # Check if new position is on road
        for tile_x, tile_y in new_tiles:
            if not self.is_valid_position(tile_x, tile_y, city_map):
                return False
        
        # Move car
        self.x = new_x
        self.y = new_y
        return True
    
    def is_valid_position(self, x, y, city_map):
        """Check if position is valid for car."""
        if 0 <= x < len(city_map[0]) and 0 <= y < len(city_map):
            return city_map[y][x] == 0  # Assuming 0 is road tile
        return False
    
    def update(self, cars, city_map, traffic_lights, npcs, player_x, player_y):
        """Update AI-controlled car."""
        if self.driver or self.hp <= 0:
            return
        
        # Simple AI: Move randomly on roads
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            if self.handle_player_input(dx, dy, city_map, cars, npcs):
                break