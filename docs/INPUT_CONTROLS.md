# RoboEyes Desktop Input Controls

This document describes the comprehensive keyboard and mouse controls available in the RoboEyes desktop application, along with customization options for developers.

## Quick Reference Card

| Action | Key(s) | Description |
|--------|--------|-------------|
| **Moods** | 1-7 | Change eye mood expressions |
| **Movement** | Arrow Keys, WASD | Move eyes in 4 directions |
| **Positioning** | Numpad 1-9 | Precise 9-direction positioning |
| **Blink** | Space | Blink both eyes |
| **Wink** | Q, E | Wink left or right eye |
| **Animations** | C, L | Confuse or laugh animations |
| **Eye State** | O, X | Open or close eyes |
| **Auto Modes** | B, I | Toggle auto-blinker or idle mode |
| **Special Modes** | Y, R | Toggle cyclops or curious mode |
| **Help** | H, F1 | Show/hide control help |
| **Fullscreen** | F11, Esc | Toggle or exit fullscreen |
| **Mouse Look** | Left Click | Make eyes look at cursor |
| **Mouse Blink** | Right Click | Trigger blink animation |

## Detailed Keyboard Controls

### Mood Changes
Transform the personality and expression of the eyes:

- **1** - **Default mood**: Normal, alert expression
- **2** - **Tired mood**: Droopy eyelids, sleepy appearance
- **3** - **Angry mood**: Angled eyebrows, stern expression
- **4** - **Happy mood**: Curved bottom eyelids, cheerful look
- **5** - **Frozen mood**: Slight horizontal shaking, cold/scared
- **6** - **Scary mood**: Partially closed with vertical shaking
- **7** - **Curious mood**: Eyes enlarge when looking left/right

### Eye Positioning
Control where the eyes are looking:

#### Basic Movement
- **↑ (Up Arrow)** - Look up (North)
- **↓ (Down Arrow)** - Look down (South)  
- **← (Left Arrow)** - Look left (West)
- **→ (Right Arrow)** - Look right (East)

#### Alternative Movement (WASD)
- **W** - Look up (North)
- **S** - Look down (South)
- **A** - Look left (West)
- **D** - Look right (East)

#### Precise Positioning (Numpad)
Use the numeric keypad for 9-direction positioning:
```
7 8 9    NW  N  NE
4 5 6  = W  CTR  E
1 2 3    SW  S  SE
```
- **Numpad 7** - Northwest
- **Numpad 8** - North  
- **Numpad 9** - Northeast
- **Numpad 4** - West
- **Numpad 5** - Center (default position)
- **Numpad 6** - East
- **Numpad 1** - Southwest
- **Numpad 2** - South
- **Numpad 3** - Southeast

### Animation Controls
Trigger specific eye animations:

- **SPACE** - **Blink both eyes**: Quick close and open
- **Q** - **Wink left eye**: Left eye closes briefly
- **E** - **Wink right eye**: Right eye closes briefly
- **C** - **Confuse animation**: Rapid horizontal shaking (500ms)
- **L** - **Laugh animation**: Vertical bouncing motion (500ms)

### Eye State Controls
Manually control eye open/closed state:

- **O** - **Open eyes**: Force eyes to open position
- **X** - **Close eyes**: Force eyes to closed position

*Note: Auto-blinker should be disabled when using manual eye state controls*

### Automatic Behavior Toggles
Control automated eye behaviors:

- **B** - **Toggle auto-blinker**: Enable/disable automatic blinking
- **I** - **Toggle idle mode**: Enable/disable automatic eye movement
- **Y** - **Toggle cyclops mode**: Switch between two eyes and single eye
- **R** - **Toggle curious mode**: Enable/disable size changes when looking sideways

### Window and System Controls
Manage the application window and interface:

- **H** - **Toggle help display**: Show/hide control reference overlay
- **F1** - **Alternative help toggle**: Same as H key
- **F11** - **Toggle fullscreen**: Switch between windowed and fullscreen
- **ESC** - **Exit fullscreen**: Return to windowed mode (only in fullscreen)

## Mouse Controls

### Interactive Eye Control
The mouse provides intuitive, direct control over eye behavior:

#### Left Click - Eye Tracking
- **Function**: Make eyes look toward the clicked position
- **Behavior**: Eyes smoothly move to track the mouse cursor location
- **Area**: Clicks anywhere within the window are converted to appropriate eye positions
- **Precision**: Mouse position is automatically scaled to match eye movement range

#### Right Click - Blink Trigger  
- **Function**: Trigger an immediate blink animation
- **Behavior**: Both eyes close and open quickly
- **Timing**: Same duration as keyboard spacebar blink
- **Cooldown**: No cooldown period, can be triggered repeatedly

