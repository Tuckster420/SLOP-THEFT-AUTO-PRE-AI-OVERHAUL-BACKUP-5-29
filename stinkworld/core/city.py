"""City generation module."""
import random
from stinkworld.core.settings import (
    MAP_WIDTH, MAP_HEIGHT, TILE_ROAD, TILE_BUILDING, TILE_PARK,
    TILE_DOOR, TILE_FLOOR, TILE_TOILET, TILE_OVEN, TILE_BED,
    TILE_DESK, TILE_SHOP_SHELF, TILE_TABLE, TILE_TREE, TILE_POND,
    TILE_GRASS, TILE_FRIDGE, TILE_COUNTER, TILE_SINK, TILE_TUB,
    TILE_COUNTRY_HOUSE, TILE_WINDOW, ROAD_SPACING, ROAD_WIDTH,
    PROP_SPAWN_RATE_GRASS, PROP_SPAWN_RATE_PARK, PROP_PROP_CANDIDATES, Settings
)
from stinkworld.utils.debug import debug_log

def place_room(grid, bx, by, bw, bh, room_type):
    furniture = []
    rx1, ry1 = bx, by
    rx2, ry2 = bx + bw - 1, by + bh - 1
    for y in range(ry1, ry2):
        for x in range(rx1, rx2):
            grid[y][x] = TILE_FLOOR
    if room_type == "bathroom":
        grid[ry1+1][rx1+1] = TILE_TOILET
        grid[ry1+1][rx1+2] = TILE_SINK
        grid[ry1+2][rx1+1] = TILE_TUB
        furniture += [(ry1+1, rx1+1, TILE_TOILET), (ry1+1, rx1+2, TILE_SINK), (ry1+2, rx1+1, TILE_TUB)]
    elif room_type == "kitchen":
        grid[ry1+1][rx1+1] = TILE_FRIDGE
        grid[ry1+1][rx1+2] = TILE_OVEN
        grid[ry1+1][rx1+3] = TILE_COUNTER
        grid[ry1+2][rx1+1] = TILE_SINK
        furniture += [(ry1+1, rx1+1, TILE_FRIDGE), (ry1+1, rx1+2, TILE_OVEN), (ry1+1, rx1+3, TILE_COUNTER), (ry1+2, rx1+1, TILE_SINK)]
    elif room_type == "bedroom":
        grid[ry1+1][rx1+1] = TILE_BED
        grid[ry1+2][rx1+1] = TILE_DESK
        furniture += [(ry1+1, rx1+1, TILE_BED), (ry1+2, rx1+1, TILE_DESK)]
    elif room_type == "living":
        grid[ry1+1][rx1+1] = TILE_TABLE
        furniture.append((ry1+1, rx1+1, TILE_TABLE))
    elif room_type == "office":
        grid[ry1+1][rx1+1] = TILE_DESK
        furniture.append((ry1+1, rx1+1, TILE_DESK))
    elif room_type == "shop":
        for i in range(rx1+1, rx2-1):
            grid[ry1+1][i] = TILE_SHOP_SHELF
            furniture.append((ry1+1, i, TILE_SHOP_SHELF))
    elif room_type == "restaurant":
        grid[ry2-2][rx1+1] = TILE_TABLE
        grid[ry2-2][rx2-2] = TILE_OVEN
        furniture += [(ry2-2, rx1+1, TILE_TABLE), (ry2-2, rx2-2, TILE_OVEN)]
    return furniture

def generate_biome(grid, bx, by, bw, bh, biome_type):
    if biome_type == "forest":
        for y in range(by, by+bh):
            for x in range(bx, bx+bw):
                grid[y][x] = TILE_GRASS
                if random.random() < 0.18:
                    grid[y][x] = TILE_TREE
                elif random.random() < 0.03:
                    grid[y][x] = TILE_POND
    elif biome_type == "countryside":
        for y in range(by, by+bh):
            for x in range(bx, bx+bw):
                grid[y][x] = TILE_GRASS
                if random.random() < 0.04:
                    grid[y][x] = TILE_TREE
                if random.random() < 0.01:
                    grid[y][x] = TILE_COUNTRY_HOUSE
    elif biome_type == "park":
        for y in range(by, by+bh):
            for x in range(bx, bx+bw):
                grid[y][x] = TILE_PARK
                if random.random() < 0.08:
                    grid[y][x] = TILE_TREE
                if random.random() < 0.01:
                    grid[y][x] = TILE_POND
    # city handled by default

