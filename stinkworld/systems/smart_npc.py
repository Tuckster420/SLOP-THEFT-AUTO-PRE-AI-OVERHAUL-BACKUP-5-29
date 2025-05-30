"""
smart_npc.py - Deep, life-sim style NPC AI for StinkWorld

This module provides a data-driven, modular AI for NPCs, supporting routines, jobs, family, and evolving relationships.
All logic is isolated here. To use, import and call decide_action(npc, game_state) in update_npcs().

Data definitions (jobs, routines, relationships) are loaded from data/npc_definitions.json for easy tweaking.

If any required data is missing, or an error occurs, the old NPC behavior is called for safety.

---
USAGE SNIPPET (for update_npcs):
    from stinkworld.systems import smart_npc
    ...
    action = smart_npc.decide_action(npc, self)
    ...
"""
import json
import os
import random
import time

# --- Load DATA from external JSON file ---
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'npc_definitions.json')
try:
    with open(DATA_PATH, 'r') as f:
        DATA = json.load(f)
except Exception as e:
    print(f"[smart_npc WARNING] Failed to load npc_definitions.json: {e}")
    DATA = {"jobs": {}, "npcs": {}, "routines": {}}

# --- Pathfinder import with logging ---
try:
    from stinkworld.core import pathfinder
except ImportError:
    print("[smart_npc WARNING] Pathfinder unavailable, NPCs will wander.")
    pathfinder = None

# --- Memory & Rumors system (optional) ---
USE_MEMORY_RUMORS = False

try:
    from stinkworld.systems.memory_and_rumors import MemoryLog, RumorMill
    # Create a single global memory log instance
    memory_log = MemoryLog()
except Exception as e:
    print(f"[smart_npc WARNING] Could not import memory_and_rumors: {e}")
    memory_log = None

# --- Helper: get current hour from time system ---
def get_current_hour(game_state):
    try:
        return int(getattr(game_state, 'time', getattr(game_state, 'time_system', None)).hour)
    except Exception:
        print("[smart_npc WARNING] Could not get current hour from time system, defaulting to 12.")
        return 12  # Default: noon

# --- Routine Engine ---
class RoutineEngine:
    @staticmethod
    def get_routine_step(routine, hour):
        for step in reversed(routine):
            if hour >= step['time']:
                return step['action']
        return routine[0]['action'] if routine else 'wander'

    @staticmethod
    def get_home_location(npc, profile, game_state):
        # Prefer explicit home in profile
        if 'home' in profile:
            return tuple(profile['home'])
        # If already assigned this session, use it
        if hasattr(npc, 'home') and npc.home:
            return npc.home
        # Otherwise, pick a random walkable tile
        try:
            walkable = []
            gmap = getattr(game_state, 'map', None)
            if gmap:
                for x in range(len(gmap)):
                    for y in range(len(gmap[0])):
                        if gmap[x][y] == 0:
                            walkable.append((x, y))
            if walkable:
                home = random.choice(walkable)
                npc.home = home
                print(f"[smart_npc WARNING] Assigned random home {home} to NPC {getattr(npc, 'npc_id', '?')}")
                return home
        except Exception as e:
            print(f"[smart_npc WARNING] Could not assign home for NPC {getattr(npc, 'npc_id', '?')}: {e}")
        # Fallback
        print(f"[smart_npc WARNING] No home found for NPC {getattr(npc, 'npc_id', '?')}, using (0,0)")
        npc.home = (0, 0)
        return (0, 0)

# --- Relationship Engine ---
class RelationshipEngine:
    @staticmethod
    def check_relationships(npc, relationships, game_state):
        for other in getattr(game_state, 'npcs', []):
            if other is npc or not hasattr(other, 'npc_id'):
                continue
            affinity = relationships.get(other.npc_id, 0)
            dist = abs(npc.x - other.x) + abs(npc.y - other.y)
            if dist <= 2:
                if affinity < -5:
                    # Rival: avoid or confront
                    if random.random() < 0.5:
                        return MovementEngine.move_away(npc, other, game_state)
                    else:
                        return {'action': 'confront', 'target': (other.x, other.y), 'with': other.npc_id}
                elif affinity > 10:
                    # Friend: socialize
                    return {'action': 'socialize', 'target': (other.x, other.y), 'with': other.npc_id}
        return None

