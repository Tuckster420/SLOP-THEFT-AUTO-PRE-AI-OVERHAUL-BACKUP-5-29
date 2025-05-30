import pygame
import random
import math
from stinkworld.core.settings import (
    TILE_SIZE, COLOR_NPC, MAP_WIDTH, MAP_HEIGHT, TILE_ROAD, TILE_PARK, TILE_FLOOR, TILE_DOOR, TILE_GRASS,
    NPC_SPEED, NPC_MAX_HP, NPC_VIEW_DISTANCE, COLOR_WHITE
)
from stinkworld.ui.appearance import (
    draw_portrait, FACE_SHAPES, EYE_TYPES, HAIR_STYLES, HAIR_COLORS, CLOTHES,
    SKIN_TONES, generate_vitiligo_patches
)
from stinkworld.entities.npc_generator import generate_biography
from stinkworld.data.personality import PERSONALITY_FLAVOR
from stinkworld.utils.debug import debug_log

# Expanded name lists for more diversity
FIRST_NAMES_FEM = [
    "Aaren","Abbey","Abby","Ada","Adah","Adaline","Adan","Adda","Addie","Adela",
    "Adelaide","Adele","Adeline","Adella","Adelle","Adina","Adora","Adrian","Adriana","Adrienne",
    "Afton","Agatha","Agnes","Aida","Aileen","Aimee","Ainsley","Aisha","Aja","Alaina",
    "Alana","Alanna","Alayna","Alberta","Aleah","Alejandra","Alexa","Alexandra","Alexis","Alice",
    "Alicia","Alina","Alisa","Alisha","Alison","Alissa","Allie","Allison","Ally","Alma",
    "Alondra","Alyce","Alyson","Alyssa","Amanda","Amber","Amelia","Amie","Amy","Ana",
    "Anastasia","Andrea","Angela","Angelica","Angelina","Angie","Anika","Anissa","Anita","Ann",
    "Anna","Annabel","Annabelle","Anne","Annette","Annie","Annika","Ansley","Antonia","April",
    "Araceli","Ariana","Arianna","Ariel","Arielle","Arlene","Ashlee","Ashley","Ashlyn","Aspen",
    "Astrid","Athena","Aubrey","Audra","Audrey","Autumn","Ava","Avery","Ayana","Ayanna"
]
FIRST_NAMES_MASC = [
    "Aaron","Adam","Adrian","Aidan","Aiden","Alan","Albert","Alec","Alex","Alexander",
    "Alfred","Ali","Allen","Alvin","Amir","Andre","Andrew","Andy","Angel","Anthony",
    "Antonio","Arthur","Asher","Austin","Avery","Axel","Barry","Ben","Benjamin","Bennett",
    "Billy","Blake","Brad","Bradley","Brady","Brandon","Brendan","Brian","Bruce","Bryan",
    "Caleb","Cameron","Carl","Carlos","Carter","Casey","Charles","Charlie","Chase","Chris",
    "Christian","Christopher","Clark","Clayton","Clifford","Clint","Cody","Colin","Connor","Corey",
    "Craig","Curtis","Cyrus","Dale","Damian","Damon","Dan","Daniel","Danny","Dante",
    "Darren","David","Dean","Dennis","Derek","Derrick","Devin","Diego","Dominic","Don",
    "Donald","Douglas","Drew","Dustin","Dylan","Eddie","Edward","Edwin","Eli","Elias"
]
FIRST_NAMES_NB = [
    "Alex","Avery","Bailey","Blair","Casey","Charlie","Dakota","Devon","Drew","Eden",
    "Emerson","Finley","Harley","Hayden","Jamie","Jesse","Jordan","Kai","Kendall","Lane",
    "Logan","Morgan","Parker","Quinn","Reese","Riley","River","Rowan","Sage","Skyler",
    "Taylor","Toby","Tristan"
]

LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
    "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
    "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
    "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","AdAMS","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts",
    "Gomez","Phillips","Evans","Turner","Diaz","Parker","Cruz","Edwards","Collins","Reyes",
    "Stewart","Morris","Morales","Murphy","Cook","Rogers","Gutierrez","Ortiz","Morgan","Cooper",
    "Peterson","Bailey","Reed","Kelly","Howard","Ramos","Kim","Cox","Ward","Richardson",
    "Watson","Brooks","Chavez","Wood","James","Bennett","Gray","Mendoza","Ruiz","Hughes",
    "Price","Alvarez","Castillo","Sanders","Patel","Myers","Long","Ross","Foster","Jimenez"
]

