"""Appearance module for character customization."""
import pygame
import random

# Appearance options
FACE_SHAPES = ['round', 'oval', 'square', 'heart', 'long']
EYE_TYPES = ['bright', 'dark', 'narrow', 'wide', 'almond']
HAIR_STYLES = ['short', 'long', 'curly', 'spiky', 'bald', 'ponytail']
HAIR_COLORS = ['black', 'brown', 'blonde', 'red', 'gray', 'white']
CLOTHES = ['casual', 'formal', 'sporty', 'punk', 'fancy']
SKIN_TONES = {
    'light': (255, 220, 178),
    'medium': (255, 198, 140),
    'dark': (141, 85, 36),
    'olive': (198, 134, 66),
    'pale': (255, 236, 204)
}
VITILIGO_INTENSITIES = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

def generate_vitiligo_patches(intensity, size):
    """Generate vitiligo patch locations based on intensity."""
    patches = []
    num_patches = int(intensity * 10)  # More patches for higher intensity
    for _ in range(num_patches):
        x = random.randint(0, size)
        y = random.randint(0, size)
        patch_size = random.randint(1, 3)
        patches.append((x, y, patch_size))
    return patches

def draw_portrait(surface, x, y, size, appearance):
    """Draw a character portrait based on appearance settings."""
    # Assume surface is already created by caller, do NOT fill or recreate it here!
    skin_tone = appearance.get('skin_tone', SKIN_TONES['medium'])
    face_shape = appearance.get('face_shape', 'round')
    # Draw face shape as the main face
    if face_shape == 'round':
        face_rect = (x + size//8, y + size//8, size*3//4, size*3//4)
        pygame.draw.ellipse(surface, skin_tone, face_rect)
        vitiligo_area = face_rect
    elif face_shape == 'oval':
        face_rect = (x + size//4, y + size//8, size//2, size*3//4)
        pygame.draw.ellipse(surface, skin_tone, face_rect)
        vitiligo_area = face_rect
    elif face_shape == 'square':
        face_rect = (x + size//4, y + size//4, size//2, size//2)
        pygame.draw.rect(surface, skin_tone, face_rect)
        vitiligo_area = face_rect
    elif face_shape == 'heart':
        points = [
            (x + size//2, y + size//4),
            (x + size*3//4, y + size//2),
            (x + size//2, y + size*3//4),
            (x + size//4, y + size//2)
        ]
        pygame.draw.polygon(surface, skin_tone, points)
        vitiligo_area = (x + size//4, y + size//4, size//2, size//2)
    elif face_shape == 'long':
        face_rect = (x + size//3, y + size//8, size//3, size*3//4)
        pygame.draw.ellipse(surface, skin_tone, face_rect)
        vitiligo_area = face_rect
    # Draw vitiligo patches if any, fit to face shape
    if appearance.get('vitiligo', 0.0) > 0:
        patches = appearance.get('vitiligo_patches', [])
        vx, vy, vw, vh = vitiligo_area
        for patch_x, patch_y, patch_size in patches:
            px = vx + int(patch_x * vw / size)
            py = vy + int(patch_y * vh / size)
            ps = max(1, int(patch_size * min(vw, vh) / size))
            pygame.draw.circle(surface, (255, 255, 255), (px, py), ps)
    
    # Draw eyes
    eye_type = appearance.get('eye_type', 'bright')
    eye_color = (0, 0, 0)  # Default black
    eye_size = size // 8
    left_eye_x = x + size // 3 - eye_size // 2
    right_eye_x = x + size * 2 // 3 - eye_size // 2
    eye_y = y + size // 2 - eye_size // 2
    if eye_type == 'bright':
        eye_color = (60, 60, 60)
        pygame.draw.ellipse(surface, eye_color, (left_eye_x, eye_y, eye_size, eye_size))
        pygame.draw.ellipse(surface, eye_color, (right_eye_x, eye_y, eye_size, eye_size))
        pygame.draw.ellipse(surface, (255,255,255), (left_eye_x+eye_size//4, eye_y+eye_size//4, eye_size//2, eye_size//2))
        pygame.draw.ellipse(surface, (255,255,255), (right_eye_x+eye_size//4, eye_y+eye_size//4, eye_size//2, eye_size//2))
    elif eye_type == 'dark':
        eye_color = (20, 20, 20)
        pygame.draw.ellipse(surface, eye_color, (left_eye_x, eye_y, eye_size, eye_size))
        pygame.draw.ellipse(surface, eye_color, (right_eye_x, eye_y, eye_size, eye_size))
    elif eye_type == 'narrow':
        eye_color = (0, 0, 0)
        pygame.draw.ellipse(surface, eye_color, (left_eye_x, eye_y + eye_size//3, eye_size, eye_size//3))
        pygame.draw.ellipse(surface, eye_color, (right_eye_x, eye_y + eye_size//3, eye_size, eye_size//3))
    elif eye_type == 'wide':
        eye_color = (0, 0, 0)
        pygame.draw.ellipse(surface, eye_color, (left_eye_x - eye_size//4, eye_y, eye_size + eye_size//2, eye_size))
        pygame.draw.ellipse(surface, eye_color, (right_eye_x - eye_size//4, eye_y, eye_size + eye_size//2, eye_size))
    elif eye_type == 'almond':
        eye_color = (0, 0, 0)
        pygame.draw.ellipse(surface, eye_color, (left_eye_x, eye_y + eye_size//6, eye_size, eye_size//1.5))
        pygame.draw.ellipse(surface, eye_color, (right_eye_x, eye_y + eye_size//6, eye_size, eye_size//1.5))
    
    # Draw hair
    hair_style = appearance.get('hair_style', 'short')
    hair_color_name = appearance.get('hair_color', 'brown')
    hair_colors = {
        'black': (0, 0, 0),
        'brown': (139, 69, 19),
        'blonde': (255, 215, 0),
        'red': (255, 0, 0),
        'gray': (128, 128, 128),
        'white': (255, 255, 255)
    }
    hair_color = hair_colors.get(hair_color_name, (0, 0, 0))
    
    if hair_style != 'bald':
        if hair_style == 'short':
            pygame.draw.rect(surface, hair_color,
                           (x + size//4, y, size//2, size//4))
        elif hair_style == 'long':
            pygame.draw.rect(surface, hair_color,
                           (x + size//4, y, size//2, size*2//3))
        elif hair_style == 'curly':
            for i in range(4):
                pygame.draw.circle(surface, hair_color,
                                (x + size//3 + (i * size//6),
                                 y + size//4), size//8)
        elif hair_style == 'spiky':
            points = [(x + size//4, y + size//4)]
            for i in range(5):
                points.append((x + size//4 + (i * size//6), y))
                points.append((x + size//4 + (i * size//6), y + size//4))
            pygame.draw.polygon(surface, hair_color, points)
        elif hair_style == 'ponytail':
            pygame.draw.rect(surface, hair_color,
                           (x + size//4, y, size//2, size//4))
            pygame.draw.rect(surface, hair_color,
                           (x + size*2//3, y + size//4, size//6, size//2))
    
    # Draw clothes
    clothes_type = appearance.get('clothes', 'casual')
    clothes_colors = {
        'casual': (0, 0, 255),  # Blue
        'formal': (0, 0, 0),    # Black
        'sporty': (255, 0, 0),  # Red
        'punk': (128, 0, 128),  # Purple
        'fancy': (218, 165, 32) # Goldenrod
    }
    clothes_color = clothes_colors.get(clothes_type, (0, 0, 255))
    pygame.draw.rect(surface, clothes_color,
                    (x, y + size*3//4, size, size//4))