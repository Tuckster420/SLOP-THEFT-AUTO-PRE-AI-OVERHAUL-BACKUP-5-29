"""Game settings and constants."""

from stinkworld.utils.debug import debug_log

# Display settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 32

# Map settings
MAP_WIDTH = 100
MAP_HEIGHT = 100
ROAD_SPACING = 12  # Space between roads
ROAD_WIDTH = 2    # Width of roads in tiles

# Tile types
TILE_GRASS = 0
TILE_ROAD = 1
TILE_BUILDING = 2
TILE_PARK = 3
TILE_DOOR = 4
TILE_FLOOR = 5
TILE_TOILET = 6
TILE_OVEN = 7
TILE_BED = 8
TILE_DESK = 9
TILE_SHOP_SHELF = 10
TILE_TABLE = 11
TILE_TREE = 12
TILE_POND = 13
TILE_FRIDGE = 14
TILE_COUNTER = 15
TILE_SINK = 16
TILE_TUB = 17
TILE_COUNTRY_HOUSE = 18
TILE_WINDOW = 20  # Make sure this value doesn't conflict with other tile types

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_PLAYER = (255, 128, 0)  # Orange color for player
COLOR_NPC = (0, 128, 255)     # Light blue color for NPCs
COLOR_TRAFFIC_GREEN = (0, 255, 0)  # Traffic light colors
COLOR_TRAFFIC_YELLOW = (255, 255, 0)
COLOR_TRAFFIC_RED = (255, 0, 0)

# Player settings
PLAYER_SPEED = 5
PLAYER_MAX_HP = 100
PLAYER_MAX_ENERGY = 100
PLAYER_MAX_HUNGER = 100
PLAYER_MAX_THIRST = 100
PLAYER_MAX_STRESS = 100

# NPC settings
NPC_SPEED = 3
NPC_MAX_HP = 100
NPC_VIEW_DISTANCE = 8

# Time settings
GAME_HOUR = 1000  # milliseconds per game hour
DAY_LENGTH = 24 * GAME_HOUR

# Weather settings
WEATHER_CHANGE_CHANCE = 0.1
WEATHER_TYPES = ['clear', 'cloudy', 'rain', 'storm']

# Traffic settings
GREEN_TIME = 180  # Time in frames for each traffic light state
YELLOW_TIME = 60
RED_TIME = 180
TRAFFIC_LIGHT_GREEN_TIME = GREEN_TIME
TRAFFIC_LIGHT_YELLOW_TIME = YELLOW_TIME
TRAFFIC_LIGHT_RED_TIME = RED_TIME

# Combat settings
DAMAGE_MULTIPLIER = 1.0
DEFENSE_MULTIPLIER = 0.5
CRITICAL_HIT_CHANCE = 0.1
CRITICAL_HIT_MULTIPLIER = 2.0

# Economy settings
STARTING_MONEY = 1000
SHOP_MARKUP = 1.5
SHOP_HOURS = (8, 20)  # 8 AM to 8 PM

# UI settings
UI_FONT_SIZE = 24
UI_PADDING = 10
UI_MARGIN = 5
UI_BACKGROUND_COLOR = (0, 0, 0, 128)  # Semi-transparent black
UI_TEXT_COLOR = (255, 255, 255)
UI_HIGHLIGHT_COLOR = (255, 255, 0)
UI_FONT = None  # Use system default font
UI_COLOR = UI_TEXT_COLOR

# Sound settings
SOUND_ENABLED = True
MUSIC_VOLUME = 0.5
SFX_VOLUME = 0.7

# Debug settings
DEBUG_MODE = False
SHOW_HITBOXES = False
SHOW_PATHFINDING = False
LOG_LEVEL = 'INFO'