# Personality types
PERSONALITIES = [
    'Friendly', 'Grumpy', 'Timid', 'Aggressive',
    'Forgiving', 'Grudgeful', 'Chatty', 'Quiet'
]

def random_name():
    group = random.choices(
        ["fem", "masc", "nb"], weights=[0.4, 0.4, 0.2]
    )[0]
    if group == "fem":
        first = random.choice(FIRST_NAMES_FEM)
    elif group == "masc":
        first = random.choice(FIRST_NAMES_MASC)
    else:
        first = random.choice(FIRST_NAMES_NB)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"

def random_personality():
    return random.choice(PERSONALITIES)

# --- INJURY SYSTEM ---
INJURY_TYPES = {
    "bruise": {"severity": 1, "heal_turns": 30, "bleed": False, "limp": False},
    "sprain": {"severity": 2, "heal_turns": 100, "bleed": False, "limp": True},
    "fracture": {"severity": 3, "heal_turns": 200, "bleed": False, "limp": True},
    "cut": {"severity": 2, "heal_turns": 60, "bleed": True, "limp": False},
    "deep wound": {"severity": 3, "heal_turns": 150, "bleed": True, "limp": True},
}
BODY_PARTS = [
    "head", "left arm", "right arm", "left leg", "right leg", "chest", "abdomen"
]

