import pygame
import random
import math
import time
from stinkworld.utils.debug import debug_log

# Options for portrait customization
FACE_SHAPES = ['round', 'square', 'oval', 'long']
EYE_TYPES = ['bright', 'dull', 'piercing', 'gentle']
HAIR_STYLES = ['short', 'long', 'curly', 'straight', 'messy', 'neatly combed']
HAIR_COLORS = ['blonde', 'brown', 'black', 'red', 'gray']
CLOTHES = ['casual', 'formal', 'worn-out', 'colorful', 'plain']

# Skin tones dictionary
SKIN_TONES = {
    'very_light': (255, 224, 196),
    'light': (255, 205, 148),
    'medium_light': (234, 192, 134),
    'medium': (224, 172, 105),
    'medium_dark': (141, 85, 36),
    'dark': (89, 47, 23),
    'very_dark': (62, 29, 19),
    'rainbow': 'rainbow'  # Special value for rainbow skin
}

# Vitiligo options
VITILIGO_INTENSITIES = {
    'none': 0.0,
    'mild': 0.2,
    'moderate': 0.4,
    'severe': 0.7,
    'complete': 1.0
}

def get_hair_offset(face_shape, tile_size):
    """Get the vertical offset for hair based on face shape"""
    if face_shape == 'oval':
        return tile_size//8
    elif face_shape == 'long':
        return tile_size//6
    return 0

