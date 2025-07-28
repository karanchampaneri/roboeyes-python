# RoboEyes Desktop API Documentation

This document provides comprehensive API documentation for developers who want to extend or integrate the RoboEyes Desktop library.

## Table of Contents

1. [Core Classes](#core-classes)
2. [Configuration System](#configuration-system)
3. [Animation System](#animation-system)
4. [Input Handling](#input-handling)
5. [Graphics and Rendering](#graphics-and-rendering)
6. [Platform Compatibility](#platform-compatibility)
7. [Performance Monitoring](#performance-monitoring)
8. [Error Handling](#error-handling)
9. [Extension Points](#extension-points)

## Core Classes

### DesktopRoboEyes

The main class that provides the desktop implementation of RoboEyes.

```python
class DesktopRoboEyes:
    def __init__(self, config: Optional[RoboEyesConfig] = None, 
                 width: int = 128, height: int = 64, frame_rate: int = 20, 
                 window_width: int = 800, window_height: int = 600,
                 bgcolor: int = BGCOLOR, fgcolor: int = FGCOLOR,
                 resizable: bool = True, fullscreen: bool = False)
```

#### Constructor Parameters

- **config**: Optional `RoboEyesConfig` instance for comprehensive configuration
- **width/height**: Eye display dimensions in pixels (overridden by config)
- **frame_rate**: Target animation frame rate (overridden by config)
- **window_width/window_height**: Application window dimensions (overridden by config)
- **bgcolor/fgcolor**: Background and foreground colors (0 or 1)
- **resizable**: Whether the window can be resized (overridden by config)
- **fullscreen**: Whether to start in fullscreen mode (overridden by config)

#### Key Methods

##### Animation Control

```python
def set_auto_blinker(self, active: int, interval: float = None, variation: float = None) -> None:
    """Enable/disable automatic blinking."""

def set_idle_mode(self, active: int, interval: float = None, variation: float = None) -> None:
    """Enable/disable automatic eye movement."""

def blink(self, left: bool = None, right: bool = None) -> None:
    """Trigger manual blink animation."""

def wink(self, left: bool = None, right: bool = None) -> None:
    """Trigger wink animation for specified eye."""

def laugh(self) -> None:
    """Trigger laugh animation (vertical eye movement)."""

def confuse(self) -> None:
    """Trigger confuse animation (horizontal eye shake)."""
```

##### Eye Appearance

```python
def eyes_width(self, leftEye: int = None, rightEye: int = None) -> None:
    """Set width for left and/or right eye."""

def eyes_height(self, leftEye: int = None, rightEye: int = None) -> None:
    """Set height for left and/or right eye."""

def eyes_radius(self, leftEye: int = None, rightEye: int = None) -> None:
    """Set border radius for left and/or right eye."""

def eyes_spacing(self, space: int) -> None:
    """Set space between eyes (can be negative)."""
```

##### Mood and Position

```python
@property
def mood(self) -> int:
    """Get current mood."""

@mood.setter
def mood(self, mood: int) -> None:
    """Set mood (DEFAULT, TIRED, ANGRY, HAPPY, FROZEN, SCARY, CURIOUS)."""

@property
def position(self) -> int:
    """Get current eye position."""

@position.setter
def position(self, direction: int) -> None:
    """Set eye position (N, NE, E, SE, S, SW, W, NW, DEFAULT)."""

@property
def cyclops(self) -> bool:
    """Get cyclops mode state."""

@cyclops.setter
def cyclops(self, enabled: bool) -> None:
    """Enable/disable cyclops mode (single eye)."""
```

##### Window Management

```python
def toggle_fullscreen(self) -> None:
    """Toggle between fullscreen and windowed mode."""

def set_window_size(self, width: int, height: int) -> None:
    """Set window size programmatically."""

def get_window_size(self) -> Tuple[int, int]:
    """Get current window size."""

def get_display_scale(self) -> float:
    """Get current display scaling factor."""

def is_fullscreen(self) -> bool:
    """Check if window is in fullscreen mode."""

def is_minimized(self) -> bool:
    """Check if window is minimized."""

def is_focused(self) -> bool:
    """Check if window has focus."""
```

##### Application Lifecycle

```python
def run(self) -> None:
    """Main application loop."""

def update(self) -> None:
    """Update animation state (called automatically by run())."""

def handle_events(self) -> None:
    """Handle Pygame events (called automatically by run())."""
```

## Configuration System

### RoboEyesConfig

Data class containing all configuration options.

```python
@dataclass
class RoboEyesConfig:
    # Window settings
    window_width: int = 800
    window_height: int = 600
    scale_factor: float = 1.0
    frame_rate: int = 60
    fullscreen: bool = False
    resizable: bool = True
    
    # Eye display settings
    eye_width: int = 36
    eye_height: int = 36
    display_width: int = 128
    display_height: int = 64
    
    # Color settings
    background_color: Tuple[int, int, int] = (0, 0, 0)
    foreground_color: Tuple[int, int, int] = (255, 255, 255)
    
    # Animation settings
    auto_blinker: bool = False
    blink_interval: float = 1.0
    blink_variation: int = 4
    idle_mode: bool = False
    idle_interval: float = 1.0
    idle_variation: int = 3
    
    # Application settings
    config_file: Optional[str] = None
    debug: bool = False
```

### ConfigManager

Handles configuration loading, saving, and validation.

```python
class ConfigManager:
    def __init__(self, config_file: Optional[str] = None)
    
    def load_config(self, config_file: Optional[str] = None) -> RoboEyesConfig:
        """Load configuration from file."""
    
    def save_config(self, config: RoboEyesConfig, config_file: Optional[str] = None) -> None:
        """Save configuration to file."""
    
    def parse_command_line(self, args: Optional[list] = None) -> RoboEyesConfig:
        """Parse command-line arguments and create configuration."""
    
    def update_config(self, **kwargs) -> None:
        """Update configuration with new values."""
```

#### Usage Example

```python
from src.desktop.config import ConfigManager, RoboEyesConfig

# Create and configure
manager = ConfigManager()
config = RoboEyesConfig(
    window_width=1024,
    window_height=768,
    frame_rate=30,
    auto_blinker=True
)

# Save configuration
manager.save_config(config, "my_settings.json")

# Load configuration
loaded_config = manager.load_config("my_settings.json")

# Parse command line
cli_config = manager.parse_command_line()
```

## Animation System

### Sequences

Container for managing multiple animation sequences.

```python
class Sequences:
    def add(self, name: str) -> 'Sequence':
        """Create and add a new sequence."""
    
    def update(self) -> None:
        """Update all active sequences."""
    
    @property
    def done(self) -> bool:
        """Check if all sequences are complete."""
```

### Sequence

Individual animation sequence with timed steps.

```python
class Sequence:
    def step(self, ms_timing: int, _lambda: Callable) -> None:
        """Add a step to execute at specified time."""
    
    def start(self) -> None:
        """Start sequence execution."""
    
    def reset(self) -> None:
        """Reset sequence to initial state."""
    
    @property
    def done(self) -> bool:
        """Check if sequence is complete."""
```

#### Usage Example

```python
# Create a complex animation sequence
seq = robo.sequences.add("greeting")
seq.step(0, lambda r: r.open())
seq.step(500, lambda r: r.set_mood(HAPPY))
seq.step(1000, lambda r: r.wink(right=True))
seq.step(1500, lambda r: r.laugh())
seq.step(2500, lambda r: r.set_mood(DEFAULT))
seq.step(3000, lambda r: r.close())

# Start the sequence
seq.start()

# Check if complete
while not seq.done:
    robo.update()
    time.sleep(0.016)  # ~60 FPS
```

## Input Handling

### InputManager

Handles keyboard and mouse input with customizable mappings.

```python
class InputManager:
    def __init__(self, roboeyes: 'DesktopRoboEyes')
    
    def process_event(self, event: pygame.event.Event) -> bool:
        """Process a Pygame event."""
    
    def add_key_mapping(self, key: int, action: Callable) -> None:
        """Add custom key mapping."""
    
    def add_mouse_mapping(self, button: str, action: Callable) -> None:
        """Add custom mouse mapping."""
    
    def remove_key_mapping(self, key: int) -> None:
        """Remove key mapping."""
    
    def toggle_help(self) -> None:
        """Toggle help display."""
    
    def render_help(self, screen: pygame.Surface) -> None:
        """Render help overlay."""
```

#### Custom Input Example

```python
import pygame

# Add custom key mappings
robo.input_manager.add_key_mapping(
    pygame.K_m,  # M key
    lambda r: r.set_mood(HAPPY)
)

robo.input_manager.add_key_mapping(
    pygame.K_r,  # R key
    lambda r: r.laugh()
)

# Add custom mouse mapping
robo.input_manager.add_mouse_mapping(
    "middle_click",
    lambda r, pos: r.confuse()
)

# Remove default mapping
robo.input_manager.remove_key_mapping(pygame.K_1)
```

## Graphics and Rendering

### FrameBufferCompat

Compatibility layer that wraps Pygame Surface with MicroPython FrameBuffer API.

```python
class FrameBufferCompat:
    def __init__(self, pygame_surface: pygame.Surface, use_optimization: bool = True)
    
    def fill(self, color: int) -> None:
        """Fill the entire buffer with color."""
    
    def pixel(self, x: int, y: int, color: int = None) -> Optional[int]:
        """Get or set pixel color."""
    
    def show(self) -> None:
        """Trigger display update."""
    
    def get_dirty_rects(self) -> List[pygame.Rect]:
        """Get dirty rectangles for optimized updates."""
```

### PygameGraphicsUtil

Graphics utilities for drawing operations.

```python
class PygameGraphicsUtil:
    def __init__(self, surface: pygame.Surface, dirty_tracker: Optional['DirtyRectTracker'] = None)
    
    def fill_rrect(self, x: int, y: int, w: int, h: int, radius: int, color: int) -> None:
        """Draw filled rounded rectangle."""
    
    def fill_triangle(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, color: int) -> None:
        """Draw filled triangle."""
```

## Platform Compatibility

### PlatformCompat

Handles platform-specific optimizations and paths.

```python
class PlatformCompat:
    @property
    def platform(self) -> Platform:
        """Get current platform."""
    
    def get_config_dir(self) -> Path:
        """Get platform-appropriate config directory."""
    
    def get_log_dir(self) -> Path:
        """Get platform-appropriate log directory."""
    
    def apply_pygame_hints(self) -> None:
        """Apply platform-specific Pygame optimizations."""
```

#### Usage Example

```python
from src.desktop.platform_compat import get_platform_compat

platform = get_platform_compat()
print(f"Running on: {platform.platform.value}")

# Get platform-specific directories
config_dir = platform.get_config_dir()
log_dir = platform.get_log_dir()

# Apply optimizations
platform.apply_pygame_hints()
```

## Performance Monitoring

### PerformanceMonitor

Tracks and reports performance metrics.

```python
class PerformanceMonitor:
    def update(self, dirty_rects_count: int = 0, total_pixels_updated: int = 0) -> 'PerformanceMetrics':
        """Update performance metrics."""
    
    def render_performance_overlay(self, screen: pygame.Surface, metrics: 'PerformanceMetrics') -> None:
        """Render performance overlay on screen."""
    
    def log_performance_summary(self) -> None:
        """Log performance summary periodically."""
```

### PerformanceMetrics

Data class containing performance information.

```python
@dataclass
class PerformanceMetrics:
    fps: float
    frame_time_ms: float
    dirty_rects_count: int
    pixels_updated: int
    memory_usage_mb: float
    cpu_usage_percent: float
```

## Error Handling

### Custom Exceptions

```python
class PygameInitializationError(Exception):
    """Raised when Pygame initialization fails."""

class DisplayError(Exception):
    """Raised when display operations fail."""

class WindowError(Exception):
    """Raised when window operations fail."""

class AnimationError(Exception):
    """Raised when animation operations fail."""

class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
```

### Error Handling Example

```python
from src.desktop.exceptions import PygameInitializationError, DisplayError

try:
    robo = DesktopRoboEyes(config=config)
    robo.run()
except PygameInitializationError as e:
    print(f"Failed to initialize graphics: {e}")
    # Handle graphics initialization failure
except DisplayError as e:
    print(f"Display error: {e}")
    # Handle display-related errors
except KeyboardInterrupt:
    print("Application interrupted by user")
```

## Extension Points

### Creating Custom Moods

```python
# Define custom mood constant
CUSTOM_MOOD = 10

# Extend the mood setter
original_mood_setter = DesktopRoboEyes.mood.fset

def custom_mood_setter(self, mood):
    if mood == CUSTOM_MOOD:
        # Custom mood behavior
        self.eyes_width(50, 30)  # Asymmetric eyes
        self.eyes_height(20, 40)
        self.horiz_flicker(True, 5)
    else:
        original_mood_setter(self, mood)

# Replace the mood setter
DesktopRoboEyes.mood = DesktopRoboEyes.mood.setter(custom_mood_setter)
```

### Custom Animation Sequences

```python
class CustomAnimations:
    def __init__(self, roboeyes):
        self.robo = roboeyes
    
    def wave_animation(self):
        """Create a waving animation."""
        seq = self.robo.sequences.add("wave")
        positions = [E, SE, S, SW, W, NW, N, NE, DEFAULT]
        
        for i, pos in enumerate(positions):
            seq.step(i * 200, lambda r, p=pos: r.set_position(p))
        
        seq.start()
    
    def rainbow_mood(self):
        """Cycle through all moods."""
        seq = self.robo.sequences.add("rainbow")
        moods = [DEFAULT, TIRED, ANGRY, HAPPY, FROZEN, SCARY, CURIOUS]
        
        for i, mood in enumerate(moods):
            seq.step(i * 1000, lambda r, m=mood: r.set_mood(m))
        
        seq.start()

# Usage
animations = CustomAnimations(robo)
animations.wave_animation()
animations.rainbow_mood()
```

### Custom Input Handlers

```python
class GamepadInputHandler:
    def __init__(self, roboeyes):
        self.robo = roboeyes
        pygame.joystick.init()
        
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            self.joystick = None
    
    def process_gamepad_input(self):
        """Process gamepad input."""
        if not self.joystick:
            return
        
        # Left stick controls eye position
        x_axis = self.joystick.get_axis(0)
        y_axis = self.joystick.get_axis(1)
        
        if abs(x_axis) > 0.5 or abs(y_axis) > 0.5:
            # Convert analog stick to position
            if x_axis > 0.5 and y_axis < -0.5:
                self.robo.position = NE
            elif x_axis > 0.5 and y_axis > 0.5:
                self.robo.position = SE
            # ... handle other directions
        
        # Buttons trigger animations
        if self.joystick.get_button(0):  # A button
            self.robo.blink()
        if self.joystick.get_button(1):  # B button
            self.robo.laugh()

# Usage
gamepad = GamepadInputHandler(robo)

# In main loop
while robo.running:
    gamepad.process_gamepad_input()
    robo.handle_events()
    robo.update()
```

### Custom Graphics Effects

```python
class EffectsRenderer:
    def __init__(self, roboeyes):
        self.robo = roboeyes
        self.effects = []
    
    def add_particle_effect(self, x, y):
        """Add particle effect at position."""
        self.effects.append({
            'type': 'particles',
            'x': x, 'y': y,
            'life': 60,  # frames
            'particles': [(random.randint(-5, 5), random.randint(-5, 5)) for _ in range(10)]
        })
    
    def render_effects(self, screen):
        """Render all active effects."""
        for effect in self.effects[:]:  # Copy list to allow modification
            if effect['type'] == 'particles':
                self._render_particles(screen, effect)
                effect['life'] -= 1
                if effect['life'] <= 0:
                    self.effects.remove(effect)
    
    def _render_particles(self, screen, effect):
        """Render particle effect."""
        for i, (dx, dy) in enumerate(effect['particles']):
            alpha = effect['life'] / 60.0
            x = effect['x'] + dx * (60 - effect['life']) / 10
            y = effect['y'] + dy * (60 - effect['life']) / 10
            
            # Draw particle with fading alpha
            color = (255, 255, 255, int(255 * alpha))
            pygame.draw.circle(screen, color[:3], (int(x), int(y)), 2)

# Usage
effects = EffectsRenderer(robo)

# Override the display update to include effects
original_show = robo._pygame_show

def enhanced_show(roboeyes_instance):
    original_show(roboeyes_instance)
    effects.render_effects(robo.screen)
    
robo._pygame_show = enhanced_show
```

This API documentation provides comprehensive coverage of the RoboEyes Desktop library's extensibility points and advanced usage patterns. Developers can use these examples as starting points for creating custom behaviors, animations, and integrations.