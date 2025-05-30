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
from stinkworld.systems.smart_npc import decide_action, maybe_spread_rumor, handle_player_threat

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
        self.current_tick = 0  # Add tick counter
        
        # Initialize systems
        self.time_system = TimeSystem()
        self.time_system.game = self  # Connect TimeSystem to Game instance
        debug_log(f"[Game] TimeSystem initialized at {hex(id(self.time_system))} | Current time: {self.time_system.get_time_string()}")
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
        self.spawn_cars(30)   # Spawn 30 cars at game start (increased from 12)

        self.init_player()

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
        """Main game loop with 8-directional movement and numpad support."""
        move_cooldown = 0
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
                    elif event.key == pygame.K_SPACE:
                        # Exit car if in car
                        if hasattr(self.player, 'in_car') and self.player.in_car:
                            self.player.in_car.remove_driver()
                            self.show_message_and_wait("You exit the car.")
                    elif event.key == pygame.K_j:
                        self.show_journal()
            # Player Movement (turn-based)
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            wait = False
            if move_cooldown <= 0:
                # 8-directional movement with numpad
                if keys[pygame.K_KP1]:
                    dx, dy = -1, 1
                elif keys[pygame.K_KP2]:
                    dx, dy = 0, 1
                elif keys[pygame.K_KP3]:
                    dx, dy = 1, 1
                elif keys[pygame.K_KP4]:
                    dx, dy = -1, 0
                elif keys[pygame.K_KP6]:
                    dx, dy = 1, 0
                elif keys[pygame.K_KP7]:
                    dx, dy = -1, -1
                elif keys[pygame.K_KP8]:
                    dx, dy = 0, -1
                elif keys[pygame.K_KP9]:
                    dx, dy = 1, -1
                elif keys[pygame.K_KP5]:
                    wait = True
                # Also allow arrow keys for 4-directional movement
                elif keys[pygame.K_UP]:
                    dx, dy = 0, -1
                elif keys[pygame.K_DOWN]:
                    dx, dy = 0, 1
                elif keys[pygame.K_LEFT]:
                    dx, dy = -1, 0
                elif keys[pygame.K_RIGHT]:
                    dx, dy = 1, 0

                if dx or dy:
                    if self.is_walkable(self.player.x + dx, self.player.y + dy):
                        move_result = self.player.move(dx, dy, self.city.map, self.npcs, self.cars)
                        if isinstance(move_result, str):
                            self.show_message_and_wait(move_result)
                        self.time_system.advance_time()  # Only advance time when player moves
                        move_cooldown = 10
                        # Update NPCs (turn-based)
                        for npc in self.npcs:
                            try:
                                npc.update(self.city.map, self.traffic_lights, self.npcs)
                                # --- Modular AI: decide action ---
                                action = decide_action(npc, self)
                                # Example: handle move action (expand as needed)
                                if action['action'] == 'move' and action['target']:
                                    npc.x, npc.y = action['target']
                                # --- Handle player threat if player is nearby and threatening ---
                                if hasattr(npc, 'can_see_player') and npc.can_see_player(self.player):
                                    # Example: check for a threat flag or recent violence (expand as needed)
                                    if getattr(self.player, 'is_threatening', False):
                                        handle_player_threat(npc, self.player, self)
                            except Exception as e:
                                debug_log(f"[Game WARNING] NPC update/AI failed for {getattr(npc, 'npc_id', '?')}: {e}")
                        # --- Rumor system: periodically spread rumors ---
                        try:
                            maybe_spread_rumor(self)
                        except Exception as e:
                            debug_log(f"[Game WARNING] RumorMill failed: {e}")
                        # Update cars (AI for all undriven cars)
                        for car in self.cars:
                            if not car.driver:
                                car.update_ai(self.city.map, self.traffic_lights, self.npcs)
                        # --- WEATHER SYSTEM: update weather each turn ---
                        current_date = self.time_system.get_current_datetime()
                        self.weather_system.update_weather(current_date)
                elif wait:
                    # Wait/skip turn
                    self.time_system.advance_time()
                    move_cooldown = 10
                    for npc in self.npcs:
                        try:
                            npc.update(self.city.map, self.traffic_lights, self.npcs)
                            action = decide_action(npc, self)
                            if action['action'] == 'move' and action['target']:
                                npc.x, npc.y = action['target']
                            if hasattr(npc, 'can_see_player') and npc.can_see_player(self.player):
                                if getattr(self.player, 'is_threatening', False):
                                    handle_player_threat(npc, self.player, self)
                        except Exception as e:
                            debug_log(f"[Game WARNING] NPC update/AI failed for {getattr(npc, 'npc_id', '?')}: {e}")
                    try:
                        maybe_spread_rumor(self)
                    except Exception as e:
                        debug_log(f"[Game WARNING] RumorMill failed: {e}")
                    for car in self.cars:
                        if not car.driver:
                            car.update_ai(self.city.map, self.traffic_lights, self.npcs)
                    current_date = self.time_system.get_current_datetime()
                    self.weather_system.update_weather(current_date)

            # Cooldown Countdown
            if move_cooldown > 0:
                move_cooldown -= 1

            # Rest of game loop (rendering etc)
            self.render_game()

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
        debug_log(f"Drawing {len(self.cars)} cars. Camera at ({camera_x}, {camera_y})")
        for car in self.cars:
            screen_x = (car.x - camera_x) * TILE_SIZE
            screen_y = (car.y - camera_y) * TILE_SIZE
            debug_log(f"Drawing car {car.type} at screen pos ({screen_x}, {screen_y}) from world pos ({car.x}, {car.y})")
            
            # Set car_direction for correct sprite flipping
            self.graphics.car_direction = car.direction
            self.graphics.draw_car(
                self.screen,
                car.type,
                screen_x,
                screen_y,
                'horizontal' if car.direction in ('left', 'right') else 'vertical',
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
        interactables = []
        for dx, dy in facing:
            tx, ty = self.player.x + dx, self.player.y + dy
            tile = self.city.get_tile(tx, ty)
            # Check for doors and windows
            if tile == TILE_DOOR:
                interactables.append({'type': 'door', 'x': tx, 'y': ty, 'desc': 'Door'})
            elif tile == TILE_WINDOW:
                interactables.append({'type': 'window', 'x': tx, 'y': ty, 'desc': 'Window'})
            # Check for cars
            car = next((c for c in self.cars if (tx, ty) in c.get_tiles()), None)
            if car:
                interactables.append({'type': 'car', 'x': tx, 'y': ty, 'desc': f"{car.type.title()} car", 'car': car})
            # Check for NPCs
            npc = next((n for n in self.npcs if n.x == tx and n.y == ty), None)
            if npc:
                interactables.append({'type': 'npc', 'x': tx, 'y': ty, 'desc': f"{npc.name}", 'npc': npc})
            # Check for shops
            shop_name = self.city.get_shop_at(tx, ty)
            if shop_name:
                interactables.append({'type': 'shop', 'x': tx, 'y': ty, 'desc': f"Shop: {shop_name}", 'shop': shop_name})
            # Check for furniture
            fname, state = self.get_furniture_at(tx, ty)
            if fname:
                interactables.append({'type': 'furniture', 'x': tx, 'y': ty, 'desc': f"{fname} (state: {state})", 'fname': fname, 'state': state})
        if not interactables:
            self.show_message_and_wait("There's nothing to interact with.")
            return
        # Build menu
        options = [f"{item['desc']} at ({item['x']},{item['y']})" for item in interactables]
        choice = self.show_menu_and_wait("Choose what to interact with:", options)
        selected = interactables[choice]
        tx, ty = selected['x'], selected['y']
        tile = self.city.get_tile(tx, ty)
        # Now show the appropriate menu for the selected interactable
        if selected['type'] == 'door':
            actions = ["Open/Close", "Inspect", "Cancel"]
            choice = self.show_menu_and_wait(f"Interact with door:", actions)
            if actions[choice] == "Open/Close":
                self.toggle_door_window(tx, ty, tile, 'open')
                self.show_message_and_wait(f"You {self.furniture_state.get((tx, ty), {}).get('state', 'closed')} the door.")
            elif actions[choice] == "Inspect":
                self.show_message_and_wait("A sturdy door.")
        elif selected['type'] == 'window':
            actions = ["Peek", "Break", "Cancel"]
            choice = self.show_menu_and_wait(f"Interact with window:", actions)
            if actions[choice] == "Peek":
                self.show_message_and_wait("You peek through the window.")
            elif actions[choice] == "Break":
                self.furniture_state[(tx, ty)] = {'type': tile, 'state': 'broken'}
                self.show_message_and_wait("You smash the window!")
        elif selected['type'] == 'car':
            car = selected['car']
            actions = ["Hijack", "Smash", "Inspect", "Enter", "Cancel"]
            choice = self.show_menu_and_wait(f"Interact with {car.type.title()} car:", actions)
            if actions[choice] == "Hijack":
                if not getattr(self.player, 'in_car', None):
                    if random.random() < 0.5:
                        if car.driver:
                            hijack_success = car.hijack(self.player)
                            if hijack_success:
                                self.show_message_and_wait(f"You violently eject {car.driver.name if car.driver and car.driver != self.player else 'the NPC'} from the car!")
                                self.add_journal_entry(f"Ejected previous driver from {car.type} car")
                                msg = f"You successfully hijack the {car.type} car!"
                                self.add_journal_entry(msg)
                            else:
                                msg = "The driver resists your hijack attempt!"
                        else:
                            car.set_driver(self.player)
                            msg = f"You successfully hijack the {car.type} car!"
                            self.add_journal_entry(msg)
                    else:
                        msg = "You fail to hijack the car!"
                    self.show_message_and_wait(msg)
                else:
                    self.show_message_and_wait("You're already in a car!")
            elif actions[choice] == "Enter":
                if not getattr(self.player, 'in_car', None):
                    if car.hp > 0:
                        if car.driver:
                            self.show_message_and_wait("Someone is already driving this car!")
                        else:
                            car.set_driver(self.player)
                            msg = f"You enter the {car.type} car."
                            self.add_journal_entry(msg)
                            self.show_message_and_wait(msg)
                    else:
                        msg = "This car is too damaged to drive!"
                        self.show_message_and_wait(msg)
                else:
                    self.show_message_and_wait("You're already in a car!")
            # ...existing code for Smash, Inspect, Cancel...
        elif selected['type'] == 'npc':
            npc = selected['npc']
            if npc.is_dead:
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
            elif npc.is_knocked_out:
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
            else:
                actions = ["Talk", "Fight", "Inspect", "Give Gift", "Insult", "Trade", "Cancel"]
                choice = self.show_menu_and_wait(f"Interact with {npc.name}:", actions)
                if actions[choice] == "Talk":
                    conversation = npc.start_conversation()
                    prompt = conversation["prompt"]
                    responses = conversation["responses"]
                    self.show_message_and_wait(f"{npc.name} asks: '{prompt}'", True, npc.appearance)
                    response_options = [resp[0] for resp in responses]
                    response_options.append("(Leave conversation)")
                    choice = self.show_menu_and_wait("How do you respond?", response_options)
                    if choice < len(responses):
                        chosen_response, reaction = responses[choice]
                        reaction = reaction.format(name=npc.name)
                        self.show_message_and_wait(reaction, True, npc.appearance)
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
        elif selected['type'] == 'shop':
            self.show_shop_menu(selected['shop'])
        elif selected['type'] == 'furniture':
            fname = selected['fname']
            state = selected['state']
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

    def show_message_and_wait(self, message, portrait=False, appearance=None):
        """Display a message and wait for player to press a key."""
        font = pygame.font.SysFont(None, 32)
        while True:
            self.screen.fill((0, 0, 0))
            lines = message.split('\n')
            for i, line in enumerate(lines):
                text = font.render(line, True, (255, 255, 255))
                self.screen.blit(text, (40, 100 + i * 40))
            # Optionally draw portrait (if used in NPC interactions)
            if portrait and appearance:
                from stinkworld.ui.appearance import draw_portrait
                draw_portrait(self.screen, 40, 40, 64, appearance)
            inst = font.render("Press any key to continue...", True, (180, 180, 180))
            self.screen.blit(inst, (40, 500))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    return

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
        for i in range(count):
            x, y = self.city.find_walkable_tile()
            if x is not None and y is not None:
                name = random_name()
                npc_id = f"npc_{i+1:04d}"
                npc = NPC(name, x, y, npc_id=npc_id)
                self.npcs.append(npc)
                self.debug(f"Spawned NPC {name} (ID: {npc_id}) at ({x}, {y})")

    def spawn_cars(self, count=30):
        """Spawn cars at random road positions."""
        road_tiles = []
        for y in range(self.city.height):
            for x in range(self.city.width):
                if self.city.get_tile(x, y) == TILE_ROAD:
                    road_tiles.append((x, y))
        
        if not road_tiles:
            debug_log("[WARNING] No road tiles found for car spawning!")
            return
            
        debug_log(f"[CAR SPAWN] Attempting to spawn {count} cars on {len(road_tiles)} road tiles")
        
        for _ in range(count):
            x, y = random.choice(road_tiles)
            car_type = random.choice(['sedan', 'truck', 'sports'])
            self.cars.append(Car(x, y, car_type))
            debug_log(f"[CAR SPAWN] Spawned {car_type} at ({x}, {y})")

    def init_player(self):
        """Initialize player at optimal road position near center."""
        # Try center position first
        center_x, center_y = self.city.width // 2, self.city.height // 2
        print(f"\n=== SPAWN DEBUG ===")
        print(f"Map dimensions: {self.city.width}x{self.city.height}")
        print(f"Checking center tile at ({center_x}, {center_y})")
        print(f"Center tile type: {self.city.get_tile(center_x, center_y)}")
        print(f"Is walkable: {self.is_walkable(center_x, center_y)}")
        
        if self.is_walkable(center_x, center_y) and self.city.get_tile(center_x, center_y) == TILE_ROAD:
            spawn_x, spawn_y = center_x, center_y
            print(f"Perfect road spawn found at center: ({center_x}, {center_y})")
        else:
            # Spiral search pattern
            print(f"Center not walkable - beginning spiral search...")
            spawn_x, spawn_y = None, None
            max_radius = min(self.city.width, self.city.height) // 2
            
            for radius in range(1, max_radius + 1):
                print(f"\nSearching radius {radius}...")
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        if abs(dx) == radius or abs(dy) == radius:
                            x, y = center_x + dx, center_y + dy
                            if 0 <= x < self.city.width and 0 <= y < self.city.height:
                                tile = self.city.get_tile(x, y)
                                walkable = self.is_walkable(x, y)
                                print(f"Checking ({x}, {y}): type={tile}, walkable={walkable}")
                                if walkable:
                                    if tile == TILE_ROAD:
                                        spawn_x, spawn_y = x, y
                                        print(f"FOUND ROAD TILE at ({x}, {y})")
                                        break
                                    elif spawn_x is None:
                                        spawn_x, spawn_y = x, y
                                        print(f"Fallback walkable at ({x}, {y})")
                    else:
                        continue
                    break
                else:
                    continue
                break
            
            if spawn_x is None:
                print("WARNING: No valid spawn found in spiral search!")
                spawn_x, spawn_y = 0, 0
        
        print(f"\n=== FINAL SPAWN DECISION ===")
        print(f"Chosen position: ({spawn_x}, {spawn_y})")
        print(f"Tile type: {self.city.get_tile(spawn_x, spawn_y)}")
        print(f"Is walkable: {self.is_walkable(spawn_x, spawn_y)}")
        
        self.player = Player(self.settings)
        self.player.x = spawn_x
        self.player.y = spawn_y
        print(f"\n=== ACTUAL PLAYER POSITION ===")
        print(f"Player.x: {self.player.x}")
        print(f"Player.y: {self.player.y}")
        print(f"Camera should focus on: ({self.player.x}, {self.player.y})")
        
        # Verify no position override happening
        print("\nVerifying no position override...")
        print(f"Player position after init: ({self.player.x}, {self.player.y})")
        
        self.debug(f"Player spawned at ({spawn_x}, {spawn_y})")

    def advance_time(self):
        """Advance the game time and trigger updates."""
        self.time_system.advance_time()
        self.turn += 1
        
        # Force updates when time advances
        for npc in self.npcs:
            npc.update(self.city.map, self.traffic_lights, self.npcs)
        
        for car in self.cars:
            if not car.driver:
                car.update_ai(self.city.map, self.traffic_lights, self.npcs)

    def render_game(self):
        """Handle all rendering operations."""
        # Calculate camera position
        if hasattr(self.player, 'in_car') and self.player.in_car:
            car = self.player.in_car
            camera_x = max(0, min(car.x - VIEWPORT_WIDTH // 2, self.city.width - VIEWPORT_WIDTH))
            camera_y = max(0, min(car.y - VIEWPORT_HEIGHT // 2, self.city.height - VIEWPORT_HEIGHT))
        else:
            camera_x = max(0, min(self.player.x - VIEWPORT_WIDTH // 2, self.city.width - VIEWPORT_WIDTH))
            camera_y = max(0, min(self.player.y - VIEWPORT_HEIGHT // 2, self.city.height - VIEWPORT_HEIGHT))
        
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Draw map and entities
        self.draw_map(camera_x, camera_y)
        self.draw_cars(camera_x, camera_y)
        
        # Draw traffic lights
        for light in self.traffic_lights:
            light.draw(self.screen, camera_x, camera_y)
        
        # Draw NPCs
        for npc in self.npcs:
            npc.draw(self.screen, camera_x, camera_y)
        
        # Draw player (only if not in car)
        if not hasattr(self.player, 'in_car') or not self.player.in_car:
            self.player.draw(self.screen, camera_x, camera_y)
        
        # Apply lighting based on time of day
        self.time_system.apply_lighting(self.screen)
        # --- WEATHER SYSTEM: draw weather effects after lighting ---
        time_of_day_lighting = self.time_system.get_lighting_color()
        self.weather_system.apply_weather_effects(self.screen, time_of_day_lighting)
        
        # Draw HUD
        self.draw_hud()
        
        # Update display
        pygame.display.flip()
        self.clock.tick(30)  # Lock to 30 FPS

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
        if hasattr(self.player, 'in_car') and self.player.in_car:
            car_type = self.player.in_car.type
            controls_text = f"SPACE: Exit {car_type}  WASD: Drive  E: Interact  J: Journal  ESC: Menu"
            # Draw car status
            car_hp = self.player.in_car.hp
            car_max_hp = self.player.in_car.max_hp
            car_status = f"Vehicle: {car_type} ({car_hp}/{car_max_hp} HP)"
            car_status_surface = font.render(car_status, True, (255, 255, 0))
            self.screen.blit(car_status_surface, (self.screen.get_width() - 300, self.screen.get_height() - 40))
        else:
            controls_text = "E: Interact  J: Journal  WASD: Move  ESC: Menu"
        controls_surface = font.render(controls_text, True, (180, 180, 180))
        self.screen.blit(controls_surface, (self.screen.get_width() - 300, self.screen.get_height() - 20))
        # --- WEATHER SYSTEM: show weather in HUD ---
        weather_text = self.weather_system.get_description()
        weather_surface = font.render(weather_text, True, (200, 200, 255))
        self.screen.blit(weather_surface, (10, self.screen.get_height() - 100))

    def start_combat(self, npc):
        """Begin combat with the given NPC."""
        if npc is None:
            debug_log("[Game ERROR] start_combat called with None NPC.")
            return
        if not hasattr(npc, 'name') or not hasattr(npc, 'npc_id'):
            debug_log(f"[Game ERROR] start_combat: NPC missing name or npc_id: {npc}")
            return
        print(f"Starting combat with {npc.name} ({npc.npc_id})")
        try:
            from stinkworld.combat.system import start_combat as combat_start
            combat_start(self, npc)
        except Exception as e:
            debug_log(f"[Game ERROR] Combat system failed to start: {e}")
            self.show_message_and_wait(f"Combat could not be started with {npc.name}.")