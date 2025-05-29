import pygame
import sys
import math
import random
from stinkworld.entities.player import Player
from stinkworld.ui.appearance import (
    draw_portrait, FACE_SHAPES, EYE_TYPES, HAIR_STYLES, HAIR_COLORS, CLOTHES,
    SKIN_TONES, VITILIGO_INTENSITIES, generate_vitiligo_patches
)
from stinkworld.utils.debug import debug_log

# Personality traits and their stat effects
PERSONALITY_TRAITS = [
    ("Friendly",     {"book_smarts": 1, "defense": 1, "strength": -1}),
    ("Grumpy",       {"strength": 2, "book_smarts": -1}),
    ("Timid",        {"defense": 2, "strength": -1, "speed": -1}),
    ("Aggressive",   {"strength": 2, "defense": -1}),
    ("Forgiving",    {"book_smarts": 1, "defense": 1, "strength": -1}),
    ("Grudgeful",    {"strength": 1, "speed": 1, "book_smarts": -1}),
    ("Chatty",       {"street_smarts": 2, "defense": -1}),
    ("Quiet",        {"defense": 1, "street_smarts": -1}),
]

def get_hair_offset(face_shape, tile_size):
    """Get the vertical offset for hair based on face shape"""
    if face_shape == 'oval':
        return tile_size//8
    elif face_shape == 'long':
        return tile_size//6
    return 0

def draw_vitiligo_patches(surface, x, y, patches):
    """Draw pre-generated vitiligo patches"""
    patch_color = (255, 255, 255)  # White patches
    for patch_x, patch_y, patch_size in patches:
        pygame.draw.circle(surface, patch_color, (x + patch_x, y + patch_y), patch_size)

def draw_preview(screen, appearance, x, y, size):
    """Draw character preview"""
    preview_surface = pygame.Surface((size, size))
    preview_surface.fill((0, 0, 0))
    draw_portrait(preview_surface, 0, 0, size, appearance)
    screen.blit(preview_surface, (x, y))

def draw_menu_option(screen, font, text, x, y, selected):
    """Draw a menu option with selection highlight"""
    color = (255, 255, 0) if selected else (255, 255, 255)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))
    return y + font.get_height() + 10