# --- Movement Engine ---
class MovementEngine:
    @staticmethod
    def move_toward(npc, dest, game_state):
        if pathfinder and hasattr(game_state, 'map'):
            try:
                path = pathfinder.find_path((npc.x, npc.y), tuple(dest), game_state.map)
                if path and len(path) > 1:
                    return {'action': 'move', 'target': path[1], 'with': None}
            except Exception as e:
                print(f"[smart_npc WARNING] Pathfinder error for NPC {getattr(npc, 'npc_id', '?')}: {e}")
        print(f"[smart_npc WARNING] Pathfinder unavailable or failed for NPC {getattr(npc, 'npc_id', '?')}, wandering.")
        return MovementEngine.wander(npc, game_state)

    @staticmethod
    def move_away(npc, other, game_state):
        dx = npc.x - other.x
        dy = npc.y - other.y
        options = [
            (npc.x + (1 if dx <= 0 else -1), npc.y),
            (npc.x, npc.y + (1 if dy <= 0 else -1)),
        ]
        random.shuffle(options)
        for pos in options:
            if MovementEngine.is_walkable(pos, game_state):
                return {'action': 'move', 'target': pos, 'with': None}
        return MovementEngine.wander(npc, game_state)

    @staticmethod
    def wander(npc, game_state):
        options = [
            (npc.x + 1, npc.y), (npc.x - 1, npc.y),
            (npc.x, npc.y + 1), (npc.x, npc.y - 1)
        ]
        random.shuffle(options)
        for pos in options:
            if MovementEngine.is_walkable(pos, game_state):
                return {'action': 'move', 'target': pos, 'with': None}
        return {'action': 'idle', 'target': None, 'with': None}

    @staticmethod
    def is_walkable(pos, game_state):
        x, y = pos
        try:
            return game_state.map[x][y] == 0
        except Exception:
            return False

# --- Main AI entry point ---
def decide_action(npc, game_state):
    """
    Decide the next action for an NPC based on routine, job, family, and relationships.
    Returns a dict: { 'action': str, 'target': (x, y) or None, 'with': npc_id or None }
    Falls back to npc.old_behavior() on error or missing data.
    """
    try:
        npc_id = getattr(npc, 'npc_id', None)
        if not npc_id or npc_id not in DATA['npcs']:
            print(f"[smart_npc WARNING] NPC {npc_id} missing from definitions, falling back.")
            return _fallback(npc)
        profile = DATA['npcs'][npc_id]
        job = profile.get('job')
        job_info = DATA['jobs'].get(job)
        routine = DATA['routines'].get('default', [])
        family = profile.get('family', [])
        relationships = profile.get('relationships', {})
        hour = get_current_hour(game_state)
        # --- Step 1: Routine selection ---
        step = RoutineEngine.get_routine_step(routine, hour)
        if step == 'go_to_work' and job_info:
            if _at_location(npc, job_info['location']):
                return {'action': 'work_task', 'target': job_info['location'], 'with': None}
            else:
                return MovementEngine.move_toward(npc, job_info['location'], game_state)
        elif step == 'eat_lunch':
            tavern = DATA['jobs']['tavernkeeper']['location']
            if _at_location(npc, tavern):
                return {'action': 'eat', 'target': tavern, 'with': None}
            else:
                return MovementEngine.move_toward(npc, tavern, game_state)
        elif step == 'go_home':
            home = RoutineEngine.get_home_location(npc, profile, game_state)
            if _at_location(npc, home):
                return {'action': 'rest', 'target': home, 'with': None}
            else:
                return MovementEngine.move_toward(npc, home, game_state)
        elif step == 'socialize':
            fam_npc = _find_nearby_family(npc, family, game_state)
            if fam_npc:
                return {'action': 'socialize', 'target': (fam_npc.x, fam_npc.y), 'with': fam_npc.npc_id}
            else:
                return MovementEngine.wander(npc, game_state)
        elif step == 'sleep':
            home = RoutineEngine.get_home_location(npc, profile, game_state)
            if _at_location(npc, home):
                return {'action': 'sleep', 'target': home, 'with': None}
            else:
                return MovementEngine.move_toward(npc, home, game_state)
        # --- Step 2: Relationship triggers ---
        rel_action = RelationshipEngine.check_relationships(npc, relationships, game_state)
        if rel_action:
            return rel_action
        # --- Step 3: Fallback to wander ---
        return MovementEngine.wander(npc, game_state)
    except Exception as e:
        print(f"[smart_npc WARNING] Exception for NPC {getattr(npc, 'npc_id', '?')}: {e}")
        return _fallback(npc)

def _at_location(npc, loc):
    return (getattr(npc, 'x', -1), getattr(npc, 'y', -1)) == tuple(loc)

def _find_nearby_family(npc, family_ids, game_state):
    for other in getattr(game_state, 'npcs', []):
        if hasattr(other, 'npc_id') and other.npc_id in family_ids:
            if abs(npc.x - other.x) + abs(npc.y - other.y) <= 2:
                return other
    return None

def _fallback(npc):
    if hasattr(npc, 'old_behavior') and callable(npc.old_behavior):
        try:
            return npc.old_behavior()
        except Exception as e:
            print(f"[smart_npc WARNING] old_behavior failed for NPC {getattr(npc, 'npc_id', '?')}: {e}")
    return {'action': 'idle', 'target': None, 'with': None}

# Example: NPCs call this when they do something notable
# (This should be called in the NPC's action logic, e.g. after a good deed or social event)
def npc_remember_action(npc, description):
    try:
        if USE_MEMORY_RUMORS and memory_log:
            memory_log.remember(str(getattr(npc, 'npc_id', '?')), description)
    except Exception as e:
        print(f"[smart_npc WARNING] npc_remember_action failed for {getattr(npc, 'npc_id', '?')}: {e}")