def generate_vitiligo_patches(tile_size, intensity, face_shape):
    """Generate static vitiligo patch positions"""
    if intensity <= 0:
        return []
        
    patches = []
    num_patches = int(10 * intensity)
    
    for _ in range(num_patches):
        patch_x = random.randint(0, tile_size)
        patch_y = random.randint(0, tile_size)
        patch_size = random.randint(tile_size//10, tile_size//4)
        
        # Adjust patch position based on face shape
        if face_shape == 'oval':
            if patch_y < tile_size//8 or patch_y > tile_size*7//8:
                continue
        elif face_shape == 'long':
            if patch_y < tile_size//6 or patch_y > tile_size*5//6:
                continue
            
        patches.append((patch_x, patch_y, patch_size))
    
    return patches

def draw_vitiligo_patches(surface, x, y, patches):
    """Draw pre-generated vitiligo patches"""
    patch_color = (255, 255, 255)  # White patches
    for patch_x, patch_y, patch_size in patches:
        pygame.draw.circle(surface, patch_color, (x + patch_x, y + patch_y), patch_size)

def draw_portrait(surface, x, y, tile_size, appearance):
    # Get base skin color
    if isinstance(appearance['skin_tone'], str) and appearance['skin_tone'] == 'rainbow':
        t = time.time() * 2
        face_color = (
            int((math.sin(t) + 1) * 127),
            int((math.sin(t + 2*math.pi/3) + 1) * 127),
            int((math.sin(t + 4*math.pi/3) + 1) * 127)
        )
    else:
        face_color = appearance['skin_tone']

    hair_colors = {
        'blonde': (240, 220, 120),
        'brown': (120, 80, 40),
        'black': (30, 30, 30),
        'red': (180, 60, 30),
        'gray': (180, 180, 180)
    }
    hair_color = hair_colors.get(appearance['hair_color'], (120, 80, 40))
    
    # Face shape with proper offsets
    face_rect = pygame.Rect(x, y, tile_size, tile_size)
    if appearance['face_shape'] == 'round':
        pygame.draw.ellipse(surface, face_color, face_rect)
    elif appearance['face_shape'] == 'square':
        pygame.draw.rect(surface, face_color, face_rect)
    elif appearance['face_shape'] == 'oval':
        pygame.draw.ellipse(surface, face_color, (x, y+tile_size//8, tile_size, tile_size*3//4))
    else:  # long
        pygame.draw.ellipse(surface, face_color, (x, y+tile_size//6, tile_size, tile_size*2//3))

    # Add vitiligo if specified
    if 'vitiligo_patches' in appearance:
        draw_vitiligo_patches(surface, x, y, appearance['vitiligo_patches'])

    # Hair style with dynamic positioning
    hair_y = y - get_hair_offset(appearance['face_shape'], tile_size)
    if appearance['hair_style'] == 'short':
        pygame.draw.rect(surface, hair_color, (x, hair_y, tile_size, tile_size//4))
    elif appearance['hair_style'] == 'long':
        pygame.draw.rect(surface, hair_color, (x, hair_y, tile_size, tile_size//2))
        pygame.draw.rect(surface, hair_color, (x, y+tile_size//2, tile_size, tile_size//3))
    elif appearance['hair_style'] == 'curly':
        for i in range(5):
            pygame.draw.circle(surface, hair_color, (x+tile_size//5+i*tile_size//6, hair_y+tile_size//8), tile_size//6)
    elif appearance['hair_style'] == 'straight':
        pygame.draw.rect(surface, hair_color, (x, hair_y, tile_size, tile_size//3))
    elif appearance['hair_style'] == 'messy':
        for i in range(4):
            height = random.randint(tile_size//6, tile_size//4)
            pygame.draw.rect(surface, hair_color, (x+i*tile_size//4, hair_y, tile_size//4, height))
    elif appearance['hair_style'] == 'neatly combed':
        pygame.draw.rect(surface, hair_color, (x, hair_y, tile_size, tile_size//4))
        pygame.draw.line(surface, (220,220,220), (x, hair_y+tile_size//5), (x+tile_size, hair_y+tile_size//5), 2)

    # Eyes
    eye_color = (40, 40, 40)
    if appearance['eye_type'] == 'bright':
        eye_color = (200, 200, 255)
    elif appearance['eye_type'] == 'dull':
        eye_color = (100, 100, 120)
    elif appearance['eye_type'] == 'piercing':
        eye_color = (0, 80, 180)
    elif appearance['eye_type'] == 'gentle':
        eye_color = (120, 180, 120)
    
    eye_y = y + tile_size//2
    eye_spacing = tile_size//3
    eye_r = tile_size//10
    pygame.draw.circle(surface, eye_color, (x+eye_spacing, eye_y), eye_r)
    pygame.draw.circle(surface, eye_color, (x+tile_size-eye_spacing, eye_y), eye_r)

    # Mouth
    mouth_y = y + tile_size*2//3
    mouth_w = tile_size//3
    mouth_h = tile_size//10
    mouth_x = x + tile_size//2 - mouth_w//2
    pygame.draw.rect(surface, (120,0,0), (mouth_x, mouth_y, mouth_w, mouth_h))

    # Clothes
    clothes_colors = {
        'casual': (100, 180, 220),
        'formal': (60, 60, 80),
        'worn-out': (120, 120, 80),
        'colorful': (220, 120, 180),
        'plain': (180, 180, 180)
    }
    pygame.draw.rect(surface, clothes_colors.get(appearance['clothes'], (180,180,180)), (x, y+tile_size-8, tile_size, 8))

def generate_npc_appearance(tile_size=32):
    """Generate a random, unique appearance for an NPC."""
    skin_tone_key = random.choice([k for k in SKIN_TONES.keys() if k != 'rainbow'])
    skin_tone = SKIN_TONES[skin_tone_key]
    face_shape = random.choice(FACE_SHAPES)
    eye_type = random.choice(EYE_TYPES)
    # Exclude 'bald' if present, and always pick a visible hair style
    visible_hair_styles = [h for h in HAIR_STYLES if h != 'bald']
    hair_style = random.choice(visible_hair_styles)
    hair_color = random.choice(HAIR_COLORS)
    clothes = random.choice(CLOTHES)
    # Vitiligo
    vitiligo_key = random.choice(list(VITILIGO_INTENSITIES.keys()))
    vitiligo = VITILIGO_INTENSITIES[vitiligo_key]
    if vitiligo > 0:
        vitiligo_patches = generate_vitiligo_patches(tile_size, vitiligo, face_shape)
    else:
        vitiligo_patches = []
    return {
        'skin_tone': skin_tone,
        'face_shape': face_shape,
        'eye_type': eye_type,
        'hair_style': hair_style,
        'hair_color': hair_color,
        'clothes': clothes,
        'vitiligo': vitiligo,
        'vitiligo_patches': vitiligo_patches
    }