def character_creation(screen, settings):
    """Handle character creation process."""
    font = pygame.font.SysFont(None, 36)
    name = ""
    
    # Character creation state
    state = "name"  # States: name, appearance, personality, stats, confirm
    current_option = 0
    
    # Character data
    appearance = {
        'skin_tone': SKIN_TONES['medium'],
        'face_shape': 'round',
        'eye_type': 'bright',
        'hair_style': 'short',
        'hair_color': 'brown',
        'clothes': 'casual',
        'vitiligo': 0.0,
        'vitiligo_patches': []
    }
    
    personality = None
    selected_personality_effects = {}
    stats = {
        'strength': 5,
        'agility': 5,
        'intelligence': 5,
        'charisma': 5,
        'book_smarts': 0,
        'street_smarts': 0
    }
    
    while True:
        screen.fill((0, 0, 0))
        
        # Draw title
        title = font.render("Create Your Character", True, (255, 255, 0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))
        
        # Draw preview
        draw_preview(screen, appearance, screen.get_width() - 250, 100, 200)
        
        if state == "name":
            # Draw name entry
            prompt = font.render("Enter your name:", True, (255, 255, 255))
            screen.blit(prompt, (50, 150))
            
            name_surface = font.render(name + "_", True, (255, 255, 255))
            screen.blit(name_surface, (50, 200))
            
            # Instructions
            inst = font.render("Press ENTER when done", True, (128, 128, 128))
            screen.blit(inst, (50, 250))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name:
                        state = "appearance"
                        current_option = 0
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif len(name) < 20 and event.unicode.isalnum():
                        name += event.unicode
        
        elif state == "appearance":
            y = 150
            options = [
                ("Skin Tone", list(SKIN_TONES.keys())),
                ("Face Shape", FACE_SHAPES),
                ("Eye Type", EYE_TYPES),
                ("Hair Style", HAIR_STYLES),
                ("Hair Color", HAIR_COLORS),
                ("Clothes", CLOTHES),
                ("Vitiligo", VITILIGO_INTENSITIES),
                ("Next", None)
            ]
            
            for i, (option, values) in enumerate(options):
                if values:
                    current_value = appearance[option.lower().replace(" ", "_")]
                    if isinstance(current_value, tuple):  # For skin tone
                        current_value = [k for k, v in SKIN_TONES.items() if v == current_value][0]
                    elif option == "Vitiligo":  # Special handling for vitiligo
                        current_value = current_value  # Just show the float value
                    text = f"{option}: {current_value}"
                else:
                    text = option
                
                y = draw_menu_option(screen, font, text, 50, y, i == current_option)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        current_option = (current_option - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        current_option = (current_option + 1) % len(options)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        if current_option < len(options) - 1:  # Not on "Next"
                            option, values = options[current_option]
                            if values:
                                key = option.lower().replace(" ", "_")
                                if option == "Vitiligo":
                                    current_idx = values.index(appearance[key])
                                    if event.key == pygame.K_LEFT:
                                        new_idx = (current_idx - 1) % len(values)
                                    else:
                                        new_idx = (current_idx + 1) % len(values)
                                    appearance[key] = values[new_idx]
                                    if appearance[key] > 0:
                                        appearance["vitiligo_patches"] = generate_vitiligo_patches(appearance[key], 200)
                                    else:
                                        appearance["vitiligo_patches"] = []
                                else:
                                    if isinstance(appearance[key], tuple):  # For skin tone
                                        current_idx = list(SKIN_TONES.keys()).index([k for k, v in SKIN_TONES.items() if v == appearance[key]][0])
                                        if event.key == pygame.K_LEFT:
                                            new_idx = (current_idx - 1) % len(values)
                                        else:
                                            new_idx = (current_idx + 1) % len(values)
                                        appearance[key] = SKIN_TONES[values[new_idx]]
                                    else:
                                        current_idx = values.index(appearance[key])
                                        if event.key == pygame.K_LEFT:
                                            new_idx = (current_idx - 1) % len(values)
                                        else:
                                            new_idx = (current_idx + 1) % len(values)
                                        appearance[key] = values[new_idx]
                    elif event.key == pygame.K_RETURN:
                        if current_option == len(options) - 1:  # "Next" selected
                            state = "personality"
                            current_option = 0
        
        elif state == "personality":
            y = 150
            for i, (trait, effects) in enumerate(PERSONALITY_TRAITS):
                effect_text = ", ".join(f"{stat}: {mod:+d}" for stat, mod in effects.items())
                text = f"{trait} ({effect_text})"
                y = draw_menu_option(screen, font, text, 50, y, i == current_option)
            
            # Draw trait description if selected
            if personality:
                desc = font.render(f"Selected: {personality}", True, (255, 255, 0))
                screen.blit(desc, (50, y + 20))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        current_option = (current_option - 1) % len(PERSONALITY_TRAITS)
                    elif event.key == pygame.K_DOWN:
                        current_option = (current_option + 1) % len(PERSONALITY_TRAITS)
                    elif event.key == pygame.K_RETURN:
                        personality = PERSONALITY_TRAITS[current_option][0]
                        selected_personality_effects = PERSONALITY_TRAITS[current_option][1]
                        # Apply effects immediately to stats
                        for stat, mod in selected_personality_effects.items():
                            if stat in stats:
                                stats[stat] = max(0, stats[stat] + mod)
                        state = "stats"
                        current_option = 0
        
        elif state == "stats":
            y = 150
            # Set a total points pool (e.g., 30 points)
            total_points = 30
            used_points = sum(stats.values())
            points_left = total_points - used_points
            
            # Draw points remaining
            points_text = font.render(f"Points remaining: {points_left}", True, (255, 255, 0))
            screen.blit(points_text, (50, y))
            y += 40
            
            # Draw stats
            for i, (stat, value) in enumerate(stats.items()):
                text = f"{stat.replace('_', ' ').title()}: {value}"
                y = draw_menu_option(screen, font, text, 50, y, i == current_option)
            
            # Draw "Done" option
            y = draw_menu_option(screen, font, "Done", 50, y, current_option == len(stats))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        current_option = (current_option - 1) % (len(stats) + 1)
                    elif event.key == pygame.K_DOWN:
                        current_option = (current_option + 1) % (len(stats) + 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT) and current_option < len(stats):
                        stat = list(stats.keys())[current_option]
                        if event.key == pygame.K_LEFT and stats[stat] > 0:
                            stats[stat] -= 1
                        elif event.key == pygame.K_RIGHT and points_left > 0 and stats[stat] < 20:
                            stats[stat] += 1
                    elif event.key == pygame.K_RETURN and current_option == len(stats):
                        if points_left == 0:
                            state = "confirm"
                            current_option = 0
        
        elif state == "confirm":
            y = 150
            # Draw character summary
            summary = [
                f"Name: {name}",
                f"Personality: {personality}",
                "Appearance:",
                f"  Face: {appearance['face_shape']} with {appearance['eye_type']} eyes",
                f"  Hair: {appearance['hair_style']} {appearance['hair_color']}",
                f"  Style: {appearance['clothes']} clothes",
                "Stats:",
                *[f"  {stat.replace('_', ' ').title()}: {value}" for stat, value in stats.items()]
            ]
            
            for line in summary:
                text = font.render(line, True, (255, 255, 255))
                screen.blit(text, (50, y))
                y += 30
            
            options = ["Confirm", "Start Over"]
            y += 20
            for i, option in enumerate(options):
                y = draw_menu_option(screen, font, option, 50, y, i == current_option)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        current_option = (current_option - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        current_option = (current_option + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if current_option == 0:  # Confirm
                            player = Player(settings)
                            player.name = name
                            player.appearance = appearance
                            player.personality = personality.lower()
                            # Set stats directly (personality already applied)
                            for stat, value in stats.items():
                                if hasattr(player, stat):
                                    setattr(player, stat, value)
                            return player
                        else:  # Start Over
                            return character_creation(screen, settings)
        
        pygame.display.flip()
