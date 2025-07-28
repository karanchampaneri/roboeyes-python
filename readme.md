# RoboEyes Desktop

**Animated robot eyes for desktop applications and AI assistants**

RoboEyes Desktop provides charming animated robot eyes perfect for AI assistants, chatbots, and interactive desktop applications. Originally inspired by the [RoboEyes video from FluxGarage](https://www.youtube.com/playlist?list=PLD2oXF44y-hLKjw_es2Vw1ycwBRNZ6ceE), this desktop implementation is optimized for integration with local LLMs like Ollama.

![Credit: RoboEyes for Arduino by [FluxGarage.com](https://www.fluxgarage.com/index.php)](docs/_static/roboeyes-01.jpg)

## Features

- **AI Assistant Integration** - Perfect for local LLMs like Ollama
- **Cross-platform desktop support** - Windows, macOS, and Linux
- **Interactive controls** - Keyboard and mouse input for real-time interaction
- **Multiple eye moods** - DEFAULT, TIRED, ANGRY, HAPPY, FROZEN, SCARY, CURIOUS
- **Smooth animations** - Blinking, winking, laughing, and position changes
- **Configurable appearance** - Eye shapes, sizes, colors, and behaviors
- **Performance optimized** - Efficient rendering with dirty rectangle updates
- **Extensible API** - Easy to integrate into chatbots and AI applications

![Credit: RoboEyes moods by [FluxGarage.com](https://www.fluxgarage.com/index.php)](docs/_static/roboeyes-00.jpg)

## Quick Start

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

3. **Run the basic example:**
   ```bash
   python examples/desktop_basic.py
   ```

4. **Try the interactive demo:**
   ```bash
   python examples/desktop_interactive.py
   ```

5. **Test Ollama integration (requires Ollama running):**
   ```bash
   pip install requests
   python examples/ollama_integration_example.py
   ```

### Basic Usage

```python
from src.roboeyes.desktop_roboeyes import DesktopRoboEyes, ON
from src.desktop.config import RoboEyesConfig

# Create configuration
config = RoboEyesConfig(
    window_width=800,
    window_height=600,
    frame_rate=60
)

# Initialize RoboEyes
robo = DesktopRoboEyes(config=config)

# Enable automatic behaviors
robo.set_auto_blinker(ON, 3, 2)  # Auto-blink every 3±2 seconds
robo.set_idle_mode(ON, 2, 2)     # Auto-move every 2±2 seconds

# Run the application
robo.run()
```

## Interactive Controls

### Keyboard Controls
- **1-7**: Change moods (Default, Tired, Angry, Happy, Frozen, Scary, Curious)
- **Arrow Keys**: Move eyes in 4 directions
- **WASD**: Alternative movement controls
- **Space**: Blink both eyes
- **Q/E**: Wink left/right eye
- **C**: Confuse animation
- **L**: Laugh animation
- **B**: Toggle auto-blinker
- **I**: Toggle idle mode
- **H/F1**: Show/hide help
- **F11**: Toggle fullscreen
- **ESC**: Exit fullscreen

### Mouse Controls
- **Left Click**: Make eyes look at clicked position
- **Right Click**: Trigger blink animation

## Examples

The `examples/` directory contains several demonstration applications:

- **`desktop_basic.py`** - Simple setup with automated behaviors
- **`desktop_interactive.py`** - Full interactive demo with all controls
- **`desktop_animation_sequence.py`** - Demonstrates animation sequences
- **`desktop_config_demo.py`** - Shows different eye configurations

## Configuration

RoboEyes Desktop supports both configuration files and command-line arguments:

```bash
# Use custom window size
python -m src.roboeyes.desktop_roboeyes --window-width 1024 --window-height 768

# Enable fullscreen mode
python -m src.roboeyes.desktop_roboeyes --fullscreen

# Save current settings
python -m src.roboeyes.desktop_roboeyes --save-config
```

Configuration files are automatically created in platform-appropriate locations:
- **Windows**: `%APPDATA%\RoboEyes\roboeyes_config.json`
- **macOS**: `~/Library/Application Support/RoboEyes/roboeyes_config.json`
- **Linux**: `~/.config/roboeyes/roboeyes_config.json`

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

## API Documentation

### Core Classes

#### DesktopRoboEyes
The main class for desktop RoboEyes applications.

```python
from src.roboeyes.desktop_roboeyes import DesktopRoboEyes
from src.desktop.config import RoboEyesConfig

# Create with configuration
config = RoboEyesConfig(window_width=800, window_height=600)
robo = DesktopRoboEyes(config=config)

# Or create with direct parameters
robo = DesktopRoboEyes(
    width=128, height=64,
    window_width=800, window_height=600,
    frame_rate=60
)
```

#### Key Methods

```python
# Animation control
robo.set_auto_blinker(ON, interval=3, variation=2)
robo.set_idle_mode(ON, interval=2, variation=2)

# Eye appearance
robo.eyes_width(left=36, right=36)
robo.eyes_height(left=36, right=36)
robo.eyes_radius(left=8, right=8)
robo.eyes_spacing(10)

# Mood and position
robo.mood = HAPPY
robo.position = NE
robo.cyclops = True

# Manual animations
robo.blink()
robo.wink(left=True)
robo.laugh()
robo.confuse()

# Window management
robo.toggle_fullscreen()
robo.set_window_size(1024, 768)
```

#### Configuration

```python
from src.desktop.config import RoboEyesConfig, ConfigManager

# Create configuration
config = RoboEyesConfig(
    window_width=800,
    window_height=600,
    display_width=128,
    display_height=64,
    frame_rate=60,
    auto_blinker=True,
    idle_mode=True
)

# Load/save configuration
manager = ConfigManager()
config = manager.load_config("my_config.json")
manager.save_config(config, "my_config.json")
```

### Animation Sequences

Create complex animation sequences with precise timing:

```python
# Create a sequence
seq = robo.sequences.add("demo")
seq.step(1000, lambda r: r.open())
seq.step(2000, lambda r: r.set_mood(HAPPY))
seq.step(3000, lambda r: r.laugh())
seq.step(4000, lambda r: r.set_mood(DEFAULT))

# Start the sequence
seq.start()
```

### Input Handling

Extend the input system with custom controls:

```python
# Add custom key mapping
robo.input_manager.add_key_mapping(
    pygame.K_m, 
    lambda r: r.set_mood(HAPPY)
)

# Add custom mouse mapping
robo.input_manager.add_mouse_mapping(
    "middle_click",
    lambda r, pos: r.confuse()
)
```

## Troubleshooting

### Common Issues

**Application won't start:**
- Ensure Python 3.8+ is installed
- Install Pygame: `pip install pygame`
- Check graphics drivers are up to date

**Poor performance:**
- Lower frame rate: `--frame-rate 30`
- Reduce window size: `--window-width 640 --window-height 480`
- Close other graphics-intensive applications

**Display issues:**
- Try different scaling: `--scale-factor 2.0`
- Toggle fullscreen: Press F11
- Check display resolution compatibility

**Input not working:**
- Ensure window has focus
- Check keyboard layout (US layout recommended)
- Try mouse controls if keyboard fails

### Platform-Specific Issues

**Windows:**
- Install Visual C++ Redistributable if Pygame fails to install
- Add Windows Defender exception if needed
- Run as Administrator if permission errors occur

**macOS:**
- Install Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew Python: `brew install python`
- Grant accessibility permissions if input fails

**Linux:**
- Install development packages: `sudo apt install python3-dev libsdl2-dev`
- Add user to audio/video groups for hardware access
- Try X11 if Wayland has issues: `export GDK_BACKEND=x11`

### Getting Help

- **Documentation**: Check the `docs/` directory for detailed guides
- **Examples**: Run examples in the `examples/` directory
- **Logs**: Check platform-specific log locations for error details
- **Issues**: Report bugs on the project's issue tracker

## AI Integration Examples

RoboEyes Desktop is designed to work seamlessly with AI assistants and chatbots:

### Ollama Integration
Perfect for adding visual feedback to local LLM interactions:

```python
from examples.ollama_integration_example import OllamaRoboEyes

# Create AI assistant with visual feedback
assistant = OllamaRoboEyes(model="llama2")
assistant.run_chat()  # Interactive chat with eye animations
```

**Visual States:**
- **Idle**: Default mood with gentle blinking
- **Thinking**: Curious mood with eye movement during processing
- **Responding**: Happy mood while generating response
- **Error**: Angry mood with confusion animation for errors

### Custom AI Integration
Easy to integrate with any Python-based AI system:

```python
# Basic integration pattern
robo.mood = CURIOUS      # AI is thinking
robo.mood = HAPPY        # AI is responding
robo.mood = DEFAULT      # AI is idle
robo.confuse()          # Show confusion for errors
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Installation Guide](INSTALL.md)** - Platform-specific installation instructions
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference for developers and AI integration
- **[Input Controls](docs/INPUT_CONTROLS.md)** - Detailed keyboard and mouse controls
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Solutions for common issues
- **[Performance Optimization](docs/PERFORMANCE_OPTIMIZATION.md)** - Performance tuning guide

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