### Mouse Coordinate Mapping
The mouse input system automatically handles:
- **Window scaling**: Mouse coordinates are scaled to match eye display area
- **Aspect ratio**: Maintains proper proportions regardless of window size
- **Boundary detection**: Clicks outside the eye area are handled gracefully
- **Multi-monitor**: Works correctly on multi-monitor setups

## Help System

### Accessing Help
- **Activation**: Press **H** or **F1** to toggle help display
- **Display**: Semi-transparent overlay showing all controls
- **Toggle**: Press the same key again to hide help
- **Persistence**: Help state is remembered during the session

### Help Content
The help overlay displays:
- All keyboard shortcuts organized by category
- Mouse control descriptions
- Current application state (fullscreen, auto-modes, etc.)
- Version information

## Advanced Features

### Input Combination Effects
Some controls work better in combination:

- **Mood + Animation**: Try HAPPY mood with LAUGH animation
- **Position + Curious**: Curious mode is most visible when looking left/right
- **Manual State + Disabled Auto**: Disable auto-blinker before using O/X keys

### Timing Considerations
- **Animation Duration**: Most animations last 500ms
- **Auto-blinker Interval**: Default 3±2 seconds (configurable)
- **Idle Movement**: Default 2±2 seconds (configurable)
- **Input Responsiveness**: All inputs are processed at 60+ FPS

## Customization and Extension

### For Developers
The input system is designed to be extensible:

#### Adding Custom Key Mappings
```python
import pygame
from src.desktop.input_manager import InputManager

# Add custom key mapping
robo.input_manager.add_key_mapping(
    pygame.K_m,  # M key
    lambda r: r.set_mood(HAPPY)  # Action function
)
```

#### Adding Custom Mouse Mappings
```python
# Add middle mouse button support
robo.input_manager.add_mouse_mapping(
    "middle_click",
    lambda r, pos: r.confuse()  # Action with position parameter
)
```

#### Removing Default Mappings
```python
# Remove default mapping
robo.input_manager.remove_key_mapping(pygame.K_1)
```

#### Accessing Current Mappings
```python
# Get all current key mappings
key_mappings = robo.input_manager.get_key_mappings()

# Get all mouse mappings  
mouse_mappings = robo.input_manager.get_mouse_mappings()
```

### Configuration Options
Input behavior can be configured through the configuration system:

```python
from src.desktop.config import RoboEyesConfig

config = RoboEyesConfig(
    # Input-related settings
    debug=True,  # Enable input debugging
    # Window settings affect mouse coordinate mapping
    window_width=1024,
    window_height=768
)
```

## Troubleshooting Input Issues

### Keyboard Not Responding
1. **Window Focus**: Ensure the RoboEyes window has focus (click on it)
2. **Caps Lock**: Ensure Caps Lock is off
3. **Keyboard Layout**: US layout recommended for best compatibility
4. **Conflicting Software**: Disable gaming software that captures input

### Mouse Not Working
1. **Click Area**: Ensure you're clicking within the window bounds
2. **Window Focus**: Click on the window first to give it focus
3. **Mouse Sensitivity**: All mouse positions are automatically scaled
4. **Multiple Monitors**: Try clicking on the primary monitor

### Help Not Showing
1. **Key Press**: Try both H and F1 keys
2. **Window Focus**: Ensure window has focus before pressing help key
3. **Toggle State**: Help toggles on/off, press again if already visible
4. **Graphics Issues**: Check if overlay is rendered but not visible

### Performance Impact
Input processing is optimized for minimal performance impact:
- **Event Processing**: Only processes events when they occur
- **No Polling**: Uses event-driven input, not continuous polling
- **Efficient Mapping**: Hash-based key mapping for O(1) lookup
- **Error Handling**: Graceful handling prevents crashes from invalid input

## Implementation Details

### Input Manager Architecture
The input system is implemented in `src/desktop/input_manager.py`:

- **Event Processing**: Handles Pygame events in real-time
- **Mapping System**: Flexible key and mouse mapping with lambda functions
- **Help Rendering**: Overlay system for displaying control information
- **Error Handling**: Comprehensive exception handling for robustness
- **Coordinate Conversion**: Automatic scaling for mouse position mapping

### Integration Points
The input system integrates with:
- **RoboEyes Core**: Direct method calls for eye control
- **Window Management**: Fullscreen and window state changes
- **Configuration**: Settings for input behavior and debugging
- **Performance Monitor**: Input event tracking for performance analysis

This comprehensive input system provides both ease of use for end users and extensive customization options for developers, making RoboEyes Desktop both accessible and extensible.