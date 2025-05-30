# StinkWorld Codemap & AI Instructions

## 1. Entry Point & Game Loop

- **File:** `stinkworld/core/main.py`
- **Purpose:** Main entry point. Initializes Pygame, settings, and launches the main menu and game loop.
- **AI Instructions:**  
  - To change how the game starts, edit `main()` here.
  - To add new startup options, modify the main menu logic.
  - For debugging startup, add logs here.

---

## 2. Core Game Logic

- **File:** `stinkworld/core/game.py`
- **Purpose:** Contains the `Game` class, which manages the main game state, player, NPCs, city, cars, menus, combat, and all core systems.
- **AI Instructions:**  
  - All main gameplay features (movement, interaction, combat, saving/loading, HUD, menus) are methods of `Game`.
  - To add new player actions, extend the `interact()` method.
  - To add new menus, add methods and call them from `game_loop()` or `interact()`.
  - To add new systems (e.g., hunger, skills), instantiate them in `__init__` and update in `game_loop()`.
  - For new save data, update `save_game()` and `load_game()`.

---

## 3. City Generation

- **File:** `stinkworld/core/city.py`
- **Purpose:** Handles procedural city generation, including roads, buildings, parks, and biomes.
- **AI Instructions:**  
  - To change city layout, edit `generate_city_map()` and related functions.
  - To add new building or terrain types, update constants and drawing logic.

---

## 4. Entities

- **Folder:** `stinkworld/entities/`
- **Files:** `player.py`, `npc.py`, `car.py`, `character_creation.py`, etc.
- **Purpose:** Define all in-game entities and their behaviors.
- **AI Instructions:**  
  - To add new entity types, create new classes here.
  - To change player or NPC stats/logic, edit `player.py` or `npc.py`.
  - For new vehicle types, extend `car.py`.

---

## 5. Systems

- **Folder:** `stinkworld/systems/`
- **Files:** `time.py`, `weather.py`, `economy.py`, `traffic.py`
- **Purpose:** Modular systems for time, weather, economy, and traffic.
- **AI Instructions:**  
  - To add a new system (e.g., hunger), create a new file and instantiate in `Game`.
  - To change how time or weather works, edit the respective file.
  - **Weather system is now fully restored, modular, and integrated. Weather effects (rain, snow, fog, etc.) are rendered, update each turn, and display in the HUD.**

---

## 6. Combat

- **Folder:** `stinkworld/combat/`
- **Files:** `system.py`, `injuries.py`, `messages.py`
- **Purpose:** Handles turn-based combat, injury mechanics, and combat messages.
- **AI Instructions:**  
  - To add new combat moves, update `system.py` and the combat menu in `game.py`.
  - To add new injury types, update `injuries.py`.
  - To change combat text, edit `messages.py`.

---

## 7. Data

- **Folder:** `stinkworld/data/`
- **Files:** `names.py`, `personality.py`, `conversations.py`
- **Purpose:** Static data for names, personalities, and conversations.
- **AI Instructions:**  
  - To add new names or personalities, edit the respective file.
  - To add new conversation prompts, update `conversations.py`.

---

## 8. UI

- **Folder:** `stinkworld/ui/`
- **Files:** `base.py`, `menus.py`, `graphics.py`, `appearance.py`
- **Purpose:** Handles all user interface elements, menus, and graphics rendering.
- **AI Instructions:**  
  - To add new UI screens, create new methods or files here.
  - To change how menus look or behave, edit `menus.py`.
  - For new HUD elements, update `graphics.py` and `game.py`.

---

## 9. Utilities

- **Folder:** `stinkworld/utils/`
- **Files:** `common.py`, `debug.py`
- **Purpose:** Helper functions and debugging utilities.
- **AI Instructions:**  
  - Add general-purpose helpers here.
  - Use `debug_log()` for logging.

---

## 10. Project Data & Scripts

- **Files:**  
  - `requirements.txt` — Python dependencies.
  - `setup.py` — Install script.
  - `README.md` — Project overview, install, and play instructions.
  - `saves/` — Save files.
  - `sprites/` — Game graphics.

---

# General AI Instructions

- **To add a new feature:**  
  1. Identify the relevant system (core, entity, system, UI, etc.).
  2. Add or extend classes/methods as needed.
  3. Register new systems/entities in `Game` if they need to be updated each turn.
  4. Update save/load logic if persistent data is needed.
  5. Add UI/menus if user interaction is required.

- **To debug:**  
  - Use `debug_log()` in `stinkworld/utils/debug.py` for logging.
  - Add logs at entry/exit of major methods.

- **To extend data-driven content:**  
  - Add to `stinkworld/data/` for names, personalities, conversations, etc.

- **To change controls or HUD:**  
  - Edit `draw_hud()` and menu methods in `game.py` and `ui/`.

---

This codemap should help any AI or developer quickly orient themselves and make effective, safe changes to the project. If you need a more detailed map of a specific module, just ask!
