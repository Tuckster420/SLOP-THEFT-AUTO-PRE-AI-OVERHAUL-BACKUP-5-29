"""Common utility functions."""
import random
import math
from stinkworld.utils.debug import debug_log

def distance(x1, y1, x2, y2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def manhattan_distance(x1, y1, x2, y2):
    """Calculate Manhattan distance between two points."""
    return abs(x2 - x1) + abs(y2 - y1)

def random_chance(probability):
    """Return True with given probability (0.0 to 1.0)."""
    return random.random() < probability

def clamp(value, min_val, max_val):
    """Clamp a value between min and max values."""
    return max(min_val, min(max_val, value))

def lerp(start, end, t):
    """Linear interpolation between start and end values."""
    return start + (end - start) * t

def format_time(minutes):
    """Format minutes into HH:MM format."""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"