class NPC:
    """Non-player character class."""
    
    def __init__(self, name, x, y, personality=None):
        """Initialize NPC."""
        self.name = name
        self.x = x
        self.y = y
        
        # Stats
        self.hp = NPC_MAX_HP
        self.max_hp = NPC_MAX_HP
        self.speed = NPC_SPEED
        
        # State
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.is_moving = False
        self.is_knocked_out = False
        self.is_dead = False
        self.is_hostile = False
        self.target = None
        
        # Personality and behavior
        self.personality = (personality or random.choice(PERSONALITIES)).lower()
        
        # Schedule and routine
        self.schedule = self.generate_schedule()
        self.current_activity = None
        
        # Inventory and equipment
        self.money = random.randint(10, 100)
        self.inventory = []
        self.equipped = {
            'weapon': None,
            'armor': None
        }
        
        # Relationship status
        self.relationship_status = random.choice(['single', 'dating', 'married', 'divorced', 'widowed'])
        self.significant_other = None
        
        # Reputation system
        self.reputation = {
            'kindness': random.randint(-50, 50),
            'reliability': random.randint(-50, 50),
            'honesty': random.randint(-50, 50),
            'bravery': random.randint(-50, 50)
        }
        
        # Social connections
        self.friends = set()
        self.enemies = set()
        self.family = set()

        # Movement and pathfinding
        self.move_cooldown = 0
        self.path = []
        self.destination = None
        self.facing = 'down'  # 'up', 'down', 'left', 'right'
        
        # Animation state
        self.animation_frame = 0
        self.animation_timer = 0
        self.hair_sway = 0
        self.hair_sway_speed = random.uniform(0.05, 0.15)
        self.hair_sway_amount = random.uniform(2, 4)
        self.hair_animation_offset = random.uniform(0, 6.28)  # Random starting phase (0 to 2π)
        
        # Stats based on personality
        self.strength = 5
        self.defense = 2
        self.street_smarts = 2
        self.adjust_stats_by_personality()

        # Relationship
        self.relationship = 0  # Default neutral relationship

        # Appearance
        from stinkworld.entities.appearance import generate_npc_appearance
        self.appearance = generate_npc_appearance()
        
        # Biography
        from stinkworld.entities.npc_generator import generate_biography
        self.biography = generate_biography(self.appearance)
        
        # Memory
        self.memory = {}

        # Optional status flags
        self.vandalized = False
        self.robbed = False
        self.driving_skill = random.randint(1, 5)  # 1-5 scale
        self.current_vehicle = None

    def adjust_stats_by_personality(self):
        """Adjust NPC stats based on their personality"""
        personality_mods = {
            'friendly': {'defense': 1, 'street_smarts': 1, 'strength': -1},
            'grumpy': {'strength': 2, 'defense': -1},
            'timid': {'defense': 2, 'speed': 1, 'strength': -2},
            'aggressive': {'strength': 3, 'defense': -1, 'speed': 1},
            'forgiving': {'defense': 2, 'strength': -1},
            'grudgeful': {'strength': 1, 'speed': 1},
            'chatty': {'street_smarts': 2, 'defense': -1},
            'quiet': {'defense': 1, 'street_smarts': -1}
        }
        
        if self.personality in personality_mods:
            mods = personality_mods[self.personality]
            for stat, mod in mods.items():
                if hasattr(self, stat):
                    setattr(self, stat, getattr(self, stat) + mod)

    def generate_schedule(self):
        """Generate a daily schedule for the NPC"""
        schedule = {
            'morning': random.choice(['sleeping', 'working', 'exercising', 'shopping']),
            'afternoon': random.choice(['working', 'relaxing', 'shopping', 'socializing']),
            'evening': random.choice(['working', 'relaxing', 'socializing', 'sleeping']),
            'night': random.choice(['sleeping', 'working', 'partying', 'relaxing'])
        }
        return schedule

    def update(self, city_map, npcs, player):
        """Guaranteed NPC movement"""
        if self.is_dead or self.is_knocked_out:
            return
        if random.random() < 0.3:  # 30% chance to move each turn
            directions = [(0,1),(0,-1),(1,0),(-1,0)]
            dx, dy = random.choice(directions)
            if self.is_walkable(city_map, self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy
                print(f"NPC moved to ({self.x}, {self.y})")

    def can_see_player(self, player):
        """Check if NPC can see the player."""
        if player.is_dead:
            return False
            
        dx = abs(self.x - player.x)
        dy = abs(self.y - player.y)
        return dx <= NPC_VIEW_DISTANCE and dy <= NPC_VIEW_DISTANCE
    
    def move_towards_target(self, city_map, npcs, cars):
        """Move towards target."""
        if not self.target:
            return
            
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        
        # Determine movement direction
        if abs(dx) > abs(dy):
            dx = 1 if dx > 0 else -1
            dy = 0
        else:
            dx = 0
            dy = 1 if dy > 0 else -1
        
        self.move(dx, dy, city_map, npcs, cars)
    
    def wander(self, city_map, npcs, cars):
        """Random movement when no target."""
        if random.random() < 0.1:  # 10% chance to change direction
            self.direction = random.choice(['up', 'down', 'left', 'right'])
        
        dx = 0
        dy = 0
        if self.direction == 'right':
            dx = 1
        elif self.direction == 'left':
            dx = -1
        elif self.direction == 'down':
            dy = 1
        else:  # up
            dy = -1
        
        if not self.move(dx, dy, city_map, npcs, cars):
            # If movement failed, try a different direction
            self.direction = random.choice(['up', 'down', 'left', 'right'])
    
    def move(self, dx, dy, city_map, npcs, cars):
        """Handle NPC movement."""
        new_x = self.x + dx
        new_y = self.y + dy

        # Check for collisions with other NPCs
        for npc in npcs:
            if not hasattr(npc, 'x') or not hasattr(npc, 'y') or not hasattr(npc, 'is_dead'):
                continue  # Skip non-NPC objects (e.g., lists)
            if npc != self and npc.x == new_x and npc.y == new_y and not npc.is_dead:
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
        """Check if position is valid for NPC by using the city's walkability system."""
        if hasattr(self, 'game') and hasattr(self.game, 'city'):
            return self.game.city.is_walkable(x, y)
        # Fallback for when city isn't available (shouldn't happen)
        if 0 <= x < len(city_map[0]) and 0 <= y < len(city_map):
            tile = city_map[y][x]
            return tile in [0, 1, 3, 4, 5]  # Grass, road, park, door, floor
        return False
    
    def draw(self, screen, camera_x, camera_y):
        """Draw NPC on screen with their portrait."""
        screen_x = (self.x - camera_x) * TILE_SIZE
        screen_y = (self.y - camera_y) * TILE_SIZE

        # Draw portrait if not dead or knocked out
        if not self.is_dead and not self.is_knocked_out:
            from stinkworld.ui.appearance import draw_portrait
            portrait_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            draw_portrait(portrait_surface, 0, 0, TILE_SIZE, self.appearance)
            screen.blit(portrait_surface, (screen_x, screen_y))
        elif self.is_knocked_out:
            self.draw_knocked_out(screen, camera_x, camera_y)
        elif self.is_dead:
            self.draw_dead(screen, camera_x, camera_y)
        # Optionally, draw direction indicator or overlays as before

    def take_damage(self, amount):
        """Handle taking damage."""
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.is_dead = True
        elif random.random() < 0.3:  # 30% chance to be knocked out
            self.is_knocked_out = True
        return self.is_dead
    
    def heal(self, amount):
        """Heal NPC."""
        self.hp = min(self.max_hp, self.hp + amount)
        if self.hp > 0:
            self.is_dead = False

    def update_relationship(self, event_type, amount):
        """Update relationship based on interactions"""
        self.relationship = max(-100, min(100, self.relationship + amount))
        
        # Update reputation based on event
        if event_type == 'gift':
            self.reputation['kindness'] += random.randint(5, 10)
        elif event_type == 'fight':
            self.reputation['kindness'] -= random.randint(5, 10)
            self.reputation['bravery'] += random.randint(-5, 10)
        elif event_type == 'help':
            self.reputation['reliability'] += random.randint(5, 10)
        elif event_type == 'lie':
            self.reputation['honesty'] -= random.randint(5, 10)

    def add_memory(self, event_type, turn, details):
        """Add a memory of an interaction"""
        if event_type not in self.memory:
            self.memory[event_type] = []
        self.memory[event_type].append((turn, details))
        
        # Update relationships based on memory
        memory_impacts = {
            'gift': 10,
            'fight': -20,
            'help': 15,
            'chat': 5,
            'insult': -15,
            'lie': -10
        }
        
        if event_type in memory_impacts:
            self.update_relationship(event_type, memory_impacts[event_type])

    def start_conversation(self):
        """Start a conversation by selecting a topic and getting possible responses."""
        from conversations_data import CONVERSATIONS
        
        # Check if knocked out
        if self.is_knocked_out:
            return {
                "prompt": "...",
                "responses": [("They're unconscious.", "You decide to leave them alone.")]
            }
        
        # If relationship is very negative, they won't talk
        if self.relationship <= -50:
            return {
                "prompt": "I don't want to talk to you!",
                "responses": [("...", "You decide to leave them alone.")]
            }
        
        # Select a conversation based on personality
        conversation = random.choice(CONVERSATIONS)
        
        # Add personality flavor to the prompt
        if self.personality in PERSONALITY_FLAVOR:
            flavor = PERSONALITY_FLAVOR[self.personality]
            if random.random() < 0.3:  # 30% chance to add flavor
                conversation = conversation.copy()  # Make a copy to not modify the original
                conversation["prompt"] = f"{flavor['greeting']} {conversation['prompt']}"
        
        return conversation

    def get_simple_response(self):
        """Get a simple response (used for non-conversation interactions)"""
        # Check if knocked out
        if self.is_knocked_out:
            return "..."
            
        if self.relationship <= -50:
            return "I don't want to talk to you!"
        
        if self.personality in PERSONALITY_FLAVOR:
            responses = {
                'high': [
                    f"{PERSONALITY_FLAVOR[self.personality]['greeting']} It's great to see you!",
                    "I was just thinking about you!",
                    "What a pleasant surprise!"
                ],
                'medium': [
                    PERSONALITY_FLAVOR[self.personality]['talk'],
                    "How are you today?",
                    "Nice weather we're having."
                ],
                'low': [
                    "...",
                    "What do you want?",
                    PERSONALITY_FLAVOR[self.personality]['greeting']
                ]
            }
            
            if self.relationship >= 50:
                return random.choice(responses['high'])
            elif self.relationship >= 0:
                return random.choice(responses['medium'])
            else:
                return random.choice(responses['low'])
        
        return "Hello."

    def get_description(self):
        """Get NPC's full description including biography and current state"""
        status = []
        
        # Add biography
        status.append(self.biography)
        status.append("")
        
        # Add current state
        if self.is_dead:
            status.append("They are dead.")
        elif self.is_knocked_out:
            status.append("They are currently knocked out and unresponsive.")
        elif self.hp < self.max_hp // 2:
            status.append("They appear to be injured.")
        
        # Add vandalism status
        if hasattr(self, 'vandalized') and self.vandalized:
            status.append(f"Someone has drawn {self.appearance.get('graffiti', 'something')} on their face.")
        
        # Add robbery status
        if hasattr(self, 'robbed') and self.robbed:
            status.append("Their pockets have been emptied.")
        
        # Add relationship status
        if self.relationship_status != 'single':
            status.append(f"Relationship Status: {self.relationship_status.title()}")
        
        # Add current activity
        if self.current_activity and not self.is_knocked_out and not self.is_dead:
            status.append(f"Currently: {self.current_activity}")
        
        # Add relationship with player
        rel_desc = {
            range(-100, -75): "They hate you with a passion.",
            range(-74, -50): "They strongly dislike you.",
            range(-49, -25): "They are wary of you.",
            range(-24, 25): "They are neutral towards you.",
            range(26, 50): "They consider you friendly.",
            range(51, 75): "They like you quite a bit.",
            range(76, 101): "They consider you a close friend."
        }
        
        for range_key, desc in rel_desc.items():
            if self.relationship in range_key:
                status.append(desc)
                break
        
        # Add memories if any
        if self.memory:
            status.append("\nRecent Memories:")
            for event_type, memories in self.memory.items():
                if memories:
                    latest = memories[-1]
                    status.append(f"- {event_type.title()}: {latest[1].get('description', 'No details')}")
        
        return "\n".join(status)

    def draw_knocked_out(self, screen, camera_x, camera_y):
        """Draw the NPC in a knocked out state."""
        screen_x = (self.x - camera_x) * TILE_SIZE
        screen_y = (self.y - camera_y) * TILE_SIZE
        
        # Draw body sideways
        pygame.draw.rect(screen, self.appearance['skin_tone'],
                        (screen_x + 8, screen_y + 12, 16, 8))
        
        # Draw X's for eyes
        pygame.draw.line(screen, (0, 0, 0),
                        (screen_x + 12, screen_y + 14),
                        (screen_x + 16, screen_y + 18))
        pygame.draw.line(screen, (0, 0, 0),
                        (screen_x + 12, screen_y + 18),
                        (screen_x + 16, screen_y + 14))

    def draw_dead(self, screen, camera_x, camera_y):
        """Draw the NPC in a dead state."""
        screen_x = (self.x - camera_x) * TILE_SIZE
        screen_y = (self.y - camera_y) * TILE_SIZE
        
        # Draw body outline
        pygame.draw.rect(screen, (100, 0, 0),
                        (screen_x + 8, screen_y + 8, 16, 16), 1)
        
        # Draw X marks
        pygame.draw.line(screen, (100, 0, 0),
                        (screen_x + 8, screen_y + 8),
                        (screen_x + 24, screen_y + 24))
        pygame.draw.line(screen, (100, 0, 0),
                        (screen_x + 24, screen_y + 8),
                        (screen_x + 8, screen_y + 24))

    def can_drive(self):
        """Check if NPC can drive based on their skills."""
        return self.driving_skill > 2  # Only skilled enough NPCs can drive
        
    def enter_vehicle(self, vehicle):
        """Attempt to enter a vehicle."""
        if not self.can_drive():
            return False
            
        if vehicle.set_driver(self):
            self.current_vehicle = vehicle
            return True
        return False
        
    def exit_vehicle(self):
        """Exit current vehicle if in one."""
        if self.current_vehicle:
            self.current_vehicle.remove_driver()
            self.current_vehicle = None
            return True
        return False
        
    def update_driving(self, city_map, npcs, player=None, cars=None):
        """Update behavior when driving a vehicle."""
        if not self.current_vehicle:
            return
            
        # If we have a destination, drive toward it
        if hasattr(self, 'destination') and self.destination:
            dx = self.destination[0] - self.current_vehicle.x
            dy = self.destination[1] - self.current_vehicle.y
            
            # Simple driving logic - could be improved with proper pathfinding
            if abs(dx) > abs(dy):
                self.current_vehicle.handle_player_input(1 if dx > 0 else -1, 0, city_map, [], npcs)
            else:
                self.current_vehicle.handle_player_input(0, 1 if dy > 0 else -1, city_map, [], npcs)
        else:
            # Random driving if no destination
            direction = random.choice(['up', 'down', 'left', 'right'])
            if direction == 'up':
                self.current_vehicle.handle_player_input(0, -1, city_map, [], npcs)
            elif direction == 'down':
                self.current_vehicle.handle_player_input(0, 1, city_map, [], npcs)
            elif direction == 'left':
                self.current_vehicle.handle_player_input(-1, 0, city_map, [], npcs)
            elif direction == 'right':
                self.current_vehicle.handle_player_input(1, 0, city_map, [], npcs)

    def debug(self, message):
        """Log debug messages."""
        debug_log(message)

    def is_walkable(self, city_map, x, y):
        """Check if a tile is walkable for NPCs."""
        if isinstance(city_map, list):
            if 0 <= x < len(city_map[0]) and 0 <= y < len(city_map):
                return city_map[y][x] in (0, 1)  # 0=road, 1=sidewalk
            return False
        else:
            return city_map.is_walkable(x, y)