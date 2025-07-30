# RoboEyes Desktop

**Emotion-driven animated robot eyes for TTS and AI assistant integration**

RoboEyes Desktop provides emotion-driven animated robot eyes perfect for healthcare applications, TTS systems, and AI assistants. The streamlined EmotionAnimationManager makes it easy for teams to integrate real-time emotion animations that respond to user interactions and coordinate seamlessly with text-to-speech playback.

![Credit: RoboEyes for Arduino by [FluxGarage.com](https://www.fluxgarage.com/index.php)](docs/_static/roboeyes-01.jpg)

## Key Features for Team Integration

- **EmotionAnimationManager** - Primary interface for emotion-driven animations
- **Real-time emotion chaining** - Seamless transitions during TTS playback
- **5 core emotions** - Happy, Neutral, Urgent, Concerned, Request
- **TTS coordination** - Perfect timing with speech synthesis systems
- **Error-safe design** - Never breaks animation continuity
- **Simple API** - Easy integration with existing applications
- **Healthcare-focused** - Designed for empathetic patient interactions

![Credit: RoboEyes moods by [FluxGarage.com](https://www.fluxgarage.com/index.php)](docs/_static/roboeyes-00.jpg)

## Quick Start for Teams

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/roboeyes/roboeyes-desktop.git
   cd roboeyes-desktop
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the team integration example:**
   ```bash
   python examples/simple_emotion_integration.py
   ```

4. **Try the TTS coordination demo:**
   ```bash
   python examples/team_integration_guide.py
   ```

5. **See real-time emotion chaining:**
   ```bash
   python examples/realtime_emotion_chaining_demo.py
   ```

### Basic EmotionAnimationManager Usage

```python
from src.roboeyes.desktop_roboeyes import DesktopRoboEyes
from src.roboeyes.emotion_animation_streamlined import (
    EmotionAnimationManager, 
    EMOTION_HAPPY, EMOTION_NEUTRAL, EMOTION_REQUEST
)
from src.desktop.config import RoboEyesConfig

# Initialize RoboEyes
config = RoboEyesConfig(window_width=800, window_height=600, frame_rate=30)
roboeyes = DesktopRoboEyes(config)

# Initialize emotion system (primary interface)
emotion_manager = EmotionAnimationManager(roboeyes)

# Trigger emotions for TTS coordination
emotion_manager.trigger_emotion(EMOTION_HAPPY)    # Greeting
emotion_manager.trigger_emotion(EMOTION_REQUEST)  # Asking question
emotion_manager.trigger_emotion(EMOTION_NEUTRAL)  # Return to idle

# CRITICAL: Call update() every frame in your main loop
while roboeyes.running:
    emotion_manager.update()  # Enables smooth transitions
    roboeyes.update()         # Updates animations
    roboeyes.clock.tick(30)   # Control frame rate
```

## Core Emotions for Team Integration

The EmotionAnimationManager provides 5 essential emotions designed for healthcare and TTS applications:

### Available Emotions

- **EMOTION_NEUTRAL** - Default calm state, ideal for idle/waiting
- **EMOTION_HAPPY** - Positive interactions, greetings, good news
- **EMOTION_REQUEST** - Asking questions, active listening mode
- **EMOTION_CONCERNED** - Showing empathy, acknowledging problems
- **EMOTION_URGENT** - Important information, alerts, attention needed

### TTS Integration Example

```python
# Coordinate emotions with speech timing
emotion_manager.trigger_emotion(EMOTION_HAPPY)
tts_engine.speak("Hello! Welcome to our healthcare system.")

emotion_manager.trigger_emotion(EMOTION_REQUEST)  
tts_engine.speak("How can I help you today?")

emotion_manager.trigger_emotion(EMOTION_CONCERNED)
tts_engine.speak("I understand your concern. Let me help.")

emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
# Return to neutral after interaction
```

## Team Integration Examples

The `examples/` directory contains focused examples for team integration:

- **`simple_emotion_integration.py`** - Basic emotion integration template
- **`team_integration_guide.py`** - Complete TTS coordination example
- **`realtime_emotion_chaining_demo.py`** - Real-time emotion transitions

### Key Integration Patterns

```python
# 1. Initialize emotion system
emotion_manager = EmotionAnimationManager(roboeyes_instance)

# 2. Get available emotions
available = emotion_manager.get_available_emotions()
# Returns: ['happy', 'neutral', 'urgent', 'concerned', 'request']

# 3. Trigger emotions safely
success = emotion_manager.trigger_emotion('happy')
if not success:
    # Fallback handling - animation continues smoothly
    emotion_manager.trigger_emotion('neutral')

# 4. Check current state
current = emotion_manager.get_current_emotion()
is_active = emotion_manager.is_emotion_active('happy')

# 5. CRITICAL: Update every frame for smooth transitions
while running:
    emotion_manager.update()  # Essential for real-time chaining
    roboeyes.update()
    clock.tick(30)
```

## Simple Configuration

EmotionAnimationManager uses simple dictionary-based configuration:

```python
# Use default emotions (recommended for most teams)
emotion_manager = EmotionAnimationManager(roboeyes_instance)

# Or customize emotions with dictionary configuration
from src.roboeyes.emotion_animation_streamlined import EmotionConfig

custom_emotions = {
    'happy': EmotionConfig(sequence_name='gentle_joy', duration_ms=4000),
    'neutral': EmotionConfig(sequence_name='idle_gentle', duration_ms=None),
    'urgent': EmotionConfig(sequence_name='alert_focused', duration_ms=None)
}

emotion_manager = EmotionAnimationManager(roboeyes_instance, custom_emotions)
```

### RoboEyes Configuration

```python
from src.desktop.config import RoboEyesConfig

# Recommended settings for team integration
config = RoboEyesConfig(
    display_width=128,
    display_height=64,
    window_width=800,
    window_height=600,
    frame_rate=30,        # 30 FPS for smooth emotion transitions
    auto_blinker=True     # Maintain natural blinking
)
```

## System Requirements

- **Python 3.8+** - Required for desktop version
- **Pygame 2.5.0+** - Graphics and windowing library
- **Operating System** - Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Memory** - At least 100MB free RAM
- **Graphics** - OpenGL-compatible graphics card (recommended)

## Installation

### Quick Installation

```bash
# Clone the repository
git clone https://github.com/roboeyes/roboeyes-desktop.git
cd roboeyes-desktop

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src.roboeyes.desktop_roboeyes
```

### Platform-Specific Installation

For detailed platform-specific installation instructions, see [INSTALL.md](INSTALL.md).

## EmotionAnimationManager API

### Core Methods

```python
from src.roboeyes.emotion_animation_streamlined import EmotionAnimationManager

# Initialize with RoboEyes instance
emotion_manager = EmotionAnimationManager(roboeyes_instance)
```

#### Primary Interface Methods

```python
# Trigger emotion animation (primary API)
success = emotion_manager.trigger_emotion('happy')
# Returns: True if successful, False otherwise

# Update animation state (call every frame)
emotion_manager.update()
# Essential for smooth transitions and timing

# Get available emotions
emotions = emotion_manager.get_available_emotions()
# Returns: ['happy', 'neutral', 'urgent', 'concerned', 'request']

# Check current emotion state
current = emotion_manager.get_current_emotion()
# Returns: Current emotion name or None

is_active = emotion_manager.is_emotion_active('happy')
# Returns: True if specified emotion is active
```

### Error Handling

The EmotionAnimationManager is designed to never break your application:

```python
# Invalid emotions fallback to neutral automatically
emotion_manager.trigger_emotion('invalid_emotion')  # Returns False, uses neutral

# Exceptions are caught and logged, animation continues
try:
    emotion_manager.trigger_emotion('happy')
except Exception:
    pass  # Won't happen - errors are handled internally

# Always safe to call in main loop
while running:
    emotion_manager.update()  # Never throws exceptions
    roboeyes.update()
```

### Integration with TTS Systems

```python
# Coordinate emotions with TTS timing
def speak_with_emotion(text, emotion):
    emotion_manager.trigger_emotion(emotion)
    your_tts_engine.speak(text)
    # Emotion transitions happen automatically via update() calls

# Example healthcare interaction
speak_with_emotion("Hello! How can I help you?", EMOTION_HAPPY)
speak_with_emotion("I understand your concern.", EMOTION_CONCERNED)
speak_with_emotion("This is important information.", EMOTION_URGENT)
```

## Troubleshooting Team Integration

### Common Integration Issues

**EmotionAnimationManager not responding:**
- Ensure `emotion_manager.update()` is called every frame in your main loop
- Check that RoboEyes instance is properly initialized
- Verify emotion names match the available emotions exactly

**Emotions not transitioning smoothly:**
- Confirm `update()` is called at consistent intervals (30 FPS recommended)
- Check that your main loop isn't blocked by long-running operations
- Ensure TTS timing doesn't interfere with animation updates

**TTS and emotion coordination issues:**
- Use the TTSEmotionCoordinator from `team_integration_guide.py`
- Don't trigger emotions faster than the animation system can process
- Allow emotions to complete their transitions before triggering new ones

### Error Handling Best Practices

```python
# Always handle emotion triggering safely
try:
    success = emotion_manager.trigger_emotion('happy')
    if not success:
        # Fallback to neutral - animation continues smoothly
        emotion_manager.trigger_emotion('neutral')
except Exception as e:
    # Log error but don't break animation loop
    logger.error(f"Emotion error: {e}")
    # System continues running normally
```

### Performance Optimization

- **Frame Rate**: Use 30 FPS for smooth emotions without excessive CPU usage
- **Update Frequency**: Call `emotion_manager.update()` every frame, not faster
- **TTS Coordination**: Don't trigger emotions more than once per second
- **Error Recovery**: Let the system handle errors automatically

## Healthcare and TTS Integration

RoboEyes Desktop is optimized for healthcare applications and TTS systems:

### Healthcare Interaction Patterns

```python
# Greeting sequence
emotion_manager.trigger_emotion(EMOTION_HAPPY)
tts.speak("Hello! Welcome to our healthcare system.")

# Information gathering
emotion_manager.trigger_emotion(EMOTION_REQUEST)
tts.speak("Could you tell me about your symptoms?")

# Showing empathy
emotion_manager.trigger_emotion(EMOTION_CONCERNED)
tts.speak("I understand this must be concerning for you.")

# Urgent information
emotion_manager.trigger_emotion(EMOTION_URGENT)
tts.speak("This is important information about your medication.")

# Return to neutral
emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
```

### Real-time Emotion Chaining

Perfect for coordinating with TTS playback timing:

```python
# Emotions chain seamlessly during speech
emotion_manager.trigger_emotion(EMOTION_HAPPY)    # Start positive
# TTS: "Hello! I'm here to help..."
emotion_manager.trigger_emotion(EMOTION_REQUEST)  # Transition to listening
# TTS: "How can I assist you today?"
emotion_manager.trigger_emotion(EMOTION_NEUTRAL)  # Return to idle

# The update() method handles smooth transitions automatically
while running:
    emotion_manager.update()  # Enables seamless chaining
    roboeyes.update()
    clock.tick(30)
```

## Documentation for Teams

Essential documentation for team integration:

- **[Installation Guide](INSTALL.md)** - Platform-specific installation instructions
- **[Team Integration Guide](docs/team_integration_guide.md)** - Complete TTS integration patterns
- **[EmotionAnimationManager API](docs/emotion_api_documentation.md)** - Core API reference
- **[Healthcare Examples](examples/)** - Real-world integration examples
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common integration issues

### Quick Reference

```python
# Essential imports
from src.roboeyes.emotion_animation_streamlined import (
    EmotionAnimationManager,
    EMOTION_HAPPY, EMOTION_NEUTRAL, EMOTION_URGENT, 
    EMOTION_CONCERNED, EMOTION_REQUEST
)

# Core pattern for all team integrations
emotion_manager = EmotionAnimationManager(roboeyes_instance)
while running:
    emotion_manager.update()  # CRITICAL: Call every frame
    roboeyes.update()
    clock.tick(30)
```

## Contributing

We welcome contributions! Please see our contributing guidelines and feel free to:

- Report bugs and request features
- Submit pull requests for improvements
- Add new eye moods or animations
- Improve documentation
- Create new examples

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Acknowledgments

- Original RoboEyes concept by [FluxGarage](https://www.fluxgarage.com/)
- MicroPython port inspiration and foundation
- Pygame community for excellent graphics library
- All contributors and users of the project