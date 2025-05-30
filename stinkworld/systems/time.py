"""Time system module."""
import time
import pygame
from datetime import datetime, timedelta
from stinkworld.utils.debug import debug_log

class TimeSystem:
    """Manages game time and day/night cycle."""
    
    def __init__(self):
        """Initialize time system."""
        self.current_minute = 0  # Minutes since game start
        self.last_update = time.time()
        
        # Time constants
        self.MINUTES_PER_HOUR = 60
        self.HOURS_PER_DAY = 24
        self.MINUTES_PER_DAY = self.MINUTES_PER_HOUR * self.HOURS_PER_DAY
        
        # --- Lighting values for each time of day (used by get_lighting_color) ---
        # Format: (R, G, B, alpha)
        self.lighting = {
            'day': (0, 0, 0, 0),         # No overlay during day
            'dawn': (80, 60, 40, 60),    # Warm, soft overlay
            'dusk': (60, 40, 80, 80),    # Cool, purple overlay
            'night': (0, 0, 0, 128)      # Dark overlay at night
        }
    
    def update(self):
        """Update game time."""
        current_time = time.time()
        elapsed = current_time - self.last_update
        self.last_update = current_time
        
        # Update game minutes (1 real second = 1 game minute)
        self.current_minute = (self.current_minute + int(elapsed)) % self.MINUTES_PER_DAY
    
    @property
    def hour(self):
        """Get current hour (0-23)."""
        return (self.current_minute // self.MINUTES_PER_HOUR) % self.HOURS_PER_DAY
    
    @property
    def minute(self):
        """Get current minute (0-59)."""
        return self.current_minute % self.MINUTES_PER_HOUR
    
    @property
    def is_night(self):
        """Check if it's nighttime (8 PM - 6 AM)."""
        return self.hour >= 20 or self.hour < 6
    
    @property
    def is_dawn(self):
        """Check if it's dawn (5 AM - 7 AM)."""
        return 5 <= self.hour < 7
    
    @property
    def is_dusk(self):
        """Check if it's dusk (6 PM - 8 PM)."""
        return 18 <= self.hour < 20
    
    def get_time_string(self):
        """Get formatted time string (HH:MM)."""
        return f"{self.hour:02d}:{self.minute:02d}"
    
    def get_current_datetime(self):
        """Get the current in-game date and time."""
        minutes_passed = self.current_minute
        return datetime(2024, 1, 1, 6, 0) + timedelta(minutes=minutes_passed)
    
    def get_time_of_day(self):
        """Get the current time of day (dawn, day, dusk, or night)."""
        current_time = self.get_current_datetime().hour
        
        if 5 <= current_time < 7:    # Dawn: 5 AM - 7 AM
            return 'dawn'
        elif 7 <= current_time < 18:  # Day: 7 AM - 6 PM
            return 'day'
        elif 18 <= current_time < 20: # Dusk: 6 PM - 8 PM
            return 'dusk'
        else:                         # Night: 8 PM - 5 AM
            return 'night'
    
    def get_lighting_color(self):
        """Get the current lighting color based on time of day."""
        # --- Use self.lighting dict, fallback to day if missing ---
        tod = self.get_time_of_day()
        return self.lighting.get(tod, (0, 0, 0, 0))
    
    def format_time(self):
        """Format the current time as HH:MM."""
        return self.get_time_string()
    
    def format_date(self):
        """Format the current date."""
        day = (self.current_minute // self.MINUTES_PER_DAY) + 1
        return f"Day {day}"
    
    def apply_lighting(self, screen):
        """Apply lighting effects based on time of day."""
        hour = self.hour
        
        # Night time (10 PM - 5 AM)
        if hour >= 22 or hour < 5:
            darkness = pygame.Surface(screen.get_size())
            darkness.fill((0, 0, 0))
            darkness.set_alpha(128)  # 50% darkness
            screen.blit(darkness, (0, 0))
            
        # Dawn/Dusk (5-6 AM and 9-10 PM)
        elif hour in [5, 21]:
            darkness = pygame.Surface(screen.get_size())
            darkness.fill((0, 0, 0))
            darkness.set_alpha(64)  # 25% darkness
            screen.blit(darkness, (0, 0))
    
    def get_weather(self):
        """Get current weather based on time and random factors."""
        # TODO: Implement weather system
        return "Clear"
    
    def advance_time(self):
        """Advance time by one turn (only called when player acts)."""
        self.current_minute = (self.current_minute + 1) % self.MINUTES_PER_DAY
        debug_log(f"[TimeSystem] Time advanced to {self.get_time_string()}")
    
    def get_current_day(self):
        """Return the current in-game day number (starting from 1)."""
        return (self.current_minute // self.MINUTES_PER_DAY) + 1