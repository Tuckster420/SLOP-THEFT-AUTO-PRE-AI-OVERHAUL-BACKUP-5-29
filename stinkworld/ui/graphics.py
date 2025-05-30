"""Graphics module for rendering game elements."""
import pygame
import os
import random
from stinkworld.utils.debug import debug_log

# Constants for viewport and tile size
VIEWPORT_WIDTH = 800  # Adjust as needed
VIEWPORT_HEIGHT = 600  # Adjust as needed
TILE_SIZE = 32  # Standard tile size

class Graphics:
    """Handles rendering of game elements."""
    
    def __init__(self, game=None):
        """Initialize graphics system."""
        self.game = game  # Reference to the Game instance
        self.terrain_colors = {
            'road_h': (90, 90, 90),
            'road_v': (90, 90, 90),
            'road_intersection': (80, 80, 80),
            'grass': (34, 139, 34),
            'building': (180, 180, 180),
            'floor': (220, 210, 180),  # Added floor color
            'tree': (20, 100, 20),
            'water': (80, 180, 255),
        }
        
        self.furniture_colors = {
            'toilet': (200, 200, 255),
            'oven': (150, 150, 150),
            'bed': (180, 120, 255),
            'desk': (160, 82, 45),
            'shop_shelf': (255, 255, 153),
            'table': (222, 184, 135),
            'fridge': (200, 255, 255),
            'counter': (210, 180, 140),
            'sink': (180, 220, 255),
            'tub': (180, 200, 255)
        }
        
        self.car_colors = {
            'sedan': (255, 0, 0),
            'truck': (0, 0, 255),
            'van': (0, 255, 0)
        }
        
        # Initialize sprite sheets and graphics
        self.sprites = {}
        self.load_sprites()
        
        # Load Roguelike wall spritesheet
        self.roguelike_tiles = self.load_spritesheet('The Roguelike 1-15-1.png', 32)
        
    def load_sprites(self):
        """Load all game sprites, using PNGs from sprites/ if available."""
        sprite_dir = os.path.join(os.getcwd(), "sprites")
        # Terrain
        self.terrain_sprites = {}
        for key in ['road_h', 'road_v', 'road_intersection', 'grass', 'sidewalk', 'building', 'floor', 'tree', 'water']:
            sprite_path = os.path.join(sprite_dir, f"{key}.png")
            if os.path.exists(sprite_path):
                self.terrain_sprites[key] = pygame.image.load(sprite_path).convert_alpha()
            else:
                # Fallback to procedural
                if key == 'road_h':
                    self.terrain_sprites[key] = self.create_road_sprite('horizontal')
                elif key == 'road_v':
                    self.terrain_sprites[key] = self.create_road_sprite('vertical')
                elif key == 'road_intersection':
                    self.terrain_sprites[key] = self.create_road_sprite('intersection')
                elif key == 'grass':
                    self.terrain_sprites[key] = self.create_grass_sprite()
                elif key == 'sidewalk':
                    self.terrain_sprites[key] = self.create_sidewalk_sprite()
                elif key == 'building':
                    self.terrain_sprites[key] = self.create_building_sprite()
                elif key == 'floor':
                    # Simple tan/beige fill for floor
                    surface = pygame.Surface((32, 32))
                    surface.fill((220, 210, 180))
                    self.terrain_sprites[key] = surface
                elif key == 'tree':
                    self.terrain_sprites[key] = self.create_tree_sprite()
                elif key == 'water':
                    self.terrain_sprites[key] = self.create_water_sprite()
        # Furniture
        self.furniture_sprites = {}
        for key in ['bed', 'toilet', 'sink', 'desk', 'table', 'fridge', 'oven', 'counter', 'shop_shelf']:
            sprite_path = os.path.join(sprite_dir, f"{key}.png")
            if os.path.exists(sprite_path):
                self.furniture_sprites[key] = pygame.image.load(sprite_path).convert_alpha()
            else:
                create_method = getattr(self, f"create_{key}_sprite", None)
                if create_method:
                    self.furniture_sprites[key] = create_method()
        # Vehicles
        self.vehicle_sprites = {}
        for key in ['sedan', 'sports_car', 'suv', 'truck']:
            sprite_path = os.path.join(sprite_dir, f"{key}.png")
            if os.path.exists(sprite_path):
                self.vehicle_sprites[key] = pygame.image.load(sprite_path).convert_alpha()
            else:
                self.vehicle_sprites[key] = self.create_car_sprite(key)

    def create_bed_sprite(self):
        """Create a bed sprite."""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 255, 255))  # White background
        
        # Draw bed frame (brown)
        pygame.draw.rect(surface, (139, 69, 19), (2, 2, 28, 28))
        
        # Draw mattress (light gray)
        pygame.draw.rect(surface, (200, 200, 200), (4, 4, 24, 24))
        
        # Draw pillow (white)
        pygame.draw.ellipse(surface, (255, 255, 255), (6, 6, 12, 8))
        
        # Draw blanket (blue)
        pygame.draw.rect(surface, (70, 130, 180), (4, 16, 24, 12))
        
        return surface

    def create_toilet_sprite(self):
        """Create a toilet sprite."""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 255, 255))
        
        # Draw base (white)
        pygame.draw.rect(surface, (240, 240, 240), (8, 16, 16, 14))
        
        # Draw bowl (white)
        pygame.draw.ellipse(surface, (250, 250, 250), (6, 6, 20, 16))
        
        # Draw seat (light gray)
        pygame.draw.arc(surface, (200, 200, 200), (6, 4, 20, 16), 0, 3.14, 2)
        
        return surface

    def create_sink_sprite(self):
        """Create a sink sprite."""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 255, 255))
        
        # Draw basin (white)
        pygame.draw.ellipse(surface, (240, 240, 240), (4, 8, 24, 16))
        
        # Draw faucet (silver)
        pygame.draw.rect(surface, (192, 192, 192), (14, 4, 4, 8))
        pygame.draw.rect(surface, (192, 192, 192), (10, 4, 12, 2))
        
        return surface

    def create_desk_sprite(self):
        """Create a desk sprite."""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 255, 255))
        
        # Draw desktop (brown)
        pygame.draw.rect(surface, (139, 69, 19), (2, 8, 28, 4))
        
        # Draw legs
        pygame.draw.rect(surface, (120, 60, 15), (4, 12, 4, 18))
        pygame.draw.rect(surface, (120, 60, 15), (24, 12, 4, 18))
        
        return surface

    def create_car_sprite(self, car_type):
        """Create a car sprite based on type."""
        surface = pygame.Surface((64, 32))  # Cars are 2 tiles wide
        surface.fill((255, 255, 255))
        surface.set_colorkey((255, 255, 255))  # Make white transparent
        
        if car_type == 'sedan':
            # Body (blue)
            pygame.draw.rect(surface, (0, 0, 200), (4, 8, 56, 16))
            # Windows
            pygame.draw.rect(surface, (200, 200, 255), (12, 4, 16, 8))
            pygame.draw.rect(surface, (200, 200, 255), (36, 4, 16, 8))
            # Wheels
            pygame.draw.circle(surface, (40, 40, 40), (16, 24), 6)
            pygame.draw.circle(surface, (40, 40, 40), (48, 24), 6)
            
        elif car_type == 'sports_car':
            # Sleek body (red)
            pygame.draw.polygon(surface, (200, 0, 0), [
                (4, 16), (60, 16),  # Bottom
                (56, 8), (32, 4), (8, 8)  # Top
            ])
            # Windows
            pygame.draw.polygon(surface, (200, 200, 255), [
                (16, 8), (48, 8),
                (44, 6), (20, 6)
            ])
            # Wheels
            pygame.draw.circle(surface, (40, 40, 40), (16, 16), 6)
            pygame.draw.circle(surface, (40, 40, 40), (48, 16), 6)
            
        elif car_type == 'suv':
            # Body (black)
            pygame.draw.rect(surface, (40, 40, 40), (4, 4, 56, 20))
            # Windows
            pygame.draw.rect(surface, (200, 200, 255), (8, 8, 12, 8))
            pygame.draw.rect(surface, (200, 200, 255), (24, 8, 12, 8))
            pygame.draw.rect(surface, (200, 200, 255), (40, 8, 12, 8))
            # Wheels
            pygame.draw.circle(surface, (40, 40, 40), (16, 24), 8)
            pygame.draw.circle(surface, (40, 40, 40), (48, 24), 8)
            
        elif car_type == 'truck':
            # Cabin (gray)
            pygame.draw.rect(surface, (80, 80, 80), (4, 8, 20, 16))
            # Cargo area
            pygame.draw.rect(surface, (100, 100, 100), (24, 4, 36, 20))
            # Windows
            pygame.draw.rect(surface, (200, 200, 255), (8, 4, 12, 8))
            # Wheels
            pygame.draw.circle(surface, (40, 40, 40), (12, 24), 8)
            pygame.draw.circle(surface, (40, 40, 40), (44, 24), 8)
        
        return surface

    def create_road_sprite(self, orientation='horizontal'):
        """Create a road sprite with lane markings based on orientation."""
        surface = pygame.Surface((32, 32))
        
        # Dark gray base
        surface.fill((50, 50, 50))
        
        # Add lane marking based on orientation
        if orientation == 'horizontal':
            # Yellow line in middle for horizontal roads
            pygame.draw.rect(surface, (255, 255, 0), (0, 14, 32, 4))
        elif orientation == 'vertical':
            # Yellow line in middle for vertical roads
            pygame.draw.rect(surface, (255, 255, 0), (14, 0, 4, 32))
        elif orientation == 'intersection':
            # Cross pattern for intersections
            pygame.draw.rect(surface, (255, 255, 0), (0, 14, 32, 4))
            pygame.draw.rect(surface, (255, 255, 0), (14, 0, 4, 32))
        
        return surface

    def create_grass_sprite(self):
        """Create a grass sprite with texture."""
        surface = pygame.Surface((32, 32))
        surface.fill((34, 139, 34))  # Base green
        
        # Add grass detail
        for _ in range(10):
            x = random.randint(0, 31)
            y = random.randint(0, 31)
            pygame.draw.line(surface, (50, 160, 50), 
                           (x, y), (x, y-4), 1)
        
        return surface

    def create_building_sprite(self):
        """Create a building sprite."""
        surface = pygame.Surface((32, 32))
        surface.fill((180, 180, 180))  # Gray base
        
        # Add windows
        for i in range(2):
            for j in range(2):
                pygame.draw.rect(surface, (200, 200, 255),
                               (8 + i*16, 8 + j*16, 8, 8))
        
        return surface

    def create_tree_sprite(self):
        """Create a tree sprite."""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 255, 255))
        surface.set_colorkey((255, 255, 255))
        
        # Draw trunk
        pygame.draw.rect(surface, (139, 69, 19), (14, 16, 4, 16))
        
        # Draw leaves
        pygame.draw.circle(surface, (0, 100, 0), (16, 12), 12)
        pygame.draw.circle(surface, (0, 120, 0), (12, 8), 8)
        pygame.draw.circle(surface, (0, 140, 0), (20, 8), 8)
        
        return surface

    def create_water_sprite(self):
        """Create an animated water sprite."""
        surface = pygame.Surface((32, 32))
        surface.fill((0, 0, 139))  # Dark blue
        
        # Add wave effect
        for i in range(4):
            y = 8 * i
            pygame.draw.arc(surface, (0, 0, 200), 
                          (0, y, 32, 8), 0, 3.14, 2)
        
        return surface

    def generate_default_sprites(self):
        """Generate and save default sprites if none exist."""
        # This would create and save basic sprite images
        # For now, we'll use the runtime-generated ones
        pass

    def draw_sprite(self, screen, sprite, x, y):
        """Helper method to draw a sprite at the given position."""
        if isinstance(sprite, pygame.Surface):
            screen.blit(sprite, (x, y))
        else:
            print(f"Warning: Invalid sprite type {type(sprite)}")

    def load_spritesheet(self, filename, tile_size=32):
        """Load a spritesheet and return a list of tile surfaces."""
        path = os.path.join(os.getcwd(), "sprites", filename)
        if not os.path.exists(path):
            debug_log(f"[Graphics] Spritesheet not found: {path}")
            return []
        sheet = pygame.image.load(path).convert_alpha()
        sheet_width, sheet_height = sheet.get_width(), sheet.get_height()
        tiles = []
        for y in range(0, sheet_height, tile_size):
            for x in range(0, sheet_width, tile_size):
                tile = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                tile.blit(sheet, (0, 0), (x, y, tile_size, tile_size))
                tiles.append(tile)
        return tiles

    def get_ground_tile(self, tile_type):
        """Return the correct ground tile surface for a given type."""
        mapping = {
            'grass': 0,  # tile index for grass (from topdown sheet)
            'dirt': 1,   # tile index for dirt (from topdown sheet)
            'building': 0,  # wall tile index from roguelike sheet (adjust as needed)
            'floor': 1,     # floor tile index from roguelike sheet (adjust as needed)
        }
        from stinkworld.utils.debug import debug_log
        if tile_type == 'building':
            if hasattr(self, 'roguelike_tiles') and self.roguelike_tiles:
                idx = mapping['building']
                debug_log(f"[GRAPHICS] Using roguelike wall tile index {idx} for 'building'")
                if idx < len(self.roguelike_tiles):
                    return self.roguelike_tiles[idx]
                else:
                    debug_log(f"[GRAPHICS] Roguelike wall tile index {idx} out of range!")
            else:
                debug_log("[GRAPHICS] Roguelike spritesheet missing for 'building'!")
        if tile_type == 'floor':
            if hasattr(self, 'roguelike_tiles') and self.roguelike_tiles:
                idx = mapping['floor']
                debug_log(f"[GRAPHICS] Using roguelike floor tile index {idx} for 'floor'")
                if idx < len(self.roguelike_tiles):
                    return self.roguelike_tiles[idx]
                else:
                    debug_log(f"[GRAPHICS] Roguelike floor tile index {idx} out of range!")
            else:
                debug_log("[GRAPHICS] Roguelike spritesheet missing for 'floor'! Using fallback color.")
        if tile_type not in mapping:
            return None
        if not hasattr(self, 'ground_tiles'):
            self.ground_tiles = self.load_spritesheet('32x32 topdown tileset Spreadsheet V1-1.png', 32)
        idx = mapping[tile_type]
        if self.ground_tiles and idx < len(self.ground_tiles):
            debug_log(f"[GRAPHICS] Using topdown sheet tile index {idx} for '{tile_type}'")
            return self.ground_tiles[idx]
        debug_log(f"[GRAPHICS] No sprite found for '{tile_type}', using fallback color.")
        return None

    def draw_terrain(self, screen, terrain_type, x, y):
        """Draw terrain tile at given screen coordinates."""
        if terrain_type == 'door':
            # Get door state from game
            state = self.game.furniture_state.get((x//32, y//32), {}).get('state', 'closed')
            
            # Draw door with state (open/closed)
            door_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
            
            # Brown door frame
            door_surface.fill((80, 60, 40))
            
            # Draw door panel based on state
            if state == 'open':
                pygame.draw.rect(door_surface, (120, 80, 60), 
                                (8, 4, 32-16, 32-8))  # Open door
            else:
                pygame.draw.rect(door_surface, (100, 70, 50), 
                                (32-12, 4, 12, 32-8))  # Closed door
                pygame.draw.circle(door_surface, (200, 200, 200), 
                                 (32-6, 32//2), 2)  # Door handle
            
            screen.blit(door_surface, (x, y))
            return
        elif terrain_type == 'window':
            # Draw window with state (normal/broken)
            window_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
            window_surface.fill((80, 80, 100))  # Window frame
            
            state = self.game.furniture_state.get((x//32, y//32), {}).get('state', 'normal')
            if state == 'broken':
                # Broken window effect
                pygame.draw.rect(window_surface, (200, 220, 255, 100), (4, 4, 24, 24))  # Glass
                for _ in range(8):  # Crack lines
                    start = (random.randint(4, 12), random.randint(4, 12))
                    end = (random.randint(20, 28), random.randint(20, 28))
                    pygame.draw.line(window_surface, (0, 0, 0), start, end, 1)
            else:
                # Normal window
                pygame.draw.rect(window_surface, (200, 220, 255, 150), (4, 4, 24, 24))  # Glass
                # Window crossbars
                pygame.draw.line(window_surface, (80, 80, 100), (4, 16), (28, 16), 2)
                pygame.draw.line(window_surface, (80, 80, 100), (16, 4), (16, 28), 2)
            
            screen.blit(window_surface, (x, y))
        else:
            # First try to use loaded sprites
            sprite = None
            if hasattr(self, 'terrain_sprites') and terrain_type in self.terrain_sprites:
                sprite = self.terrain_sprites[terrain_type]
            
            if sprite:
                screen.blit(sprite, (x, y))
                return
            
            # Fallback to procedural rendering with consistent colors
            if terrain_type == 'grass':
                pygame.draw.rect(screen, (34, 139, 34), (x, y, 32, 32))
                # Add grass detail
                for _ in range(10):
                    px = x + random.randint(0, 31)
                    py = y + random.randint(0, 31)
                    pygame.draw.line(screen, (50, 160, 50), 
                                   (px, py), (px, py-4), 1)
            elif terrain_type in ['road_h', 'road_v', 'road_intersection']:
                # Dark gray base
                pygame.draw.rect(screen, (50, 50, 50), (x, y, 32, 32))
                # Add lane markings
                if terrain_type == 'road_h':
                    pygame.draw.rect(screen, (255, 255, 0), (x, y+14, 32, 4))
                elif terrain_type == 'road_v':
                    pygame.draw.rect(screen, (255, 255, 0), (x+14, y, 4, 32))
                elif terrain_type == 'road_intersection':
                    pygame.draw.rect(screen, (255, 255, 0), (x, y+14, 32, 4))
                    pygame.draw.rect(screen, (255, 255, 0), (x+14, y, 4, 32))
            elif terrain_type == 'building':
                pygame.draw.rect(screen, (120, 120, 120), (x, y, 32, 32))
            elif terrain_type == 'floor':
                pygame.draw.rect(screen, (220, 210, 180), (x, y, 32, 32))
            elif terrain_type == 'water':
                pygame.draw.rect(screen, (80, 180, 255), (x, y, 32, 32))

    def draw_furniture(self, surface, furniture_type, x, y, state='normal', size=32):
        sprite = self.furniture_sprites.get(furniture_type)
        if sprite:
            surface.blit(pygame.transform.scale(sprite, (size, size)), (x, y))
        else:
            base_color = self.furniture_colors.get(furniture_type, (200, 200, 200))
            if state == 'broken':
                color = tuple(max(0, c - 100) for c in base_color)
                pygame.draw.rect(surface, color, (x, y, size, size))
                pygame.draw.line(surface, (0, 0, 0), (x, y), (x + size, y + size))
                pygame.draw.line(surface, (0, 0, 0), (x + size, y), (x, y + size))
            elif state == 'vandalized':
                pygame.draw.rect(surface, base_color, (x, y, size, size))
                pygame.draw.line(surface, (255, 0, 0), (x + 5, y + 5), (x + size - 5, y + size - 5), 2)
                pygame.draw.circle(surface, (0, 0, 255), (x + size//2, y + size//2), size//4)
            elif state == 'moved':
                pygame.draw.rect(surface, base_color, (x, y, size, size))
                overlay = pygame.Surface((size, size), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 128))
                surface.blit(overlay, (x, y))
            else:
                pygame.draw.rect(surface, base_color, (x, y, size, size))

    def draw_car(self, surface, car_type, x, y, direction='horizontal', damaged=False, size=32):
        sprite = self.vehicle_sprites.get(car_type)
        if sprite:
            if direction == 'horizontal':
                blit_sprite = pygame.transform.scale(sprite, (size*2, size))
                # Flip horizontally if moving left
                if hasattr(self, 'car_direction') and self.car_direction == 'left':
                    blit_sprite = pygame.transform.flip(blit_sprite, True, False)
            else:
                blit_sprite = pygame.transform.rotate(pygame.transform.scale(sprite, (size*2, size)), 90)
                # Flip vertically if moving up
                if hasattr(self, 'car_direction') and self.car_direction == 'up':
                    blit_sprite = pygame.transform.flip(blit_sprite, False, True)
            surface.blit(blit_sprite, (x, y))
        else:
            color = self.car_colors.get(car_type, (255, 0, 0))
            if damaged:
                color = tuple(max(0, c - 100) for c in color)
            if direction == 'horizontal':
                pygame.draw.rect(surface, color, (x, y, size * 2, size))
                window_color = (200, 200, 255)
                pygame.draw.rect(surface, window_color, (x + size//2, y + 5, size, size - 10))
            else:
                pygame.draw.rect(surface, color, (x, y, size, size * 2))
                window_color = (200, 200, 255)
                pygame.draw.rect(surface, window_color, (x + 5, y + size//2, size - 10, size))

    def create_table_sprite(self):
        """Create a table sprite."""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 255, 255))
        
        # Draw table top (wood)
        pygame.draw.rect(surface, (139, 69, 19), (2, 8, 28, 4))
        
        # Draw legs
        pygame.draw.rect(surface, (120, 60, 15), (4, 12, 4, 18))
        pygame.draw.rect(surface, (120, 60, 15), (24, 12, 4, 18))
        
        return surface

    def create_fridge_sprite(self):
        """Create a fridge sprite."""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 255, 255))
        
        # Draw fridge body (white)
        pygame.draw.rect(surface, (240, 240, 240), (4, 2, 24, 28))
        
        # Draw handle
        pygame.draw.rect(surface, (192, 192, 192), (24, 8, 2, 16))
        
        # Draw divider between freezer and fridge
        pygame.draw.line(surface, (192, 192, 192), (4, 12), (28, 12), 1)
        
        return surface

    def create_oven_sprite(self):
        """Create an oven sprite."""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 255, 255))
        
        # Draw oven body (white/silver)
        pygame.draw.rect(surface, (220, 220, 220), (4, 2, 24, 28))
        
        # Draw door
        pygame.draw.rect(surface, (180, 180, 180), (6, 8, 20, 20))
        pygame.draw.rect(surface, (160, 160, 160), (22, 16, 2, 4))  # Handle
        
        # Draw burners
        for i in range(2):
            for j in range(2):
                pygame.draw.circle(surface, (40, 40, 40), 
                                 (10 + i*12, 6), 3)
        
        return surface

    def create_counter_sprite(self):
        """Create a counter sprite."""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 255, 255))
        
        # Draw counter top
        pygame.draw.rect(surface, (210, 180, 140), (2, 8, 28, 4))
        
        # Draw base
        pygame.draw.rect(surface, (180, 150, 110), (4, 12, 24, 18))
        
        # Draw handle
        pygame.draw.rect(surface, (120, 120, 120), (12, 20, 8, 2))
        
        return surface

    def create_shop_shelf_sprite(self):
        """Create a shop shelf sprite."""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 255, 255))
        
        # Draw main shelf structure
        pygame.draw.rect(surface, (139, 69, 19), (2, 2, 28, 28))
        
        # Draw shelves
        for i in range(4):
            pygame.draw.rect(surface, (160, 82, 45), 
                           (4, 6 + i*7, 24, 2))
            
        # Draw items on shelves (simplified)
        for i in range(3):
            for j in range(4):
                pygame.draw.rect(surface, (random.randint(50, 200),
                                         random.randint(50, 200),
                                         random.randint(50, 200)),
                               (6 + i*8, 8 + j*7, 4, 4))
        
        return surface

    def create_sidewalk_sprite(self):
        """Create a sidewalk sprite."""
        surface = pygame.Surface((32, 32))
        surface.fill((200, 200, 200))  # Light gray base
        
        # Add texture
        for i in range(4):
            for j in range(4):
                if (i + j) % 2 == 0:
                    pygame.draw.rect(surface, (180, 180, 180),
                                   (i*8, j*8, 8, 8))
        
        return surface

    def load_natural_props(self):
        """Load all natural prop sprites from The Natural v1-4/Props."""
        props_dir = os.path.join(os.getcwd(), "sprites", "The Natural v1-4", "Props")
        self.natural_props = {}
        if os.path.exists(props_dir):
            for fname in os.listdir(props_dir):
                if fname.endswith('.png'):
                    key = fname[:-4].lower().replace(' ', '_')  # e.g., 'Bush 01.png' -> 'bush_01'
                    self.natural_props[key] = pygame.image.load(os.path.join(props_dir, fname)).convert_alpha()

    def get_natural_prop(self, name):
        """Get a natural prop sprite by name (case-insensitive, spaces/underscores ignored)."""
        if not hasattr(self, 'natural_props'):
            self.load_natural_props()
        key = name.lower().replace(' ', '_')
        return self.natural_props.get(key)

    def draw_natural_prop(self, surface, name, x, y, size=32):
        sprite = self.get_natural_prop(name)
        if sprite:
            surface.blit(pygame.transform.scale(sprite, (size, size)), (x, y))
        else:
            # fallback: draw a magenta box for missing sprite
            pygame.draw.rect(surface, (255, 0, 255), (x, y, size, size))

    def redraw_tile(self, x, y):
        """Force redraw of a specific tile."""
        # Convert tile coordinates to screen coordinates
        screen_x = (x - self.game.player.x + VIEWPORT_WIDTH // 2) * TILE_SIZE
        screen_y = (y - self.game.player.y + VIEWPORT_HEIGHT // 2) * TILE_SIZE
        
        # Get tile type and redraw
        tile = self.game.city.get_tile(x, y)
        if tile == 'door':
            self.draw_terrain(self.screen, 'door', screen_x, screen_y)
        pygame.display.update(pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE))