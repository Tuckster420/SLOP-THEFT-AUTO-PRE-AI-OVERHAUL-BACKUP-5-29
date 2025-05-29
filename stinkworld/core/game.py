"""Main game module."""
import pygame
import sys
import random
import json
import os
from datetime import datetime, timedelta
from stinkworld.ui.menus import main_menu
from stinkworld.entities.character_creation import character_creation
from stinkworld.core.settings import (
    Settings, TILE_ROAD, TILE_PARK, TILE_FLOOR, TILE_DOOR, TILE_GRASS,
    TILE_TREE, TILE_POND, TILE_TOILET, TILE_OVEN, TILE_BED, TILE_DESK,
    TILE_SHOP_SHELF, TILE_TABLE, TILE_FRIDGE, TILE_COUNTER, TILE_SINK,
    TILE_TUB, TILE_COUNTRY_HOUSE, TILE_BUILDING, TILE_WINDOW
)
from stinkworld.systems.weather import WeatherSystem
from stinkworld.systems.time import TimeSystem
from stinkworld.ui.base import UI
from stinkworld.ui.graphics import Graphics
from stinkworld.entities.player import Player
from stinkworld.systems.economy import Economy
from stinkworld.core.city import City  # <-- Correct import for City
from stinkworld.utils.debug import debug_log
from stinkworld.data.names import random_name
from stinkworld.entities.npc import NPC
from stinkworld.entities.car import Car
from stinkworld.systems.traffic import TrafficLight
from stinkworld.combat.messages import car_combat_message
from stinkworld.ui.appearance import draw_portrait

# Viewport size in tiles
from stinkworld.core.settings import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
VIEWPORT_WIDTH = SCREEN_WIDTH // TILE_SIZE
VIEWPORT_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

