"""Weather system module."""
import random
from datetime import datetime
from stinkworld.utils.debug import debug_log

class WeatherSystem:
    """Manages game weather conditions."""
    
    def __init__(self):
        """Initialize weather system."""
        self.weather_types = {
            'clear': {
                'name': 'Clear',
                'lighting_mod': (0, 0, 0, 0),
                'movement_penalty': 0,
                'visibility_reduction': 0
            },
            'cloudy': {
                'name': 'Cloudy',
                'lighting_mod': (0, 0, 0, 30),
                'movement_penalty': 0,
                'visibility_reduction': 1
            },
            'rain': {
                'name': 'Rain',
                'lighting_mod': (-20, -20, -20, 40),
                'movement_penalty': 1,
                'visibility_reduction': 2,
                'particles': 'rain'
            },
            'storm': {
                'name': 'Storm',
                'lighting_mod': (-40, -40, -40, 60),
                'movement_penalty': 2,
                'visibility_reduction': 3,
                'particles': 'rain',
                'lightning': True
            },
            'fog': {
                'name': 'Fog',
                'lighting_mod': (50, 50, 50, 70),
                'movement_penalty': 1,
                'visibility_reduction': 4,
                'particles': 'fog'
            },
            'snow': {
                'name': 'Snow',
                'lighting_mod': (100, 100, 100, 20),
                'movement_penalty': 2,
                'visibility_reduction': 2,
                'particles': 'snow'
            }
        }
        
        self.current_weather = 'clear'
        self.weather_duration = 0  # How many more turns this weather will last
        self.particles = []  # List to store active weather particles
        
        # Season-based weather probabilities
        self.seasonal_weights = {
            'spring': {
                'clear': 0.4, 'cloudy': 0.3, 'rain': 0.2, 'storm': 0.05, 'fog': 0.05
            },
            'summer': {
                'clear': 0.6, 'cloudy': 0.2, 'rain': 0.1, 'storm': 0.1
            },
            'fall': {
                'clear': 0.3, 'cloudy': 0.4, 'rain': 0.2, 'fog': 0.1
            },
            'winter': {
                'clear': 0.3, 'cloudy': 0.3, 'snow': 0.3, 'fog': 0.1
            }
        }
    
    def get_season(self, current_date):
        """Determine the current season based on the date."""
        month = current_date.month
        if 3 <= month <= 5:
            return 'spring'
        elif 6 <= month <= 8:
            return 'summer'
        elif 9 <= month <= 11:
            return 'fall'
        else:
            return 'winter'
    
    def update_weather(self, current_date):
        """Update weather conditions based on time and season."""
        if self.weather_duration <= 0:
            season = self.get_season(current_date)
            weights = self.seasonal_weights[season]
            
            # Filter out impossible weather types for the season
            possible_weather = {k: v for k, v in weights.items() if k in self.weather_types}
            
            # Normalize weights
            total = sum(possible_weather.values())
            normalized_weights = {k: v/total for k, v in possible_weather.items()}
            
            # Choose new weather
            self.current_weather = random.choices(
                list(normalized_weights.keys()),
                list(normalized_weights.values())
            )[0]
            
            # Set duration (2-8 hours in turns)
            self.weather_duration = random.randint(8, 32)  # 2-8 hours (4 turns per hour)
        else:
            self.weather_duration -= 1
    
    def get_current_weather(self):
        """Get current weather data."""
        return self.weather_types[self.current_weather]
    
    def apply_weather_effects(self, screen, time_of_day_lighting):
        """Apply weather effects to the screen."""
        weather = self.get_current_weather()
        
        # Apply weather lighting modification
        mod = weather['lighting_mod']
        final_color = (
            max(0, min(255, time_of_day_lighting[0] + mod[0])),
            max(0, min(255, time_of_day_lighting[1] + mod[1])),
            max(0, min(255, time_of_day_lighting[2] + mod[2])),
            max(0, min(255, time_of_day_lighting[3] + mod[3]))
        )
        
        overlay = pygame.Surface(screen.get_size())
        overlay.fill(final_color[:3])
        overlay.set_alpha(final_color[3])
        screen.blit(overlay, (0, 0))
        
        # Update and draw weather particles
        if 'particles' in weather:
            self.update_particles(screen, weather['particles'])
    
    def update_particles(self, screen, particle_type):
        """Update and draw weather particles."""
        # Add new particles
        if len(self.particles) < 100:  # Maintain 100 particles
            if particle_type == 'rain':
                self.particles.append({
                    'x': random.randint(0, screen.get_width()),
                    'y': random.randint(-20, 0),
                    'speed': random.randint(10, 20),
                    'length': random.randint(5, 15)
                })
            elif particle_type == 'snow':
                self.particles.append({
                    'x': random.randint(0, screen.get_width()),
                    'y': random.randint(-20, 0),
                    'speed': random.randint(1, 3),
                    'size': random.randint(2, 4)
                })
            elif particle_type == 'fog':
                self.particles.append({
                    'x': random.randint(0, screen.get_width()),
                    'y': random.randint(0, screen.get_height()),
                    'size': random.randint(20, 50),
                    'alpha': random.randint(20, 60)
                })
        
        # Update existing particles
        for particle in self.particles[:]:
            if particle_type == 'rain':
                particle['y'] += particle['speed']
                pygame.draw.line(screen, (200, 200, 255),
                               (particle['x'], particle['y']),
                               (particle['x'], particle['y'] + particle['length']))
                if particle['y'] > screen.get_height():
                    self.particles.remove(particle)
            
            elif particle_type == 'snow':
                particle['y'] += particle['speed']
                particle['x'] += random.randint(-1, 1)
                pygame.draw.circle(screen, (255, 255, 255),
                                 (int(particle['x']), int(particle['y'])),
                                 particle['size'])
                if particle['y'] > screen.get_height():
                    self.particles.remove(particle)
            
            elif particle_type == 'fog':
                fog_surface = pygame.Surface((particle['size'], particle['size']))
                fog_surface.fill((200, 200, 200))
                fog_surface.set_alpha(particle['alpha'])
                screen.blit(fog_surface, (particle['x'], particle['y']))
                
                # Slowly move fog
                particle['x'] += random.randint(-1, 1)
                particle['y'] += random.randint(-1, 1)
                if not (0 <= particle['x'] <= screen.get_width() and
                       0 <= particle['y'] <= screen.get_height()):
                    self.particles.remove(particle)
    
    def update(self):
        """Update weather conditions."""
        self.weather_duration -= 1
        
        if self.weather_duration <= 0:
            self._change_weather()
    
    def _change_weather(self):
        """Change weather to a new random condition."""
        # Don't pick the same condition
        possible_conditions = [c for c in self.weather_types if c != self.current_weather]
        self.current_weather = random.choice(possible_conditions)
        
        # Set new duration (2-8 hours in turns)
        self.weather_duration = random.randint(8, 32)  # 2-8 hours (4 turns per hour)
    
    def get_visibility(self):
        """Get current visibility factor (0.0-1.0)."""
        weather = self.get_current_weather()
        return 1.0 - weather['visibility_reduction'] / 4.0
    
    def get_movement_penalty(self):
        """Get current movement speed penalty (0.0-1.0)."""
        weather = self.get_current_weather()
        return weather['movement_penalty'] / 2.0
    
    def get_description(self):
        """Get weather description string."""
        weather = self.get_current_weather()
        return f"Weather: {weather['name']}"