def generate_city_map(width, height, road_spacing=ROAD_SPACING, road_width=ROAD_WIDTH, extra_roads=30):
    grid = [[TILE_GRASS for _ in range(width)] for _ in range(height)]
    debug_log("[CITY] Generating biomes...")
    # --- Biome regions ---
    biome_regions = []
    # City center
    biome_regions.append((width//4, height//4, width//2, height//2, "city"))
    # Forest
    biome_regions.append((0, 0, width//3, height//3, "forest"))
    biome_regions.append((width*2//3, 0, width//3, height//3, "forest"))
    # Countryside
    biome_regions.append((0, height*2//3, width//2, height//3, "countryside"))
    biome_regions.append((width//2, height*2//3, width//2, height//3, "countryside"))
    # Park
    biome_regions.append((width//3, height//8, width//3, height//6, "park"))

    for bx, by, bw, bh, btype in biome_regions:
        if btype != "city":
            generate_biome(grid, bx, by, bw, bh, btype)
    debug_log("[CITY] Biomes generated.")
    # --- City roads and buildings (city center) ---
    debug_log("[CITY] Generating roads...")
    for y in range(height//4, height*3//4, road_spacing):
        for w in range(road_width):
            if y + w < height*3//4:
                for x in range(width//4, width*3//4):
                    grid[y + w][x] = TILE_ROAD
    for x in range(width//4, width*3//4, road_spacing):
        for w in range(road_width):
            if x + w < width*3//4:
                for y in range(height//4, height*3//4):
                    grid[y][x + w] = TILE_ROAD
    debug_log("[CITY] Roads generated.")
    # --- Multi-room buildings in city center ---
    debug_log("[CITY] Generating buildings...")
    for _ in range(30):
        bx = random.randint(width//4+2, width*3//4-18)
        by = random.randint(height//4+2, height*3//4-18)
        bw = random.randint(10, 18)
        bh = random.randint(10, 18)
        # Draw building shell
        for y in range(by, by+bh):
            for x in range(bx, bx+bw):
                if x == bx or x == bx+bw-1 or y == by or y == by+bh-1:
                    grid[y][x] = TILE_BUILDING
                else:
                    grid[y][x] = TILE_FLOOR
        # Place main door
        grid[by+bh//2][bx] = TILE_DOOR

        # --- Realistic random room layout ---
        # Always include a bathroom, then randomize other rooms
        possible_rooms = ["kitchen", "bedroom", "living", "office", "closet", "storage"]
        num_rooms = random.randint(3, 5)
        rooms = ["bathroom"] + random.sample(possible_rooms, num_rooms-1)
        random.shuffle(rooms)
        # Generate room rectangles (simple grid split, but randomize sizes)
        splits_x = sorted([0] + sorted(random.sample(range(3, bw-3), num_rooms-1)) + [bw])
        splits_y = sorted([0] + sorted(random.sample(range(3, bh-3), num_rooms-1)) + [bh])
        room_rects = []
        for i in range(num_rooms):
            # Alternate between horizontal and vertical splits for variety
            if i % 2 == 0:
                x1 = bx + splits_x[i]
                x2 = bx + splits_x[i+1]
                y1 = by + 1
                y2 = by + bh - 1
            else:
                y1 = by + splits_y[i]
                y2 = by + splits_y[i+1]
                x1 = bx + 1
                x2 = bx + bw - 1
            # Clamp min size
            if x2 - x1 < 3 or y2 - y1 < 3:
                continue
            room_rects.append((x1, y1, x2, y2))
        # If not enough rooms, fallback to quadrant split
        while len(room_rects) < num_rooms:
            x1 = bx + 2 + 2*len(room_rects)
            y1 = by + 2 + 2*len(room_rects)
            x2 = min(bx+bw-2, x1+4)
            y2 = min(by+bh-2, y1+4)
            room_rects.append((x1, y1, x2, y2))
        # Place rooms, walls, and doors
        doors = []
        for (room, rect) in zip(rooms, room_rects):
            x1, y1, x2, y2 = rect
            # Draw room walls
            for x in range(x1, x2):
                grid[y1][x] = TILE_BUILDING
                grid[y2-1][x] = TILE_BUILDING
            for y in range(y1, y2):
                grid[y][x1] = TILE_BUILDING
                grid[y][x2-1] = TILE_BUILDING
            # Place a door to the hallway or to another room
            def safe_rand(a, b):
                return a if a >= b else random.randint(a, b)
            if room == "bathroom":
                # Always place a door for bathroom
                if x2 - x1 > 2:
                    door_x = safe_rand(x1+1, x2-2)
                    grid[y1][door_x] = TILE_DOOR
                    doors.append((door_x, y1))
                elif y2 - y1 > 2:
                    door_y = safe_rand(y1+1, y2-2)
                    grid[door_y][x1] = TILE_DOOR
                    doors.append((x1, door_y))
                # else: skip door if too small (shouldn't happen)
            else:
                # Place a door on a random wall, but only if wall is long enough
                wall = random.choice(["top", "bottom", "left", "right"])
                if wall == "top" and x2 - x1 > 2:
                    door_x = safe_rand(x1+1, x2-2)
                    grid[y1][door_x] = TILE_DOOR
                    doors.append((door_x, y1))
                elif wall == "bottom" and x2 - x1 > 2:
                    door_x = safe_rand(x1+1, x2-2)
                    grid[y2-1][door_x] = TILE_DOOR
                    doors.append((door_x, y2-1))
                elif wall == "left" and y2 - y1 > 2:
                    door_y = safe_rand(y1+1, y2-2)
                    grid[door_y][x1] = TILE_DOOR
                    doors.append((x1, door_y))
                elif wall == "right" and y2 - y1 > 2:
                    door_y = safe_rand(y1+1, y2-2)
                    grid[door_y][x2-1] = TILE_DOOR
                    doors.append((x2-1, door_y))
            # Place furniture for the room
            place_room(grid, x1+1, y1+1, max(2, x2-x1-2), max(2, y2-y1-2), room)
    debug_log("[CITY] Buildings generated.")
    # --- Extra random roads ---
    for _ in range(extra_roads):
        rx = random.randint(width//4, width*3//4-1)
        ry = random.randint(height//4, height*3//4-1)
        grid[ry][rx] = TILE_ROAD
    debug_log("[CITY] Roads and buildings generation complete.")
    debug_log("[CITY] City map generation complete.")
    return grid

class City:
    """City generation and management."""
    
    def __init__(self, settings=None):
        """Initialize city."""
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.map = [[TILE_GRASS for _ in range(self.width)] for _ in range(self.height)]
        self.shops = {}  # (x, y) -> shop_name
        self.props = {}  # (x, y) -> prop_name
        self.settings = settings or Settings()
        self.generate_city()
    
    def generate_city(self):
        """Generate the city layout."""
        # Generate road grid
        self.generate_roads()
        
        # Fill blocks with buildings and parks
        self.fill_blocks()
        
        # Add building interiors
        self.generate_interiors()
        
        # Add natural features
        self.add_natural_features()
    
    def generate_roads(self):
        """Generate road grid."""
        # Vertical roads
        for x in range(ROAD_SPACING, self.width - ROAD_SPACING, ROAD_SPACING):
            for y in range(self.height):
                for dx in range(ROAD_WIDTH):
                    if 0 <= x + dx < self.width:
                        self.map[y][x + dx] = TILE_ROAD
        
        # Horizontal roads
        for y in range(ROAD_SPACING, self.height - ROAD_SPACING, ROAD_SPACING):
            for x in range(self.width):
                for dy in range(ROAD_WIDTH):
                    if 0 <= y + dy < self.height:
                        self.map[y + dy][x] = TILE_ROAD
    
    def fill_blocks(self):
        """Fill city blocks with buildings and parks."""
        for y in range(0, self.height - ROAD_SPACING, ROAD_SPACING):
            for x in range(0, self.width - ROAD_SPACING, ROAD_SPACING):
                if random.random() < 0.2:  # 20% chance for park
                    self.create_park(x, y)
                else:
                    self.create_building(x, y)
    
    def add_natural_features(self):
        """Add natural features like trees, ponds, and props."""
        prop_candidates = self.settings.prop_prop_candidates
        prop_rate = self.settings.prop_spawn_rate_grass
        for y in range(self.height):
            for x in range(self.width):
                if self.map[y][x] == TILE_GRASS:
                    r = random.random()
                    if r < 0.05:
                        self.map[y][x] = TILE_TREE
                    elif r < 0.07:
                        self.map[y][x] = TILE_POND
                    elif r < 0.07 + prop_rate:  # prop spawn rate
                        prop = random.choice(prop_candidates)
                        self.props[(x, y)] = prop
    
    def create_park(self, start_x, start_y):
        """Create a park in the given block, with trees and props."""
        prop_candidates = self.settings.prop_prop_candidates
        prop_rate = self.settings.prop_spawn_rate_park
        for y in range(start_y, min(start_y + ROAD_SPACING, self.height)):
            for x in range(start_x, min(start_x + ROAD_SPACING, self.width)):
                if self.map[y][x] != TILE_ROAD:
                    r = random.random()
                    if r < 0.1:
                        self.map[y][x] = TILE_TREE
                    elif r < 0.1 + prop_rate:
                        prop = random.choice(prop_candidates)
                        self.props[(x, y)] = prop
                    else:
                        self.map[y][x] = TILE_PARK
    
    def create_building(self, start_x, start_y):
        """Create a building in the given block."""
        debug_log(f"[CITY] Generating building at {start_x},{start_y}")
        
        # Random building size
        width = random.randint(5, ROAD_SPACING - 2)
        height = random.randint(5, ROAD_SPACING - 2)
        
        # Random position within block
        offset_x = random.randint(1, ROAD_SPACING - width - 1)
        offset_y = random.randint(1, ROAD_SPACING - height - 1)
        
        # First create interior floors (MUST HAPPEN BEFORE WALLS)
        for y in range(1, height-1):
            for x in range(1, width-1):
                map_x = start_x + offset_x + x
                map_y = start_y + offset_y + y
                if 0 <= map_x < self.width and 0 <= map_y < self.height:
                    self.map[map_y][map_x] = TILE_FLOOR  # Explicit floor assignment
        
        # Then create walls
        for y in range(height):
            for x in range(width):
                map_x = start_x + offset_x + x
                map_y = start_y + offset_y + y
                if 0 <= map_x < self.width and 0 <= map_y < self.height:
                    if x == 0 or x == width-1 or y == 0 or y == height-1:
                        if self.map[map_y][map_x] != TILE_FLOOR:  # Don't overwrite floors
                            self.map[map_y][map_x] = TILE_BUILDING
        
        # Add main door (always connects to exterior)
        door_side = random.choice(['bottom', 'left', 'right'])  # Top is rare for buildings
        door_placed = False
        
        # Try up to 3 times to place a valid door
        for attempt in range(3):
            if door_side == 'bottom' and height > 2:  # Need space for door not in corner
                door_x = start_x + offset_x + random.randint(1, width-2)  # Avoid corners
                door_y = start_y + offset_y + height - 1
                # Check door leads to grass and connects to interior
                if (door_y + 1 < self.height and 
                    self.map[door_y + 1][door_x] == TILE_GRASS and
                    self.map[door_y - 1][door_x] == TILE_FLOOR):
                    self.map[door_y][door_x] = TILE_DOOR
                    door_placed = True
                    break
            
            elif door_side == 'left' and width > 2:
                door_x = start_x + offset_x
                door_y = start_y + offset_y + random.randint(1, height-2)
                if (door_x > 0 and 
                    self.map[door_y][door_x - 1] == TILE_GRASS and
                    self.map[door_y][door_x + 1] == TILE_FLOOR):
                    self.map[door_y][door_x] = TILE_DOOR
                    door_placed = True
                    break
            
            elif door_side == 'right' and width > 2:
                door_x = start_x + offset_x + width - 1
                door_y = start_y + offset_y + random.randint(1, height-2)
                if (door_x + 1 < self.width and 
                    self.map[door_y][door_x + 1] == TILE_GRASS and
                    self.map[door_y][door_x - 1] == TILE_FLOOR):
                    self.map[door_y][door_x] = TILE_DOOR
                    door_placed = True
                    break
            
            # Try a different side if first attempt failed
            door_side = random.choice(['bottom', 'left', 'right'])
        
        # Fallback - brute force search for valid door location
        if not door_placed:
            for y in range(1, height-1):
                for x in range(1, width-1):
                    map_x = start_x + offset_x + x
                    map_y = start_y + offset_y + y
                    if self.map[map_y][map_x] == TILE_BUILDING:
                        # Check all four directions for potential door placement
                        if (map_y > 0 and map_y < self.height-1 and 
                            self.map[map_y-1][map_x] == TILE_FLOOR and 
                            self.map[map_y+1][map_x] == TILE_GRASS):
                            self.map[map_y][map_x] = TILE_DOOR
                            door_placed = True
                            break
                        elif (map_x > 0 and map_x < self.width-1 and 
                              self.map[map_y][map_x-1] == TILE_FLOOR and 
                              self.map[map_y][map_x+1] == TILE_GRASS):
                            self.map[map_y][map_x] = TILE_DOOR
                            door_placed = True
                            break
                    if door_placed:
                        break
                if door_placed:
                    break
        
        # Add windows (only on walls facing grass)
        window_count = 0
        for y in range(height):
            for x in range(width):
                map_x = start_x + offset_x + x
                map_y = start_y + offset_y + y
                
                # Only place windows on outer walls that aren't doors
                if (x == 0 or x == width - 1 or y == 0 or y == height - 1) and \
                   self.map[map_y][map_x] == TILE_BUILDING:
                    
                    # Check if wall faces grass (potential window location)
                    if x == 0 and map_x > 0 and self.map[map_y][map_x - 1] == TILE_GRASS and random.random() < 0.3:
                        self.map[map_y][map_x] = TILE_WINDOW
                        window_count += 1
                    elif x == width - 1 and map_x < self.width - 1 and self.map[map_y][map_x + 1] == TILE_GRASS and random.random() < 0.3:
                        self.map[map_y][map_x] = TILE_WINDOW
                        window_count += 1
                    elif y == 0 and map_y > 0 and self.map[map_y - 1][map_x] == TILE_GRASS and random.random() < 0.3:
                        self.map[map_y][map_x] = TILE_WINDOW
                        window_count += 1
                    elif y == height - 1 and map_y < self.height - 1 and self.map[map_y + 1][map_x] == TILE_GRASS and random.random() < 0.3:
                        self.map[map_y][map_x] = TILE_WINDOW
                        window_count += 1
        
        debug_log(f"[CITY] Building generated with {door_placed and 'a door' or 'NO DOOR'} and {window_count} windows")
    
    def generate_interiors(self):
        """Generate building interiors."""
        debug_log("[CITY] Generating building interiors...")
        # First pass: mark all interior building tiles as floor
        to_floor = []
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if self.map[y][x] == TILE_BUILDING:
                    # If any neighbor is not TILE_BUILDING, this is a wall
                    if (self.map[y-1][x] != TILE_BUILDING or self.map[y+1][x] != TILE_BUILDING or
                        self.map[y][x-1] != TILE_BUILDING or self.map[y][x+1] != TILE_BUILDING):
                        continue  # keep as wall
                    else:
                        to_floor.append((x, y))
        debug_log(f"[CITY] {len(to_floor)} interior tiles to convert to floor.")
        for x, y in to_floor:
            self.map[y][x] = TILE_FLOOR
        # Second pass: place furniture only on floor tiles
        furniture_count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.map[y][x] == TILE_FLOOR:
                    if random.random() < 0.1:
                        furniture = random.choice([
                            TILE_TOILET, TILE_OVEN, TILE_BED, TILE_DESK,
                            TILE_SHOP_SHELF, TILE_TABLE, TILE_FRIDGE,
                            TILE_COUNTER, TILE_SINK, TILE_TUB
                        ])
                        self.map[y][x] = furniture
                        furniture_count += 1
                        if furniture == TILE_SHOP_SHELF:
                            shop_type = random.choice(['General Store', 'Clothing Store'])
                            self.shops[(x, y)] = shop_type
        debug_log(f"[CITY] Placed {furniture_count} furniture items in interiors.")
    
    def get_tile(self, x, y):
        """Get tile at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.map[y][x]
        return TILE_GRASS
    
    def get_shop_at(self, x, y):
        """Get shop name at position."""
        return self.shops.get((x, y))

    def set_walkable(self, x, y, walkable):
        """
        Mark a tile as walkable or not walkable.
        Used primarily for doors that can change state.
        Note: This doesn't change the underlying tile type,
        just how it's treated for pathfinding/movement.
        """
        if not hasattr(self, '_walkability_overrides'):
            self._walkability_overrides = {}
        
        if walkable:
            if (x, y) in self._walkability_overrides:
                del self._walkability_overrides[(x, y)]
        else:
            self._walkability_overrides[(x, y)] = False

    def is_shop_tile(self, x, y):
        """Check if the given location is part of a shop."""
        # Check surrounding tiles for shop registration
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (x + dx, y + dy) in self.shops:
                    return True
        return False

    def find_walkable_tile(self):
        """Find a random walkable tile in the city."""
        walkable_tiles = []
        for y in range(self.height):
            for x in range(self.width):
                if self.is_walkable(x, y):
                    walkable_tiles.append((x, y))
        return random.choice(walkable_tiles) if walkable_tiles else (None, None)

    def find_road_tile(self):
        """Find a random road tile in the city."""
        road_tiles = []
        for y in range(self.height):
            for x in range(self.width):
                if self.get_tile(x, y) == TILE_ROAD:
                    road_tiles.append((x, y))
        return random.choice(road_tiles) if road_tiles else (None, None)

    def is_walkable(self, x, y):
        """Check if a tile is walkable."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
            
        # First check walkability overrides if they exist
        if hasattr(self, '_walkability_overrides') and (x, y) in self._walkability_overrides:
            return self._walkability_overrides[(x, y)]
            
        tile = self.get_tile(x, y)
        walkable_tiles = [TILE_FLOOR, TILE_ROAD, TILE_GRASS, TILE_PARK]
        return tile in walkable_tiles