# Example: Periodically spread rumors (call this from your main loop or NPC system)
_last_rumor_time = 0

def maybe_spread_rumor(game_state):
    global _last_rumor_time
    try:
        if not USE_MEMORY_RUMORS or not memory_log:
            return
        now = time.time()
        # Spread a rumor every 5-15 seconds (randomized interval)
        interval = getattr(maybe_spread_rumor, 'interval', None)
        if interval is None or now - _last_rumor_time > interval:
            import random
            maybe_spread_rumor.interval = random.uniform(5, 15)
            _last_rumor_time = now
            # Pick a random NPC to spread a rumor
            npcs = getattr(game_state, 'npcs', [])
            if npcs:
                spreader = random.choice(npcs)
                RumorMill.spread(memory_log, npcs, game_state)
    except Exception as e:
        print(f"[smart_npc WARNING] maybe_spread_rumor failed: {e}")

def handle_player_threat(npc, player, game_state):
    """
    Decide if the NPC flees or fights when threatened by the player, based on personality traits.
    - High cowardice: flee
    - High aggression/anger: fight
    - Neutral: random/hesitate
    Integrates with MemoryLog and logs all events.
    """
    try:
        # Get traits (default to 0 if missing)
        cowardice = getattr(npc, 'cowardice', 0)
        aggression = getattr(npc, 'aggression', 0)
        anger = getattr(npc, 'anger', 0)
        # Decision logic
        if cowardice > 7:
            # Flee
            npc.is_afraid = True
            # Move away from player
            if hasattr(game_state, 'player'):
                move_action = None
                try:
                    from stinkworld.systems.smart_npc import MovementEngine
                    move_action = MovementEngine.move_away(npc, player, game_state)
                except Exception as e:
                    print(f"[smart_npc WARNING] Flee pathfinding failed for {getattr(npc, 'npc_id', '?')}: {e}")
                # Optionally trigger scared reaction
                print(f"[smart_npc] {getattr(npc, 'npc_id', '?')} flees from player!")
                # Log to memory
                if 'memory_log' in globals() and memory_log:
                    memory_log.remember(str(getattr(npc, 'npc_id', '?')), "bad: threatened")
                return move_action if move_action else {'action': 'move', 'target': (npc.x, npc.y), 'with': None}
        elif aggression > 7 or anger > 7:
            # Fight
            # Optionally trigger taunt
            print(f"[smart_npc] {getattr(npc, 'npc_id', '?')} attacks the player!")
            # Log to memory
            if 'memory_log' in globals() and memory_log:
                memory_log.remember(str(getattr(npc, 'npc_id', '?')), "bad: attacked player")
            # Reduce affinity toward player if possible
            if hasattr(npc, 'adjust_affinity'):
                try:
                    npc.adjust_affinity(getattr(player, 'npc_id', 'player'), -2)
                except Exception as e:
                    print(f"[smart_npc WARNING] adjust_affinity failed for {getattr(npc, 'npc_id', '?')}: {e}")
            # Initiate combat (assume combat system is called elsewhere)
            return {'action': 'attack', 'target': (player.x, player.y), 'with': getattr(player, 'npc_id', 'player')}
        else:
            # Neutral/hesitate: random choice
            import random
            if random.random() < 0.5:
                # Flee
                npc.is_afraid = True
                print(f"[smart_npc] {getattr(npc, 'npc_id', '?')} hesitates, then flees!")
                if 'memory_log' in globals() and memory_log:
                    memory_log.remember(str(getattr(npc, 'npc_id', '?')), "bad: threatened")
                move_action = None
                try:
                    from stinkworld.systems.smart_npc import MovementEngine
                    move_action = MovementEngine.move_away(npc, player, game_state)
                except Exception as e:
                    print(f"[smart_npc WARNING] Flee pathfinding failed for {getattr(npc, 'npc_id', '?')}: {e}")
                return move_action if move_action else {'action': 'move', 'target': (npc.x, npc.y), 'with': None}
            else:
                # Fight
                print(f"[smart_npc] {getattr(npc, 'npc_id', '?')} hesitates, then attacks!")
                if 'memory_log' in globals() and memory_log:
                    memory_log.remember(str(getattr(npc, 'npc_id', '?')), "bad: attacked player")
                if hasattr(npc, 'adjust_affinity'):
                    try:
                        npc.adjust_affinity(getattr(player, 'npc_id', 'player'), -1)
                    except Exception as e:
                        print(f"[smart_npc WARNING] adjust_affinity failed for {getattr(npc, 'npc_id', '?')}: {e}")
                return {'action': 'attack', 'target': (player.x, player.y), 'with': getattr(player, 'npc_id', 'player')}
    except Exception as e:
        print(f"[smart_npc WARNING] handle_player_threat failed for {getattr(npc, 'npc_id', '?')}: {e}")
        return {'action': 'idle', 'target': None, 'with': None}

# --- TODO: Expand routines, jobs, and relationship logic as needed. ---