# Prop customization settings
PROP_SPAWN_RATE_GRASS = 0.05  # Chance for a prop on grass tile
PROP_SPAWN_RATE_PARK = 0.15   # Chance for a prop in park
PROP_PROP_CANDIDATES = [
    'bush_01', 'bush_02', 'bush_03', 'bush_04', 'bush_05',
    'rock_1', 'rock_2', 'rock_3', 'rock_4', 'rock_5',
    'flower_01', 'flower_02', 'flower_03', 'flower_04', 'flower_05',
    'plant_01', 'plant_02', 'plant_03', 'plant_04', 'plant_05'
]

class Settings:
    """Game settings class that encapsulates all game settings."""
    def __init__(self):
        # Display settings
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.fps = FPS
        self.tile_size = TILE_SIZE
        
        # Map settings
        self.map_width = MAP_WIDTH
        self.map_height = MAP_HEIGHT
        self.road_spacing = ROAD_SPACING
        self.road_width = ROAD_WIDTH
        
        # Colors
        self.color_black = COLOR_BLACK
        self.color_white = COLOR_WHITE
        self.color_red = COLOR_RED
        self.color_green = COLOR_GREEN
        self.color_blue = COLOR_BLUE
        self.color_yellow = COLOR_YELLOW
        self.color_gray = COLOR_GRAY
        self.color_player = COLOR_PLAYER
        self.color_npc = COLOR_NPC
        
        # Player settings
        self.player_speed = PLAYER_SPEED
        self.player_max_hp = PLAYER_MAX_HP
        self.player_max_energy = PLAYER_MAX_ENERGY
        self.player_max_hunger = PLAYER_MAX_HUNGER
        self.player_max_thirst = PLAYER_MAX_THIRST
        self.player_max_stress = PLAYER_MAX_STRESS
        
        # NPC settings
        self.npc_speed = NPC_SPEED
        self.npc_max_hp = NPC_MAX_HP
        self.npc_view_distance = NPC_VIEW_DISTANCE
        
        # Time settings
        self.game_hour = GAME_HOUR
        self.day_length = DAY_LENGTH
        
        # Weather settings
        self.weather_change_chance = WEATHER_CHANGE_CHANCE
        self.weather_types = WEATHER_TYPES.copy()
        
        # Traffic settings
        self.traffic_light_green_time = TRAFFIC_LIGHT_GREEN_TIME
        self.traffic_light_yellow_time = TRAFFIC_LIGHT_YELLOW_TIME
        self.traffic_light_red_time = TRAFFIC_LIGHT_RED_TIME
        
        # Combat settings
        self.damage_multiplier = DAMAGE_MULTIPLIER
        self.defense_multiplier = DEFENSE_MULTIPLIER
        self.critical_hit_chance = CRITICAL_HIT_CHANCE
        self.critical_hit_multiplier = CRITICAL_HIT_MULTIPLIER
        
        # Economy settings
        self.starting_money = STARTING_MONEY
        self.shop_markup = SHOP_MARKUP
        self.shop_hours = SHOP_HOURS
        
        # UI settings
        self.ui_font_size = UI_FONT_SIZE
        self.ui_padding = UI_PADDING
        self.ui_margin = UI_MARGIN
        self.ui_background_color = UI_BACKGROUND_COLOR
        self.ui_text_color = UI_TEXT_COLOR
        self.ui_highlight_color = UI_HIGHLIGHT_COLOR
        self.ui_font = UI_FONT
        self.ui_color = UI_COLOR
        
        # Sound settings
        self.sound_enabled = SOUND_ENABLED
        self.music_volume = MUSIC_VOLUME
        self.sfx_volume = SFX_VOLUME
        
        # Debug settings
        self.debug_mode = DEBUG_MODE
        self.show_hitboxes = SHOW_HITBOXES
        self.show_pathfinding = SHOW_PATHFINDING
        self.log_level = LOG_LEVEL

        # Prop customization
        self.prop_spawn_rate_grass = PROP_SPAWN_RATE_GRASS
        self.prop_spawn_rate_park = PROP_SPAWN_RATE_PARK
        self.prop_prop_candidates = PROP_PROP_CANDIDATES.copy()