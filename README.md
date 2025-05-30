# Stink World

A city simulation game where AI systems drive core mechanics, with rigorous testing and iterative improvement.

## Features

### Implemented
- Basic city rendering (buildings, roads, grass).
- NPCs with rudimentary AI (pathfinding and basic interactions).
- Day/night cycle with dynamic lighting.
- Modular weather system: Dynamic weather (rain, snow, fog, etc.) is now fully restored and integrated. Weather updates each turn, is rendered visually, and the current weather is shown in the HUD.

### Unimplemented (Planned)
- **Car Driving**: Implement vehicle physics and traffic AI.

## Project Philosophy

This project prioritizes:
1. **AI-Centric Development**: All core systems rely on AI, with a focus on scalability and adaptability.
2. **Critical Feedback**: AI performance is scrutinized aggressively. Examples of required feedback:
   - "This pathfinding algorithm is an embarrassment to computational science."
   - "Your weather simulation is so broken, it's actively making the game worse."
   - "If this NPC behavior were any dumber, it would qualify as a bug, not a feature."

## How to Contribute
- Report bugs with explicit, technical critiques of the AI's failures.
- Propose features that stress-test the AI's capabilities.
- Document edge cases where the AI behaves unpredictably or fails.

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd stinkworld
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Running the Game

After installation, you can run the game in two ways:

1. Using the console script:
```bash
stinkworld
```

2. Running the module directly:
```bash
python -m stinkworld.core.main
```

## Project Structure

```
stinkworld/
├── core/           # Core game mechanics
│   ├── main.py     # Main entry point
│   ├── game.py     # Main game class
│   ├── settings.py # Game settings
│   └── city.py     # City generation
├── entities/       # Game entities
│   ├── player.py   # Player class
│   ├── npc.py      # NPC system
│   └── car.py      # Vehicle system
├── systems/        # Game systems
│   ├── time.py     # Time system
│   ├── weather.py  # Weather system
│   └── economy.py  # Economy system
├── ui/            # User interface
│   ├── base.py     # Base UI components
│   └── menus.py    # Menu system
├── combat/        # Combat system
│   ├── system.py   # Combat mechanics
│   └── injuries.py # Injury system
├── data/          # Game data
│   ├── names.py    # NPC names
│   └── personality.py # NPC personalities
└── utils/         # Utility functions
    └── helpers.py  # Helper functions
```

## Dependencies

- Python >= 3.8
- Pygame >= 2.5.0
- NumPy >= 1.24.0

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Current Features

### Core Systems
- Open world city environment with procedurally generated buildings and streets
- Day/night cycle with 96 turns per day (15 minutes per turn)
- Dynamic lighting system based on time of day (dawn, day, dusk, night)
- Comprehensive weather system with multiple conditions:
  - Clear, cloudy, rain, storm, fog, and snow
  - Season-based weather probabilities
  - Visual effects including particle systems
  - Weather impacts on gameplay (movement penalties, visibility)

### Graphics System
- Detailed sprite-based graphics for all game elements
- Animated character sprites with dynamic hair movement
- Vehicle sprites with proper rotation and dimensions
- Terrain sprites including textured roads, grass, and buildings
- Furniture sprites with state-based rendering (normal, damaged, vandalized)
- Dynamic visual effects for weather and time of day
- Proper transparency handling for all sprites

### Character Systems
- Detailed character creation
- NPCs with unique personalities and appearances
- Relationship system with NPCs
- Memory system for NPC interactions
- Comprehensive injury system with different body parts and injury types
- Animated NPCs with realistic movement and pathfinding

### Combat System
- Turn-based combat mechanics
- Multiple attack types (punch, kick, targeted attacks)
- Critical hit system
- Injury mechanics affecting gameplay
- Taunting system with NPC debuffs

### World Interaction
- Interactive furniture and objects
- Multiple interaction options (use, move, break, vandalize, inspect)
- Vehicle system with cars and traffic
- Traffic light system at intersections

### UI and Game Systems
- In-game journal system
- Detailed HUD with health, time, and position information
- Save/load system with multiple slots
- Main menu and character creation interfaces

## Roadmap

### Priority Features
1. **Dynamic Weather System**
   - Precipitation effects (rain/snow) with particle systems
   - Weather-impacted NPC behavior (e.g., seeking shelter)
   - Performance optimizations for weather rendering

2. **Vehicle Physics & Traffic AI**
   - Basic car mechanics (acceleration, collision)
   - Traffic flow algorithms for NPC drivers
   - Intersection logic (stop signs, traffic lights)

3. **Advanced NPC Systems**
   - Scheduled routines (work, sleep, leisure)
   - Relationship networks (friendships, rivalries)
   - Improved pathfinding with obstacle avoidance

### Future Goals
- Economy system (currency, jobs, trading)
- Housing ownership and customization
- Expanded combat mechanics (weapons, injuries)
- Quest generation framework

*Note: This roadmap is subject to change based on AI performance reviews.*

## How to Play

Use WASD keys to move around the world. Additional controls:
- E: Interact with objects and NPCs
- J: Open journal
- TAB: View character stats
- ESC: Game menu
- F5: Quick save
- F6: Save menu
- F7: Load menu
- F9: Quick load

## Disclaimer
This README was generated by an AI that was instructed to 'be funny.' It failed spectacularly. Please judge the project by its code, not this cringe-worthy documentation.