class Game:
    """Main game class."""
    
    def __init__(self, settings):
        """Initialize game."""
        self.settings = settings
        self.screen = pygame.display.set_mode(
            (settings.screen_width, settings.screen_height)
        )
        pygame.display.set_caption("Slop Theft Auto")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize systems
        self.time_system = TimeSystem()
        self.weather_system = WeatherSystem()
        
        # Initialize UI
        self.ui = UI(settings)
        self.graphics = Graphics(self)
        
        self.state = "menu"
        self.city = None
        self.npcs = []
        self.cars = []
        self.traffic_lights = []
        self.turn = 0
        self.message_to_show = None
        self.player = None
        self.furniture_state = {}  # (x, y): {'state': 'normal'|'moved'|'broken'|'vandalized', 'type': tile, 'desc': str}
        self.economy = Economy()  # Initialize economy system

        self.debug("Game initialized.")
        
        # Initialize city and spawn entities
        self.city = City()
        self.spawn_npcs(50)  # Spawn 50 NPCs at game start
        self.spawn_cars(3)   # Spawn 3 cars at game start

    def debug(self, message):
        debug_log(f"[Game] {message}")

    def toggle_door_window(self, x, y, tile_type, action):
        """Toggle door/window state and update walkability."""
        if (x, y) not in self.furniture_state:
            self.furniture_state[(x, y)] = {}
        
        current_state = self.furniture_state[(x, y)].get('state', 'closed')
        new_state = 'open' if current_state == 'closed' else 'closed'
        self.furniture_state[(x, y)]['state'] = new_state
        
        # Update walkability for doors
        if tile_type == TILE_DOOR:
            self.city.set_walkable(x, y, new_state == 'open')
            
            # Force redraw of the tile to show new state
            self.graphics.redraw_tile(x, y)
        
        self.debug(f"Toggled {tile_type} at ({x}, {y}) to {new_state}")

    def run(self):
        """Main game loop."""
        move_cooldown = 0
        game_tick = 0
        
        # Initialize player if not set
        if not hasattr(self, 'player') or self.player is None:
            self.player = Player("DefaultPlayer")
            
        # Initialize city if not set
        if not hasattr(self, 'city') or self.city is None:
            self.city = City()
            
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.show_pause_menu()
                    elif event.key == pygame.K_e:
                        self.interact()
                    elif event.key == pygame.K_j:
                        self.show_journal()
                    elif event.key == pygame.K_SPACE:
                        if hasattr(self.player, 'driving') and self.player.driving:
                            self.player.driving.driver = None
                            self.player.driving = None
                            self.show_message_and_wait("You exit the vehicle.")
                            self.add_journal_entry("Exited vehicle")
            
            # Handle movement with cooldown
            if move_cooldown <= 0:
                keys = pygame.key.get_pressed()
                dx, dy = 0, 0
                
                # Numpad movement
                if keys[pygame.K_KP8] or keys[pygame.K_UP]: dy = -1
                if keys[pygame.K_KP2] or keys[pygame.K_DOWN]: dy = 1
                if keys[pygame.K_KP4] or keys[pygame.K_LEFT]: dx = -1
                if keys[pygame.K_KP6] or keys[pygame.K_RIGHT]: dx = 1
                
                # Diagonal movement
                if keys[pygame.K_KP7]: dx, dy = -1, -1
                if keys[pygame.K_KP9]: dx, dy = 1, -1
                if keys[pygame.K_KP1]: dx, dy = -1, 1
                if keys[pygame.K_KP3]: dx, dy = 1, 1
                
                # Wait (numpad 5)
                if keys[pygame.K_KP5]:
                    self.time_system.advance_time()
                    move_cooldown = 5
                    continue
                
                if dx or dy:
                    if hasattr(self.player, 'driving') and self.player.driving:
                        # Handle car movement
                        car = self.player.driving
                        result = car.handle_player_input(dx, dy, self.city.map, self.cars, self.npcs)
                        if isinstance(result, str):  # Hit an NPC
                            self.show_message_and_wait(result)
                            self.add_journal_entry(result)
                        if result:  # Successfully moved
                            self.player.x = car.x
                            self.player.y = car.y
                            move_cooldown = 5  # Faster cooldown for cars
                            self.time_system.advance_time()
                    else:
                        # Normal player movement
                        if self.is_walkable(self.player.x + dx, self.player.y + dy):
                            self.player.move(dx, dy, self.city.map, self.npcs, self.cars)
                            move_cooldown = 10
                            self.time_system.advance_time()
                            
                            # Update NPCs only on player movement (turn-based)
                            for npc in self.npcs:
                                npc.update(self.city.map, self.npcs, self.player, self.cars)

            # Update cooldown
            if move_cooldown > 0:
                move_cooldown -= 1

            # Update game tick (for visual-only updates)
            game_tick += 1
            if game_tick % 30 == 0:  # Every second (at 30 FPS)
                # Update traffic lights (visual only)
                for light in self.traffic_lights:
                    light.update()
                
                # Update AI-controlled cars (visual only)
                for car in self.cars:
                    if not car.driver:  # Only update AI cars
                        car.update(self.cars, self.city.map, self.traffic_lights, self.npcs, self.player.x, self.player.y)

            # Calculate camera position
            camera_x = max(0, min(self.player.x - VIEWPORT_WIDTH // 2, self.city.width - VIEWPORT_WIDTH))
            camera_y = max(0, min(self.player.y - VIEWPORT_HEIGHT // 2, self.city.height - VIEWPORT_HEIGHT))
            
            # Clear screen
            self.screen.fill((0, 0, 0))
            
            # Draw map and entities
            self.draw_map(camera_x, camera_y)
            
            # Draw cars
            self.draw_cars(camera_x, camera_y)
            
            # Draw traffic lights
            for light in self.traffic_lights:
                light.draw(self.screen, camera_x, camera_y)
            
            # Draw NPCs
            for npc in self.npcs:
                npc.draw(self.screen, camera_x, camera_y)
            
            # Draw player (only if not in car)
            if not hasattr(self.player, 'driving') or not self.player.driving:
                self.player.draw(self.screen, camera_x, camera_y)
            
            # Apply lighting based on time of day
            self.time_system.apply_lighting(self.screen)
            
            # Draw HUD
            self.draw_hud()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(30)  # Lock to 30 FPS

    def draw_map(self, camera_x, camera_y):
        for y in range(camera_y, camera_y + VIEWPORT_HEIGHT):
            for x in range(camera_x, camera_x + VIEWPORT_WIDTH):
                screen_x = (x - camera_x) * TILE_SIZE
                screen_y = (y - camera_y) * TILE_SIZE
                tile = self.city.get_tile(x, y)
                
                # Draw terrain
                if tile == TILE_ROAD:
                    # Determine road orientation based on surrounding roads
                    is_vertical = (self.city.get_tile(x, y-1) == TILE_ROAD and 
                                 self.city.get_tile(x, y+1) == TILE_ROAD)
                    is_horizontal = (self.city.get_tile(x-1, y) == TILE_ROAD and 
                                   self.city.get_tile(x+1, y) == TILE_ROAD)
                    
                    if is_vertical and is_horizontal:
                        self.graphics.draw_terrain(self.screen, 'road_intersection', screen_x, screen_y)
                    elif is_vertical:
                        self.graphics.draw_terrain(self.screen, 'road_v', screen_x, screen_y)
                    else:  # Default to horizontal
                        self.graphics.draw_terrain(self.screen, 'road_h', screen_x, screen_y)
                elif tile == TILE_PARK:
                    self.graphics.draw_terrain(self.screen, 'grass', screen_x, screen_y)
                elif tile == TILE_BUILDING:
                    self.graphics.draw_terrain(self.screen, 'building', screen_x, screen_y)
                elif tile == TILE_TREE:
                    self.graphics.draw_terrain(self.screen, 'tree', screen_x, screen_y)
                elif tile == TILE_POND:
                    self.graphics.draw_terrain(self.screen, 'water', screen_x, screen_y)
                elif tile == TILE_GRASS:
                    self.graphics.draw_terrain(self.screen, 'grass', screen_x, screen_y)
                elif tile == TILE_FLOOR:
                    self.graphics.draw_terrain(self.screen, 'floor', screen_x, screen_y)
                elif tile == TILE_DOOR:
                    self.graphics.draw_terrain(self.screen, 'door', screen_x, screen_y)
                elif tile == TILE_WINDOW:
                    self.graphics.draw_terrain(self.screen, 'window', screen_x, screen_y)
                
                # Draw prop if present
                prop = self.city.props.get((x, y))
                if prop:
                    self.graphics.draw_natural_prop(self.screen, prop, screen_x, screen_y)
                
                # Draw furniture with proper sprites and states
                furniture_map = {
                    TILE_TOILET: 'toilet',
                    TILE_OVEN: 'oven',
                    TILE_BED: 'bed',
                    TILE_DESK: 'desk',
                    TILE_SHOP_SHELF: 'shop_shelf',
                    TILE_TABLE: 'table',
                    TILE_FRIDGE: 'fridge',
                    TILE_COUNTER: 'counter',
                    TILE_SINK: 'sink',
                    TILE_TUB: 'tub'
                }
                
                if tile in furniture_map:
                    state = self.furniture_state.get((x, y), {}).get('state', 'normal')
                    self.graphics.draw_furniture(
                        self.screen,
                        furniture_map[tile],
                        screen_x,
                        screen_y,
                        state
                    )

    def draw_cars(self, camera_x, camera_y):
        """Draw all cars with proper sprites."""
        for car in self.cars:
            screen_x = (car.x - camera_x) * TILE_SIZE
            screen_y = (car.y - camera_y) * TILE_SIZE
            
            self.graphics.draw_car(
                self.screen,
                car.type,
                screen_x,
                screen_y,
                car.direction,
                car.hp < car.max_hp
            )

    def is_walkable(self, x, y):
        """Check if a tile is walkable."""
        # First check walkability overrides
        if hasattr(self.city, '_walkability_overrides') and (x, y) in self.city._walkability_overrides:
            return self.city._walkability_overrides[(x, y)]
            
        tile = self.city.get_tile(x, y)
        walkable_tiles = [TILE_FLOOR, TILE_ROAD, TILE_GRASS, TILE_PARK]
        if tile in walkable_tiles:
            return True
        if tile == TILE_DOOR:
            # Check door state in furniture_state
            door_state = self.furniture_state.get((x, y), {}).get('state', 'closed')
            return door_state == 'open'
        return False

    def get_furniture_at(self, x, y):
        tile = self.city.get_tile(x, y)
        furniture_names = {
            TILE_TOILET: "Toilet",
            TILE_OVEN: "Oven",
            TILE_BED: "Bed",
            TILE_DESK: "Desk",
            TILE_SHOP_SHELF: "Shop Shelf",
            TILE_TABLE: "Table",
            TILE_FRIDGE: "Fridge",
            TILE_COUNTER: "Counter",
            TILE_SINK: "Sink",
            TILE_TUB: "Tub"
        }
        if tile in furniture_names:
            state = self.furniture_state.get((x, y), {'state': 'normal'})['state']
            return furniture_names[tile], state
        return None, None

    def interact(self):
        self.debug("Player interaction triggered.")
        facing = [(0,-1),(0,1),(-1,0),(1,0)]
        for dx, dy in facing:
            tx, ty = self.player.x + dx, self.player.y + dy
            
            # Check for doors and windows first
            tile = self.city.get_tile(tx, ty)
            if tile == TILE_DOOR or tile == TILE_WINDOW:
                if tile == TILE_DOOR:
                    actions = ["Open/Close", "Inspect", "Cancel"]
                    choice = self.show_menu_and_wait(f"Interact with door:", actions)
                    if actions[choice] == "Open/Close":
                        self.toggle_door_window(tx, ty, tile, 'open')
                        self.show_message_and_wait(f"You {self.furniture_state.get((tx, ty), {}).get('state', 'closed')} the door.")
                    elif actions[choice] == "Inspect":
                        self.show_message_and_wait("A sturdy door.")
                elif tile == TILE_WINDOW:
                    actions = ["Peek", "Break", "Cancel"]
                    choice = self.show_menu_and_wait(f"Interact with window:", actions)
                    if actions[choice] == "Peek":
                        self.show_message_and_wait("You peek through the window.")
                    elif actions[choice] == "Break":
                        self.furniture_state[(tx, ty)] = {'type': tile, 'state': 'broken'}
                        self.show_message_and_wait("You smash the window!")
                return
            
            # Check for cars first
            car = next((c for c in self.cars if (tx, ty) in c.get_tiles()), None)
            if car:
                actions = ["Hijack", "Smash", "Inspect", "Enter", "Cancel"]
                choice = self.show_menu_and_wait(f"Interact with {car.type.title()} car:", actions)
                
                if actions[choice] == "Hijack":
                    if not hasattr(self.player, 'driving'):
                        # 50% chance to successfully hijack
                        if random.random() < 0.5:
                            self.player.driving = car
                            car.hijacked = True
                            car.driver = self.player
                            msg = f"You successfully hijack the {car.type} car!"
                            self.add_journal_entry(msg)
                        else:
                            msg = "You fail to hijack the car!"
                        self.show_message_and_wait(msg)
                    else:
                        self.show_message_and_wait("You're already in a car!")
                
                elif actions[choice] == "Smash":
                    # Choose random car part
                    parts = ["windshield", "headlights", "hood", "door", "trunk", "tires", "engine"]
                    target = random.choice(parts)
                    damage = random.randint(1, 6)
                    car.hp -= damage
                    msg = car_combat_message(damage, target, car.hp)
                    self.show_message_and_wait(msg)
                    self.add_journal_entry(f"Damaged {car.type} car's {target}")
                
                elif actions[choice] == "Inspect":
                    status = "wrecked" if car.hp <= 0 else "damaged" if car.hp < car.max_hp else "pristine"
                    msg = f"A {car.type} car in {status} condition. "
                    if hasattr(car, 'hijacked') and car.hijacked:
                        msg += "The ignition has been hotwired."
                    self.show_message_and_wait(msg)
                
                elif actions[choice] == "Enter":
                    if not hasattr(self.player, 'driving'):
                        if car.hp > 0:
                            self.player.driving = car
                            car.driver = self.player
                            msg = f"You enter the {car.type} car."
                            self.add_journal_entry(msg)
                        else:
                            msg = "This car is too damaged to drive!"
                        self.show_message_and_wait(msg)
                    else:
                        self.show_message_and_wait("You're already in a car!")
                
                return
            
            # Check for NPCs next
            npc = next((n for n in self.npcs if n.x == tx and n.y == ty), None)
            if npc:
                if npc.is_dead:
                    # Special menu for dead NPCs
                    actions = ["Dismember", "Decapitate", "Eviscerate", "Incinerate", "Desecrate", "Inspect", "Cancel"]
                    choice = self.show_menu_and_wait(f"Interact with {npc.name}'s corpse:", actions)
                    
                    if actions[choice] == "Dismember":
                        limb = random.choice(["arms", "legs", "torso"])
                        msg = f"You violently tear {npc.name}'s {limb} apart in a shower of gore!"
                        self.show_message_and_wait(msg)
                        self.add_journal_entry(f"Dismembered {npc.name}'s {limb}")
                        
                    elif actions[choice] == "Decapitate":
                        msg = f"You sever {npc.name}'s head clean off! Their lifeless eyes stare blankly into the void."
                        self.show_message_and_wait(msg)
                        self.add_journal_entry(f"Decapitated {npc.name}'s corpse")
                        
                    elif actions[choice] == "Eviscerate":
                        organs = random.choice(["intestines", "liver", "lungs", "heart"])
                        msg = f"You brutally rip out {npc.name}'s {organs} in a horrific display of violence!"
                        self.show_message_and_wait(msg)
                        self.add_journal_entry(f"Eviscerated {npc.name}, removing their {organs}")
                        
                    elif actions[choice] == "Incinerate":
                        msg = f"You set {npc.name}'s corpse ablaze! The smell of burning flesh fills the air as their remains turn to ash."
                        self.show_message_and_wait(msg)
                        self.add_journal_entry(f"Incinerated {npc.name}'s remains")
                        # Remove the NPC from the game
                        self.npcs.remove(npc)
                        
                    elif actions[choice] == "Desecrate":
                        acts = [
                            f"carve obscene symbols into {npc.name}'s flesh",
                            f"arrange {npc.name}'s limbs into an unnatural pose",
                            f"paint ritual markings using {npc.name}'s blood",
                            f"stack rocks in a disturbing pattern around {npc.name}'s corpse"
                        ]
                        act = random.choice(acts)
                        msg = f"You {act}, defiling their remains in a macabre display."
                        self.show_message_and_wait(msg)
                        self.add_journal_entry(f"Desecrated {npc.name}'s corpse: {act}")
                        
                    elif actions[choice] == "Inspect":
                        injuries = ', '.join(f"{part} ({info['type']})" for part, info in npc.injuries.items())
                        cause = "unknown causes" if not injuries else f"injuries to their {injuries}"
                        msg = f"{npc.name}'s lifeless body shows signs of {cause}. Their cold flesh has begun to stiffen with rigor mortis."
                        self.show_message_and_wait(msg)
                        self.add_journal_entry(f"Inspected {npc.name}'s corpse")
                    
                    return
                    
                elif npc.is_knocked_out:
                    # Special menu for knocked out NPCs
                    actions = ["Finish Off", "Draw On Face", "Rob", "Help Up", "Inspect", "Cancel"]
                    choice = self.show_menu_and_wait(f"Interact with unconscious {npc.name}:", actions)
                    if actions[choice] == "Finish Off":
                        from stinkworld.combat.injuries import BODY_PARTS
                        from stinkworld.combat.messages import npc_combat_message
                        target_part = random.choice(BODY_PARTS)
                        msg = npc_combat_message(999, target_part, 0, npc.name, fatal=True)
                        self.show_message_and_wait(msg)
                        npc.hp = 0
                        npc.is_dead = True
                        npc.is_knocked_out = False
                        self.add_journal_entry(f"Finished off {npc.name} with a fatal blow to the {target_part}")
                    elif actions[choice] == "Draw On Face":
                        if not hasattr(npc, 'vandalized'):
                            npc.vandalized = True
                            npc.appearance['graffiti'] = random.choice([
                                "mustache", "glasses", "beard", "clown makeup", 
                                "rude words", "funny face", "black eye"
                            ])
                            self.show_message_and_wait(f"You draw {npc.appearance['graffiti']} on {npc.name}'s face.")
                            self.add_journal_entry(f"Drew {npc.appearance['graffiti']} on {npc.name}'s face")
                            npc.add_memory("vandalized", self.turn, {"description": "Had face drawn on while unconscious"})
                        else:
                            self.show_message_and_wait(f"{npc.name}'s face is already decorated with {npc.appearance['graffiti']}.")
                    elif actions[choice] == "Rob":
                        if not hasattr(npc, 'robbed'):
                            npc.robbed = True
                            self.show_message_and_wait(f"You take {npc.name}'s valuables while they're unconscious.")
                            self.add_journal_entry(f"Robbed {npc.name} while unconscious")
                            npc.add_memory("robbed", self.turn, {"description": "Was robbed while unconscious"})
                        else:
                            self.show_message_and_wait(f"You've already taken everything from {npc.name}.")
                    elif actions[choice] == "Help Up":
                        npc.is_knocked_out = False
                        npc.hp = npc.max_hp // 2
                        self.show_message_and_wait(f"You help {npc.name} back to their feet. They seem grateful.")
                        self.add_journal_entry(f"Helped {npc.name} regain consciousness")
                        npc.add_memory("helped", self.turn, {"description": "Was helped while unconscious"})
                        npc.relationship += 25
                    elif actions[choice] == "Inspect":
                        desc = npc.get_description()
                        self.show_message_and_wait(desc, True, npc.appearance)
                        self.add_journal_entry(f"Inspected unconscious {npc.name}")
                    return
                
                # Regular NPC interaction menu
                actions = ["Talk", "Fight", "Inspect", "Give Gift", "Insult", "Trade", "Cancel"]
                choice = self.show_menu_and_wait(f"Interact with {npc.name}:", actions)
                if actions[choice] == "Talk":
                    # Get conversation from NPC
                    conversation = npc.start_conversation()
                    prompt = conversation["prompt"]
                    responses = conversation["responses"]
                    
                    # Show the NPC's question/prompt
                    self.show_message_and_wait(f"{npc.name} asks: '{prompt}'", True, npc.appearance)
                    
                    # Show possible responses
                    response_options = [resp[0] for resp in responses]  # Get just the response texts
                    response_options.append("(Leave conversation)")
                    
                    # Let player choose response
                    choice = self.show_menu_and_wait("How do you respond?", response_options)
                    
                    if choice < len(responses):  # If not "Leave conversation"
                        chosen_response, reaction = responses[choice]
                        # Show the reaction
                        reaction = reaction.format(name=npc.name)
                        self.show_message_and_wait(reaction, True, npc.appearance)
                        # Add memory of chat
                        npc.add_memory("chat", self.turn, {"description": f"Had a conversation about {prompt}"})
                        self.add_journal_entry(f"Talked to {npc.name} about {prompt}")
                    else:
                        self.show_message_and_wait(f"You end the conversation with {npc.name}.")
                        self.add_journal_entry(f"Ended conversation with {npc.name}")
                    
                elif actions[choice] == "Fight":
                    self.start_combat(npc)
                elif actions[choice] == "Inspect":
                    desc = npc.get_description()
                    self.show_message_and_wait(desc, True, npc.appearance)
                    self.add_journal_entry(f"Inspected {npc.name}")
                elif actions[choice] == "Give Gift":
                    npc.add_memory("gift", self.turn, {"description": "Received a gift"})
                    self.show_message_and_wait(f"You gave a gift to {npc.name}. They seem pleased!", True, npc.appearance)
                    self.add_journal_entry(f"Gave a gift to {npc.name}")
                elif actions[choice] == "Insult":
                    npc.add_memory("insulted", self.turn, {"description": "Was insulted"})
                    self.show_message_and_wait(f"You insulted {npc.name}. They look angry!", True, npc.appearance)
                    self.add_journal_entry(f"Insulted {npc.name}")
                elif actions[choice] == "Trade":
                    self.trade_with_npc(npc)
                return
            
            # Check for shops
            shop_name = self.city.get_shop_at(tx, ty)
            if shop_name:
                self.show_shop_menu(shop_name)
                return
            
            # Then check for furniture
            fname, state = self.get_furniture_at(tx, ty)
            if fname:
                # Show furniture interaction menu
                actions = ["Use", "Move", "Break", "Vandalize", "Inspect", "Cancel"]
                choice = self.show_menu_and_wait(f"Interact with {fname} (state: {state}):", actions)
                if actions[choice] == "Use":
                    self.use_furniture(tx, ty, fname, state)
                elif actions[choice] == "Move":
                    self.move_furniture(tx, ty, fname, state)
                elif actions[choice] == "Break":
                    self.break_furniture(tx, ty, fname, state)
                elif actions[choice] == "Vandalize":
                    self.vandalize_furniture(tx, ty, fname, state)
                elif actions[choice] == "Inspect":
                    self.inspect_furniture(tx, ty, fname, state)
                return
        
        self.show_message_and_wait("There's nothing to interact with.")

    def add_journal_entry(self, text):
        self.debug(f"Journal entry: {text}")
        """Add an entry to the player's journal with the current in-game day."""
        # Get the current in-game day
        current_day = self.time_system.get_current_day()
        entry = f"[Day {current_day}] {text}"
        self.player.journal.append(entry)

    def use_furniture(self, x, y, fname, state):
        flavor = {
            "Bed": "You take a quick nap. You feel a bit better.",
            "Toilet": "You use the toilet. Relief!",
            "Sink": "You wash your hands. Hygiene is important!",
            "Fridge": "You rummage for snacks. Maybe something edible...",
            "Oven": "You try to cook, but there's nothing to cook.",
            "Desk": "You sit and ponder your next move.",
            "Shop Shelf": "You browse the shelves. Nothing useful.",
            "Table": "You rest at the table for a moment.",
            "Counter": "You lean on the counter, looking cool.",
            "Tub": "You take a quick bath. Refreshed!"
        }
        msg = flavor.get(fname, f"You use the {fname}.")
        self.add_journal_entry(f"Used {fname} at ({x}, {y})")
        self.show_message_and_wait(msg)

    def move_furniture(self, x, y, fname, state):
        if state == 'moved':
            self.show_message_and_wait(f"The {fname} is already moved.")
            return
        self.furniture_state[(x, y)] = {'state': 'moved'}
        self.add_journal_entry(f"Moved {fname} at ({x}, {y})")
        self.show_message_and_wait(f"You push the {fname} aside. You can now walk through that space.")

    def break_furniture(self, x, y, fname, state):
        if state == 'broken':
            self.show_message_and_wait(f"The {fname} is already broken.")
            return
        self.furniture_state[(x, y)] = {'state': 'broken'}
        self.add_journal_entry(f"Broke {fname} at ({x}, {y})")
        self.show_message_and_wait(f"You smash the {fname}! It's now broken and useless.")

    def vandalize_furniture(self, x, y, fname, state):
        if state == 'vandalized':
            self.show_message_and_wait(f"The {fname} is already vandalized.")
            return
        self.furniture_state[(x, y)] = {'state': 'vandalized'}
        self.add_journal_entry(f"Vandalized {fname} at ({x}, {y})")
        self.show_message_and_wait(f"You spray paint rude words on the {fname}. It's now vandalized.")

    def inspect_furniture(self, x, y, fname, state):
        descs = {
            'normal': f"A standard {fname}.",
            'moved': f"The {fname} has been pushed aside.",
            'broken': f"The {fname} is broken and useless.",
            'vandalized': f"The {fname} is covered in graffiti."
        }
        desc = descs.get(state, f"A {fname}.")
        self.add_journal_entry(f"Inspected {fname} at ({x}, {y}) [{state}]")
        self.show_message_and_wait(desc)

    def show_menu_and_wait(self, prompt, options):
        font = pygame.font.SysFont(None, 32)
        selected = 0
        while True:
            self.screen.fill((0,0,0))
            txt = font.render(prompt, True, (255,255,0))
            self.screen.blit(txt, (40, 40))
            for i, opt in enumerate(options):
                color = (255,255,255) if i == selected else (180,180,180)
                opt_txt = font.render(opt, True, color)
                self.screen.blit(opt_txt, (60, 120 + i*40))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return selected

    def show_journal(self):
        self.debug("Journal opened.")
        font = pygame.font.SysFont(None, 32)
        bigfont = pygame.font.SysFont(None, 44)
        scroll = 0
        lines = self.player.journal if self.player.journal else ["(Your journal is empty.)"]
        while True:
            self.screen.fill((0,0,0))
            title = bigfont.render("Journal", True, (255,255,0))
            self.screen.blit(title, (40, 20))
            for i, entry in enumerate(lines[scroll:scroll+12]):
                txt = font.render(entry, True, (255,255,255))
                self.screen.blit(txt, (60, 80 + i*32))
            inst = font.render("Up/Down: Scroll  Esc: Close", True, (180,180,180))
            self.screen.blit(inst, (40, 500))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_UP:
                        scroll = max(0, scroll-1)
                    elif event.key == pygame.K_DOWN:
                        if scroll < max(0, len(lines)-12):
                            scroll += 1

    def show_stats_menu(self):
        self.debug("Stats menu opened.")
        """Show the player stats and inventory menu."""
        font = pygame.font.SysFont(None, 32)
        bigfont = pygame.font.SysFont(None, 44)
        
        # Stats page
        STATS_PAGE = 0
        # Inventory page
        INVENTORY_PAGE = 1
        # Journal page
        JOURNAL_PAGE = 2
        
        current_page = STATS_PAGE
        scroll = 0
        
        while True:
            self.screen.fill((0, 0, 0))
            
            # Draw title
            if current_page == STATS_PAGE:
                title = bigfont.render("Character Stats", True, (255, 255, 0))
            elif current_page == INVENTORY_PAGE:
                title = bigfont.render("Inventory", True, (255, 255, 0))
            else:
                title = bigfont.render("Journal", True, (255, 255, 0))
            self.screen.blit(title, (40, 20))
            
            y = 80
            
            if current_page == STATS_PAGE:
                # Basic Stats
                stats_text = [
                    f"Name: {self.player.name}",
                    f"HP: {self.player.hp}/{self.player.max_hp}",
                    "",
                    "Combat Stats:",
                    f"Strength: {self.player.strength}",
                    f"Defense: {self.player.defense}",
                    f"Speed: {self.player.speed}",
                    "",
                    "Mental Stats:",
                    f"Street Smarts: {self.player.street_smarts}",
                    f"Book Smarts: {self.player.book_smarts}",
                    "",
                    "Points: {self.player.points}",
                    "",
                    "Active Effects:"
                ]
                
                # Add injuries if any
                if self.player.injuries:
                    for part, info in self.player.injuries.items():
                        stats_text.append(f"- {part}: {info['type']} ({info['turns']} turns left)")
                else:
                    stats_text.append("None")
                
                for line in stats_text:
                    text = font.render(line, True, (255, 255, 255))
                    self.screen.blit(text, (60, y))
                    y += 30
            
            elif current_page == INVENTORY_PAGE:
                if self.player.inventory:
                    for item in self.player.inventory[scroll:scroll+12]:
                        text = font.render(f"- {item}", True, (255, 255, 255))
                        self.screen.blit(text, (60, y))
                        y += 30
                else:
                    text = font.render("(Inventory is empty)", True, (180, 180, 180))
                    self.screen.blit(text, (60, y))
            
            else:  # Journal page
                if self.player.journal:
                    for entry in self.player.journal[scroll:scroll+12]:
                        text = font.render(entry, True, (255, 255, 255))
                        self.screen.blit(text, (60, y))
                        y += 30
                else:
                    text = font.render("(Journal is empty)", True, (180, 180, 180))
                    self.screen.blit(text, (60, y))
            
            # Draw controls
            controls = [
                "Tab: Switch Page",
                "Up/Down: Scroll",
                "Esc: Close"
            ]
            y = self.screen.get_height() - 100
            for control in controls:
                text = font.render(control, True, (180, 180, 180))
                self.screen.blit(text, (40, y))
                y += 30
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_TAB:
                        current_page = (current_page + 1) % 3
                        scroll = 0
                    elif event.key == pygame.K_UP:
                        scroll = max(0, scroll - 1)
                    elif event.key == pygame.K_DOWN:
                        if current_page == INVENTORY_PAGE and scroll < len(self.player.inventory) - 12:
                            scroll += 1
                        elif current_page == JOURNAL_PAGE and scroll < len(self.player.journal) - 12:
                            scroll += 1

    def draw_hud(self):
        # Draw HUD at the bottom of the screen
        font = pygame.font.SysFont(None, 24)
        
        # Player stats
        hp_text = f"HP: {self.player.hp}/{self.player.max_hp}"
        hp_surface = font.render(hp_text, True, (255, 255, 255))
        self.screen.blit(hp_surface, (10, self.screen.get_height() - 80))
        
        # Time and date
        time_text = f"Time: {self.time_system.format_time()}"
        time_surface = font.render(time_text, True, (255, 255, 255))
        self.screen.blit(time_surface, (10, self.screen.get_height() - 60))
        
        date_text = f"Date: {self.time_system.format_date()}"
        date_surface = font.render(date_text, True, (255, 255, 255))
        self.screen.blit(date_surface, (10, self.screen.get_height() - 40))
        
        # Player position
        pos_text = f"Pos: ({self.player.x}, {self.player.y})"
        pos_surface = font.render(pos_text, True, (255, 255, 255))
        self.screen.blit(pos_surface, (10, self.screen.get_height() - 20))
        
        # Controls reminder - changes based on if player is in a car
        if hasattr(self.player, 'driving') and self.player.driving:
            car_type = self.player.driving.type
            controls_text = f"SPACE: Exit {car_type}  WASD: Drive  E: Interact  J: Journal  ESC: Menu"
            # Draw car status
            car_hp = self.player.driving.hp
            car_max_hp = self.player.driving.max_hp
            car_status = f"Vehicle: {car_type} ({car_hp}/{car_max_hp} HP)"
            car_status_surface = font.render(car_status, True, (255, 255, 0))
            self.screen.blit(car_status_surface, (self.screen.get_width() - 300, self.screen.get_height() - 40))
        else:
            controls_text = "E: Interact  J: Journal  WASD: Move  ESC: Menu"
        
        controls_surface = font.render(controls_text, True, (180, 180, 180))
        self.screen.blit(controls_surface, (self.screen.get_width() - 300, self.screen.get_height() - 20))

    def show_high_scores(self):
        self.debug("High scores viewed.")
        font = pygame.font.SysFont(None, 36)
        self.screen.fill((0,0,0))
        txt = font.render("High Scores (Press any key)", True, (255,255,255))
        self.screen.blit(txt, (40, 100))
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    waiting = False

    @staticmethod
    def generate_npc_description_static(*args, **kwargs):
        return "A mysterious stranger."

    def show_message_and_wait(self, msg, show_portrait=False, portrait_data=None):
        self.debug(f"Show message: {msg}")
        font = pygame.font.SysFont(None, 32)
        self.screen.fill((0,0,0))
        
        # If showing a portrait
        if show_portrait and portrait_data:
            # Draw portrait on the left side
            portrait_surface = pygame.Surface((100, 100))
            portrait_surface.fill((0, 0, 0))
            draw_portrait(portrait_surface, 0, 0, 100, portrait_data)
            self.screen.blit(portrait_surface, (40, 40))
            
            # Draw text to the right of portrait
            lines = msg.split('\n')
            y = 40
            for line in lines:
                # Wrap text to fit screen width
                words = line.split()
                line_buffer = []
                for word in words:
                    line_buffer.append(word)
                    test_line = ' '.join(line_buffer)
                    test_surface = font.render(test_line, True, (255,255,255))
                    if test_surface.get_width() > self.screen.get_width() - 160:  # Account for portrait
                        # Draw the line without the last word
                        line_buffer.pop()
                        final_line = ' '.join(line_buffer)
                        txt = font.render(final_line, True, (255,255,255))
                        self.screen.blit(txt, (160, y))  # Start text after portrait
                        y += 32
                        line_buffer = [word]
                
                # Draw remaining words
                if line_buffer:
                    final_line = ' '.join(line_buffer)
                    txt = font.render(final_line, True, (255,255,255))
                    self.screen.blit(txt, (160, y))
                    y += 32
        else:
            # Regular message display without portrait
            lines = msg.split('\n')
            y = 40
            for line in lines:
                # Wrap text to fit screen width
                words = line.split()
                line_buffer = []
                for word in words:
                    line_buffer.append(word)
                    test_line = ' '.join(line_buffer)
                    test_surface = font.render(test_line, True, (255,255,255))
                    if test_surface.get_width() > self.screen.get_width() - 80:
                        # Draw the line without the last word
                        line_buffer.pop()
                        final_line = ' '.join(line_buffer)
                        txt = font.render(final_line, True, (255,255,255))
                        self.screen.blit(txt, (40, y))
                        y += 32
                        line_buffer = [word]
                
                # Draw remaining words
                if line_buffer:
                    final_line = ' '.join(line_buffer)
                    txt = font.render(final_line, True, (255,255,255))
                    self.screen.blit(txt, (40, y))
                    y += 32
        
        inst = font.render("Press any key...", True, (180,180,180))
        self.screen.blit(inst, (40, self.screen.get_height() - 60))
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    waiting = False

    def start_combat(self, npc):
        self.debug(f"Combat started with NPC: {npc.name}")
        from stinkworld.combat.injuries import BODY_PARTS, add_injury, process_injuries, INJURY_TYPES
        from stinkworld.combat.messages import npc_combat_message
        player = self.player
        if not hasattr(player, "injuries"):
            player.injuries = {}
        if not hasattr(npc, "injuries"):
            npc.injuries = {}
        self.add_journal_entry(f"You started a fight with {npc.name}!")
        combat_over = False
        while not combat_over:
            # Process injuries for both
            p_bleed, p_limp, p_bleed_amt = process_injuries(player)
            n_bleed, n_limp, n_bleed_amt = process_injuries(npc)

            # Show HP and injuries
            status = (
                f"Your HP: {player.hp}/{player.max_hp} | "
                f"Injuries: {', '.join([f'{k}({v['type']})' for k,v in player.injuries.items()]) or 'None'}"
                f"{' | Bleeding!' if p_bleed else ''}{' | Limping!' if p_limp else ''}\n"
                f"{npc.name} HP: {npc.hp}/10 | "
                f"Injuries: {', '.join([f'{k}({v['type']})' for k,v in npc.injuries.items()]) or 'None'}"
                f"{' | Bleeding!' if n_bleed else ''}{' | Limping!' if n_limp else ''}"
            )
            self.show_message_and_wait(status)
            self.add_journal_entry(f"Combat status: {status.replace(chr(10), ' | ')}")

            # Player turn
            actions = ["Punch", "Kick", "Targeted Attack", "Taunt", "Flee"]
            while True:
                choice = self.show_menu_and_wait("Choose your action:", actions)
                if actions[choice] == "Flee":
                    self.message_to_show = "You run away!"
                    self.add_journal_entry(f"You fled from combat with {npc.name}.")
                    combat_over = True
                    break
                elif actions[choice] == "Targeted Attack":
                    part_idx = self.show_menu_and_wait("Target which body part?", BODY_PARTS)
                    target_part = BODY_PARTS[part_idx]
                    attack_type = "targeted"
                    break
                elif actions[choice] == "Taunt":
                    taunts = [
                        "You're slower than a parked car!",
                        "Is that all you've got?",
                        "I've seen puddles with more fight than you!",
                        "You call that a punch? My grandma hits harder!",
                        "You're about as sharp as a marble!",
                        "Did you forget your brain at home today?",
                        "You're not even worth my time!",
                        "You look like you lost a fight with a mop!",
                        "I've met friendlier rats in the sewer!",
                        "You couldn't win a staring contest with a goldfish!",
                        "You fight like a dairy farmer!",
                        "Your breath could knock out a skunk!",
                        "I've seen bread with more backbone!",
                        "You look like you eat soup with a fork!",
                        "You're about as scary as a kitten in a tutu!",
                        "If brains were dynamite, you couldn't blow your nose!",
                        "You're the reason the gene pool needs a lifeguard!",
                        "You couldn't pour water out of a boot with instructions on the heel!",
                        "You're the human equivalent of a participation trophy!",
                        "If I wanted to hear from you, I'd rattle your cage!"
                    ]
                    taunt = random.choice(taunts)
                    if not hasattr(npc, 'taunted') or not npc.taunted:
                        npc.strength = max(1, getattr(npc, 'strength', 5) - 2)
                        npc.defense = max(0, getattr(npc, 'defense', 2) - 1)
                        npc.taunted = True
                        debuff_msg = f"{npc.name}'s strength and defense are lowered!"
                    else:
                        debuff_msg = f"{npc.name} is already demoralized."
                    self.show_message_and_wait(f"You taunt {npc.name}: '{taunt}'\n{debuff_msg}")
                    self.add_journal_entry(f"You taunted {npc.name}: '{taunt}' {debuff_msg}")
                    continue
                else:
                    target_part = random.choice(BODY_PARTS)
                    attack_type = actions[choice].lower()
                    break

            if actions[choice] == "Flee":
                break

            # Calculate hit/miss/crit
            hit_roll = random.random()
            if hit_roll < 0.1:
                self.show_message_and_wait("You miss!")
                self.add_journal_entry(f"You missed {npc.name}.")
            else:
                crit = hit_roll > 0.95
                base_damage = player.strength + random.randint(0, player.street_smarts)
                damage = base_damage * (2 if crit else 1)
                # Injury logic
                injury = None
                if attack_type == "targeted" or crit or damage > 6:
                    if damage > 12 or crit:
                        injury_type = random.choice(["fracture", "deep wound"])
                    elif damage > 8:
                        injury_type = random.choice(["sprain", "cut"])
                    else:
                        injury_type = "bruise"
                    add_injury(npc, target_part, injury_type)
                    injury = f" and cause a {injury_type} to their {target_part}!"
                    self.add_journal_entry(f"You injured {npc.name}'s {target_part} with a {injury_type}.")
                npc.hp -= damage
                msg = f"You {attack_type} {npc.name}'s {target_part} for {damage} damage"
                if injury:
                    msg += injury
                if crit:
                    msg += " (Critical!)"
                self.show_message_and_wait(msg)
                self.add_journal_entry(msg)
                if npc.hp <= 0:
                    self.show_message_and_wait(f"{npc.name} is knocked out!")
                    self.add_journal_entry(f"You knocked out {npc.name}!")
                    npc.is_knocked_out = True
                    combat_over = True
                    break

            # NPC turn (skip if KO)
            if npc.hp > 0:
                npc_action = random.choice(["punch", "kick", "target"])
                if npc_action == "target":
                    npc_part = random.choice(BODY_PARTS)
                    npc_msg = f"{npc.name} targets your {npc_part}!"
                else:
                    npc_part = random.choice(BODY_PARTS)
                    npc_msg = f"{npc.name} tries to {npc_action} you!"
                hit_roll = random.random()
                if hit_roll < 0.1:
                    self.show_message_and_wait(npc_msg + " But they miss!")
                    self.add_journal_entry(f"{npc.name} missed you.")
                else:
                    crit = hit_roll > 0.95
                    base_damage = npc.strength + random.randint(0, npc.speed)
                    damage = base_damage * (2 if crit else 1)
                    injury = None
                    if npc_action == "target" or crit or damage > 6:
                        if damage > 12 or crit:
                            injury_type = random.choice(["fracture", "deep wound"])
                        elif damage > 8:
                            injury_type = random.choice(["sprain", "cut"])
                        else:
                            injury_type = "bruise"
                        add_injury(player, npc_part, injury_type)
                        injury = f" and causes a {injury_type} to your {npc_part}!"
                        self.add_journal_entry(f"{npc.name} injured your {npc_part} with a {injury_type}.")
                    player.hp -= damage
                    msg = f"{npc.name} hits your {npc_part} for {damage} damage"
                    if injury:
                        msg += injury
                    if crit:
                        msg += " (Critical!)"
                    self.show_message_and_wait(msg)
                    self.add_journal_entry(msg)
                    if player.hp <= 0:
                        self.show_message_and_wait("You are knocked out!")
                        self.add_journal_entry(f"You were knocked out by {npc.name}!")
                        self.player_is_knocked_out = True
                        combat_over = True
                        break
        self.add_journal_entry(f"Combat with {npc.name} ended.")

    def generate_npc_response(self, npc):
        responses = {
            "friendly": [
                "Hello! Nice to meet you!",
                "What a wonderful day!",
                "I'm always happy to chat!",
                "You seem like a nice person!",
                "Let's be friends!"
            ],
            "grumpy": [
                "What do you want?",
                "Leave me alone...",
                "I'm not in the mood.",
                "Make it quick.",
                "*grumbles*"
            ],
            "timid": [
                "Oh! Um... hi...",
                "Please don't hurt me...",
                "I should go...",
                "*nervous laugh*",
                "Is everything okay?"
            ],
            "aggressive": [
                "Watch yourself!",
                "You looking for trouble?",
                "Better back off!",
                "What's your problem?",
                "Keep walking!"
            ],
            "chatty": [
                "Oh my gosh, hi! Let me tell you about my day!",
                "I've been waiting for someone to talk to!",
                "You'll never believe what I just saw!",
                "Have you heard the latest news?",
                "I know all the best gossip!"
            ],
            "quiet": [
                "*nods*",
                "Mhm.",
                "...",
                "*slight wave*",
                "Hey."
            ]
        }
        
        personality = npc.personality
        if npc.relationship <= -50:
            return "I don't want to talk to you!"
        elif npc.relationship <= -20:
            return random.choice(responses["grumpy"])
        elif npc.relationship >= 50:
            return "It's great to see you, friend!"
        else:
            return random.choice(responses.get(personality, ["Hello."]))

    def generate_npc_description(self, npc):
        # Build a detailed description based on NPC attributes
        desc = f"{npc.name} is a {npc.personality} person.\n"
        
        # Appearance
        desc += f"They have {npc.appearance['hair_style']} {npc.appearance['hair_color']} hair "
        desc += f"and {npc.appearance['eye_type']} eyes. "
        desc += f"Their face is {npc.appearance['face_shape']}-shaped. "
        desc += f"They're wearing {npc.appearance['clothes']} clothes.\n"
        
        # Status
        if npc.is_knocked_out:
            desc += "They are currently knocked out.\n"
        elif npc.hp < npc.max_hp // 2:
            desc += "They appear to be injured.\n"
        
        # Injuries
        if npc.injuries:
            injury_desc = ", ".join(f"{part} ({info['type']})" for part, info in npc.injuries.items())
            desc += f"Current injuries: {injury_desc}\n"
        
        # Relationship
        if npc.relationship >= 75:
            desc += "They consider you a close friend.\n"
        elif npc.relationship >= 50:
            desc += "They seem to like you.\n"
        elif npc.relationship >= 25:
            desc += "They're friendly towards you.\n"
        elif npc.relationship <= -75:
            desc += "They hate you.\n"
        elif npc.relationship <= -50:
            desc += "They strongly dislike you.\n"
        elif npc.relationship <= -25:
            desc += "They don't trust you.\n"
        else:
            desc += "They seem neutral towards you.\n"
        
        return desc

    def save_game(self):
        self.debug("Saving game state.")
        """Save the game state to a file."""
        save_data = {
            'player': {
                'x': self.player.x,
                'y': self.player.y,
                'hp': self.player.hp,
                'max_hp': self.player.max_hp,
                'name': self.player.name,
                'journal': self.player.journal,
                'skin_tone': self.player.skin_tone
            },
            'npcs': [{
                'x': npc.x,
                'y': npc.y,
                'hp': npc.hp,
                'max_hp': npc.max_hp,
                'name': npc.name,
                'personality': npc.personality,
                'relationship': npc.relationship,
                'memory': npc.memory,
                'appearance': npc.appearance,
                'injuries': npc.injuries,
                'is_knocked_out': npc.is_knocked_out,
                'is_dead': npc.is_dead
            } for npc in self.npcs],
            'turn': self.turn,
            'furniture_state': self.furniture_state,
            'time_system': {
                'current_turn': self.time_system.current_turn
            }
        }
        
        filename = f"saves/save_{self.turn}.json"
        with open(filename, 'w') as f:
            json.dump(save_data, f)
        return filename

    def load_game(self):
        self.debug("Loading game state.")
        """Load the game state from a file."""
        try:
            with open(f"saves/save_{self.turn}.json", 'r') as f:
                data = json.load(f)
            
            # Recreate game state
            self.player = Player(data['player']['name'])
            self.player.x = data['player']['x']
            self.player.y = data['player']['y']
            self.player.hp = data['player']['hp']
            self.player.max_hp = data['player']['max_hp']
            self.player.journal = data['player']['journal']
            self.player.skin_tone = data['player'].get('skin_tone', (220, 180, 160))
            
            self.npcs = []
            for npc_data in data['npcs']:
                npc = NPC(npc_data['x'], npc_data['y'])
                npc.hp = npc_data['hp']
                npc.max_hp = npc_data['max_hp']
                npc.name = npc_data['name']
                npc.personality = npc_data['personality']
                npc.relationship = npc_data['relationship']
                npc.memory = npc_data['memory']
                npc.appearance = npc_data['appearance']
                npc.injuries = npc_data['injuries']
                npc.is_knocked_out = npc_data['is_knocked_out']
                npc.is_dead = npc_data['is_dead']
                self.npcs.append(npc)
            
            self.turn = data['turn']
            self.furniture_state = data['furniture_state']
            self.city = City()  # Recreate city
            return True
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return False

    def show_save_load_menu(self, is_saving=True):
        """Show the save/load game menu."""
        # Get list of save files
        saves = []
        for i in range(5):  # 5 save slots
            filename = f"saves/save_{i}.json"
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    try:
                        data = json.load(f)
                        saves.append(f"Slot {i}: {data['player']['name']} - Turn {data['turn']}")
                    except:
                        saves.append(f"Slot {i}: Empty")
            else:
                saves.append(f"Slot {i}: Empty")
        
        saves.append("Cancel")
        
        choice = self.show_menu_and_wait(
            "Choose a slot to " + ("save to:" if is_saving else "load from:"),
            saves
        )
        
        if choice < len(saves) - 1:  # Not cancel
            if is_saving:
                filename = self.save_game()
                self.show_message_and_wait(f"Game saved to slot {choice}")
                return True
            else:
                if self.load_game():
                    self.show_message_and_wait(f"Game loaded from slot {choice}")
                    return True
                else:
                    self.show_message_and_wait("Failed to load game!")
                    return False
        return False

    def confirm_menu_exit(self):
        self.debug("Menu exit confirmation shown.")
        """Show confirmation before exiting to menu."""
        actions = ["Save and Exit", "Exit without Saving", "Cancel"]
        choice = self.show_menu_and_wait("Return to main menu?", actions)
        
        if actions[choice] == "Save and Exit":
            if self.show_save_load_menu(is_saving=True):
                self.state = "menu"
        elif actions[choice] == "Exit without Saving":
            choice = self.show_menu_and_wait("Are you sure? All progress will be lost!", ["Yes", "No"])
            if choice == 0:  # Yes
                self.state = "menu"

    def show_shop_menu(self, shop_name):
        self.debug(f"Shop menu opened for: {shop_name}")
        """Show the shop menu with available items."""
        # Get current inventory based on time
        current_hour = self.time_system.get_current_hour()
        inventory = self.economy.get_shop_inventory(shop_name, current_hour)
        
        if not inventory:
            self.show_message_and_wait(f"The {shop_name} is currently closed.")
            return
            
        # Show shop menu
        options = ["Buy", "Sell", "Exit"]
        choice = self.show_menu_and_wait(f"{shop_name} - Your money: {self.player.money} Credits", options)
        
        if options[choice] == "Buy":
            # Show available items
            items = [f"{item['name']} ({item['price']} Credits)" for item in inventory]
            items.append("Cancel")
            item_choice = self.show_menu_and_wait("What would you like to buy?", items)
            
            if item_choice < len(inventory):  # Not cancel
                item = inventory[item_choice]
                success, message = self.economy.buy_item(self.player, shop_name, item['name'], current_hour)
                self.show_message_and_wait(message)
                if success:
                    self.add_journal_entry(f"Bought {item['name']} at {shop_name}")
                    
        elif options[choice] == "Sell":
            if not self.player.inventory:
                self.show_message_and_wait("You have nothing to sell.")
                return
                
            # Show player's inventory
            items = [f"{item}" for item in self.player.inventory]
            items.append("Cancel")
            item_choice = self.show_menu_and_wait("What would you like to sell?", items)
            
            if item_choice < len(self.player.inventory):  # Not cancel
                item_name = self.player.inventory[item_choice]
                success, message = self.economy.sell_item(self.player, shop_name, item_name, current_hour)
                self.show_message_and_wait(message)
                if success:
                    self.add_journal_entry(f"Sold {item_name} at {shop_name}")

    def show_job_menu(self):
        self.debug("Job menu opened.")
        """Show available jobs and let player work."""
        available_jobs = self.economy.get_available_jobs(self.player)
        
        if not available_jobs:
            self.show_message_and_wait("No jobs are available right now.")
            return
            
        # Show job list
        job_names = [f"{job['title']} ({job['salary']} Credits/hr)" for job in available_jobs]
        job_names.append("Cancel")
        choice = self.show_menu_and_wait("Available Jobs:", job_names)
        
        if choice < len(available_jobs):  # Not cancel
            job = available_jobs[choice]
            
            # Ask for hours
            hours_options = ["4 hours", "6 hours", "8 hours", "Cancel"]
            hours_choice = self.show_menu_and_wait(f"How long do you want to work as {job['title']}?", hours_options)
            
            if hours_choice < len(hours_options) - 1:  # Not cancel
                hours = int(hours_options[hours_choice].split()[0])
                pay, effects = self.economy.work_shift(self.player, job['title'], hours)
                
                if isinstance(pay, str):  # Error message
                    self.show_message_and_wait(pay)
                else:
                    # Apply effects
                    self.player.money += pay
                    if hasattr(self.player, 'stress'):
                        self.player.stress += effects['stress']
                    if hasattr(self.player, 'energy'):
                        self.player.energy += effects['energy']
                    if hasattr(self.player, 'reputation'):
                        self.player.reputation += effects['reputation']
                        
                    msg = f"You earned {pay} Credits working as {job['title']}!"
                    self.show_message_and_wait(msg)
                    self.add_journal_entry(msg)
                    
                    # Advance time based on hours worked
                    for _ in range(hours * self.time_system.TURNS_PER_HOUR):
                        self.turn += 1
                        self.time_system.advance_time()

    def show_pause_menu(self):
        """Basic pause menu that shows game options"""
        options = ["Resume", "Settings", "Save Game", "Quit to Menu"]
        choice = self.show_menu_and_wait("Game Paused", options)
        
        if options[choice] == "Quit to Menu":
            self.running = False
        elif options[choice] == "Save Game":
            self.save_game()
            self.show_message_and_wait("Game saved successfully")

    def spawn_npcs(self, count=50):
        """Spawn NPCs in walkable areas."""
        for _ in range(count):
            x, y = self.city.find_walkable_tile()
            if x is not None and y is not None:
                name = random_name()
                npc = NPC(name, x, y)
                self.npcs.append(npc)
                self.debug(f"Spawned NPC {name} at ({x}, {y})")

    def spawn_cars(self, count=3):
        """Spawn cars on roads."""
        for _ in range(count):
            x, y = self.city.find_road_tile()
            if x is not None and y is not None:
                car = Car(x, y)
                self.cars.append(car)
                self.debug(f"Spawned car at ({x}, {y})")