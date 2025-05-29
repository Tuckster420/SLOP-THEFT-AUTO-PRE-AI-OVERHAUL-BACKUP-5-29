"""Traffic system module."""
import pygame
from stinkworld.core.settings import (
    TILE_SIZE, COLOR_TRAFFIC_GREEN, COLOR_TRAFFIC_YELLOW, COLOR_TRAFFIC_RED,
    GREEN_TIME, YELLOW_TIME, RED_TIME
)
from stinkworld.utils.debug import debug_log

class TrafficLight:
    """Traffic light class."""
    
    def __init__(self, x, y):
        """Initialize traffic light."""
        self.x = x
        self.y = y
        self.state = 'green'  # green, yellow, red
        self.timer = 0
        self.GREEN_TIME = GREEN_TIME
        self.YELLOW_TIME = YELLOW_TIME
        self.RED_TIME = RED_TIME
    
    def update(self):
        """Update traffic light state."""
        self.timer += 1
        
        if self.state == 'green' and self.timer >= self.GREEN_TIME:
            self.state = 'yellow'
            self.timer = 0
        elif self.state == 'yellow' and self.timer >= self.YELLOW_TIME:
            self.state = 'red'
            self.timer = 0
        elif self.state == 'red' and self.timer >= self.RED_TIME:
            self.state = 'green'
            self.timer = 0
    
    def draw(self, screen, camera_x, camera_y):
        """Draw traffic light."""
        screen_x = (self.x - camera_x) * TILE_SIZE
        screen_y = (self.y - camera_y) * TILE_SIZE
        
        # Draw light based on state
        if self.state == 'green':
            color = COLOR_TRAFFIC_GREEN
        elif self.state == 'yellow':
            color = COLOR_TRAFFIC_YELLOW
        else:  # red
            color = COLOR_TRAFFIC_RED
        
        rect = pygame.Rect(
            screen_x + TILE_SIZE//4,
            screen_y + TILE_SIZE//4,
            TILE_SIZE//2, TILE_SIZE//2
        )
        pygame.draw.rect(screen, color, rect)

    def is_red(self):
        return self.state == 'red'